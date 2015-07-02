drop table if exists vs_booth2014;
drop table if exists vs_booth2011;
drop table if exists vs_booth;
drop table if exists vs_parties;

create table vs_booth2014(
       electorate_number integer,
       electorate_name varchar,
       voting_place_id integer PRIMARY KEY,
       voting_place_suburb varchar,
       voting_place_address varchar,
       NZTM2000_Northing float,
       NZTM2000_Easting float,
       NZMG_Northing float,
       NZMG_Easting float,
       geom geometry(POINT, 2193));


create table vs_booth2011(
       electorate_number integer,
       electorate_name varchar,
       voting_place_id integer  PRIMARY KEY,
       voting_place_suburb varchar,
       voting_place_address varchar,
       NZTM2000_Northing float,
       NZTM2000_Easting float,       
       geom geometry(POINT, 2193));

create table vs_booth(
       electorate_number integer,
       electorate_name varchar,
       voting_place_id integer  PRIMARY KEY,
       voting_place_suburb varchar,
       voting_place_address varchar,
       NZTM2000_Northing float,
       NZTM2000_Easting float,       
       geom geometry(POINT, 2193));



create table vs_parties(
       pid integer PRIMARY KEY,
       pname VARCHAR,
       index2014 integer,
       index2011 integer);

\copy vs_booth2014( electorate_number, electorate_name, voting_place_id, voting_place_suburb, voting_place_address, NZTM2000_Northing, NZTM2000_Easting, NZMG_Northing, NZMG_Easting) from '/home/sstewart/greens/work/vote_stats/data/2014_Voting_Place_Co-ordinates.csv' CSV HEADER QUOTE '"'

\copy vs_booth2011( electorate_number, electorate_name, voting_place_id, voting_place_suburb, voting_place_address, NZTM2000_Northing, NZTM2000_Easting) from '/home/sstewart/greens/work/vote_stats/data/2011_Polling_Place_Co-ordinates.csv' CSV HEADER QUOTE '"'


UPDATE vs_booth2014 set geom = ST_SETSRID(ST_MakePoint(NZTM2000_Northing, NZTM2000_Easting), 2193);
UPDATE vs_booth2011 set geom = ST_SETSRID(ST_MakePoint(NZTM2000_Northing, NZTM2000_Easting), 2193);
CREATE INDEX idx_booth2014_geom on vs_booth2014 USING GIST(geom);
CREATE INDEX idx_booth2011_geom on vs_booth2011 USING GIST(geom);




INSERT INTO vs_booth SELECT electorate_number, electorate_name,voting_place_id, voting_place_suburb, voting_place_address,NZTM2000_Northing,NZTM2000_Easting, geom FROM vs_booth2014;



INSERT INTO 	  vs_booth 
       SELECT 	  electorate_number, electorate_name,voting_place_id, voting_place_suburb,voting_place_address,NZTM2000_Northing,NZTM2000_Easting, geom 
       FROM   	  vs_booth2011
       WHERE 	  voting_place_id not in (SELECT voting_place_id FROM vs_booth);


