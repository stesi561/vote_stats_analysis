#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import csv
import sys
import psycopg2

import re

import codecs
import StringIO
import UnicodeReader

directory = '../data/party'


outputfilename = "../data/combined_%d.csv"
# Output file columns:
# Election, Electorate Code, Electorate


dbname = 'votingstatistics'
user='python'
host='localhost'

DATA_FINISHED = "Votes Allowed for Party Only"
FIRST_SPECIAL = "Polling places where less than 6 votes were taken"




def connect_to_db():
    conn_string = "host='%s' dbname='%s' user='%s' " % (host,dbname,user)

    conn = psycopg2.connect(conn_string)
    curr = conn.cursor()
    curr.execute("SET CLIENT_ENCODING TO 'utf-8';")
    return (conn, curr)
    
        
def close_db(curr, conn, commit=True):
    if curr is not None:
        curr.close()
    if conn is not None:
        if commit:
            conn.commit()
        conn.close()


def get_file_list():
    """Returns list of files in the data directory"""
    files = []
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            if filename[-4:] != ".csv":
                continue
            tmp1, tmp2, election_year, tmp = filename.split('_')
            if election_year not in ('2011','2014'):
                continue
            files.append("%s/%s" % (root, filename))
    return files            


def import_files(filelist, lookup_by_party_name, lookup_by_booth_address):
    """Join booth Data from all files in the data directory into one
    csv file."""
    
    # columns all ordered the same as given by result of
    # create_party_list.
    # Booth id prepended to rows.

    parties = lookup_by_party_name.keys()
    parties.sort()
    matched = 0
    unmatched = 0

    for filename in filelist:
        with open(filename,'r') as inputfile:
            election_year = filename.split('/')[-1].split('_')[2]

            # Save the column in lookup_by_party_name we are going to be using
            party_index_col = 0
            if election_year == "2014":
                party_index_col = 1
            elif election_year == "2011":
                party_index_col = 2
            else:
                print "!!!!!!!!ERROR!!!!!!!"
                print "Expected a file with election year of 2014 or 2011 in filename as per format"
                sys.exit(0)

            lines = []

            inputfilereader = UnicodeReader.UnicodeReader(inputfile,
                                                          delimiter=',',
                                                          quotechar='"');     
            # Drop first line

            next(inputfilereader)
            
            # First col: Electorate Name SPACE Electorate Code
            electorate_code, electorate_name = next(inputfilereader)[0].rsplit(' ',1)

            # Skip Party names we have needed info in lookup_by_party_name already
            next(inputfilereader)
            
            suburb = ""
            specials = False
            for row in inputfilereader:
                if row[1] == FIRST_SPECIAL:
                    specials = True
                    row[0] = "Other Vote"
                elif specials == True and row[1] == DATA_FINISHED:
                    break
                elif specials:
                    row[0] = "Other Vote"

                if specials:
                    if "-" in row[1]:
                        row[1] = row[1].split(" - ", 1)[0]
                    
                        

                if row[0] == "":
                    row[0] = suburb
                else:
                    suburb = row[0]
                    

                
                
                if row[1] in lookup_by_booth_address or specials:
                    # Record data

                    # Booth Id and Booth details in cols 0 and 1
                    line = []
                    if specials:
                        line = ['Special'] + row[:2]
                    else:
                        line = [lookup_by_booth_address[row[1]]] + row[:2]
                    
                    # Reshuffle cols so party data matches up
                    for party in parties:
                        line.append(row[lookup_by_party_name[party][party_index_col]])
                   
                    lines.append(line)
                    matched += 1
                else:
                    unmatched += 1
    print "Matched: %d\tUnmatched: %d" % (matched,unmatched)


def get_booth_lookup(conn,curr):
    
    # Create lookup on 2014 addresses
    qry_str = """SELECT voting_place_address,  voting_place_id from vs_booth"""
    curr.execute(qry_str)
    lookup = dict()
    for row in curr.fetchall():
        lookup[row[0]] =  row[1]

    # Add lookups for any booths that changed address from 2011 to 2014

    qry_str = "SELECT a.voting_place_id, b.voting_place_address from vs_booth as a inner join vs_booth2011 as b on a.voting_place_id = b.voting_place_id where a.voting_place_address != b.voting_place_address;"""

    curr.execute(qry_str)
    for row in curr.fetchall():
        lookup[row[0]] = row[1]

    return lookup
            

def create_party_lookup(curr):
    
    qry_str = "SELECT pname, pid, index2014,index2011 FROM vs_parties"
    curr.execute(qry_str)
    lookup_by_pname = dict()
    for row in curr.fetchall():
        lookup_by_pname[row[0]] = row[1:]
    return lookup_by_pname
        

            
def create_party_list(curr):    

    qry = "SELECT count(*) from vs_parties"
    curr.execute(qry)
    if curr.fetchone()[0] > 0:
        return create_party_lookup(curr)

    parties_lookup = dict()
    parties = set()

    files = get_file_list()
    for filename in files:            
        with open(filename,'r') as inputfile:
            inputfilereader = UnicodeReader.UnicodeReader(inputfile,
                                                          delimiter=',',
                                                          quotechar='"');     
            # Drop first two lines
            next(inputfilereader)
            next(inputfilereader)
            line = next(inputfilereader)
            # Remove directory then grap the year out of the filename
            election_year = filename.split('/')[-1].split('_')[2]
            if election_year not in parties_lookup:
                parties_lookup[election_year]= dict()

            for col_num, party in zip(range(len(line)), line):
                if party == "":
                    continue
                if party not in  parties_lookup[election_year]:
                    parties_lookup[election_year][party] = col_num
                    parties.add(party)
                elif parties_lookup[election_year][party] != col_num:
                    print "ERROR: Mismatch Party Index"
                    print filename
                    print "expected: %s in col %s" % ( party,parties_lookup[election_year][party])
                    print "found: %s in col %s" % party, col_num
                    
    parties = list(parties)
    party_ids = dict()
    ins_data = []
    for pid, party in zip(range(len(parties)),parties):
        party_ids[party] = pid
        index2014 = -1
        index2011 = -1
        if party in parties_lookup['2014']:
            index2014= parties_lookup['2014'][party]
        if party in parties_lookup['2011']:
            index2011= parties_lookup['2011'][party]

        ins_data.append((pid, party, index2014, index2011))


    ins_str = "INSERT into vs_parties(pid, pname, index2014, index2011) VALUES (%s,%s,%s,%s)"    
    curr.executemany(ins_str,ins_data)
    
    return create_party_lookup(curr)


def main():
    conn, curr = connect_to_db()
    lookup_by_party_name = create_party_list(curr)
    lookup_by_booth_address = get_booth_lookup(conn, curr)

    import_files(get_file_list(), lookup_by_party_name, lookup_by_booth_address)

    close_db(curr, conn)
                
if __name__ == "__main__":
    
    main()

