#! /usr/bin/env python3
import os
import csv
import sys

import re


directory = '../data/party'


output_filename = "../data/combined.csv"
# Output file columns:
# Election, Electorate Code, Electorate

DATA_FINISHED = "Votes Allowed for Party Only"
FIRST_SPECIAL = "Polling places where less than 6 votes were taken"

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


def import_files(filelist, output_filename):
    """Join booth Data from all files in the data directory into one massive
    csv file."""
    BOOTH = 'Booth'
    AREA = 'Area'
    cols = [AREA,BOOTH ,"Green Party","Labour Party","National Party","New Zealand First Party","Total Valid Party Votes","Informal Party Votes"]
    out_header = ['Election', 'Electorate'] + cols

    with open(output_filename,'w') as outputfile:  
        csvwriter = csv.writer(outputfile)
        csvwriter.writerow(out_header)
                
    for filename in filelist:
        with open(filename,'r') as inputfile, open(output_filename,'a') as outputfile:
            csvwriter = csv.writer(outputfile)
            
            election_year = filename.split('/')[-1].split('_')[2]

            next(inputfile) # Skip first row.                       
            # First col: Electorate Name SPACE Electorate Code
            electorate_name, electorate_code = next(inputfile).strip().replace('"','').replace("'","").split(',')[0].rsplit(' ',1)
            in_header = [col.strip() for col in next(inputfile).replace("'","").replace('"','').split(',')]
            in_header[0] = cols[0]
            in_header[1] = cols[1]            
            csvreader = csv.DictReader(inputfile, fieldnames= in_header)
            
            suburb = ""
            specials = False
            for row in csvreader:

                
                out_row = [row[x] for x in cols]
                                    
                
                if row[BOOTH] == FIRST_SPECIAL:
                    specials = True
                    out_row[cols.index(AREA)] = "Other Vote"                
                elif specials:
                    out_row[0] = "Other Vote"

                    
                #if specials:
                #    if "-" in row[BOOTH]:
                #        out_row[0] = row[BOOTH].split(" - ", 1)[0]
                    
                        
                        
                if out_row[0] == "":
                    out_row[0] = suburb
                else:
                    suburb = out_row[0]

                out_row = [election_year, electorate_name] + out_row
                csvwriter.writerow(out_row)                
                if row[BOOTH] == DATA_FINISHED:
                    break



def main():
    files = get_file_list()
    import_files(files, output_filename)
    
if __name__ == "__main__":
    main()

