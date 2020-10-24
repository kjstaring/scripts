# Karin_Staring_Geomatics_Thesis
Thesis research about the storage and querying of CityJSON in different databases using GraphQL

### macOS Mojave 

- Source install brew:  https://brew.sh/index_nl: 
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```
**Installation MongoDB via brew **: 
```
brew services stop mongodb
brew uninstall mongodb

brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Installation Python libraries via pip **: 
```
pip3 install pymongo
pip3 install cjio 
pip3 install flask 
pip3 install flask_graphql
pip3 install graphene
pip3 install shapely 
pip3 install scipy 
pip3 install matplotlib 
pip3 install graphene_mongo
pip3 install psycopg2
pip3 install SQLalchemy 
pip3 install geoalchemy2
```

**Installation PostgreSQL and the extension PostGIS with sfcgal**: 
```
brew uninstall postgresql
brew uninstall postgis
brew tap osgeo/osgeo4mac
brew install osgeo-postgresql
brew install osgeo-postgis
```

```
brew link osgeo-postgresql --force
initdb /usr/local/var/postgresql -E utf8 --locale=en_US.UTF-8
pg_ctl start -D /usr/local/var/postgresql
psql -h localhost -d postgres
```
```
create role postgres;
alter role postgres with superuser;
alter role postgres with createrole;
alter role postgres with createdb;
alter role postgres with replication;
alter role postgres with bypassrls;
alter role postgres with password '1234';
alter database postgres owner to postgres; 
alter role postgres with login; 
exit 
psql -U postgres

\du
\l
```

Download the pgadmin4-4.20.dmg file from 
https://www.postgresql.org/ftp/pgadmin/pgadmin4/v4.20/macos/ 
, install pgadmin, drag pgadmin to the applications folder and follow these instructions (must be adapted): 
https://dev.to/letsbsocial1/installing-pgadmin-only-after-installing-postgresql-with-homebrew-part-2-4k44

**Things to add**: 
val3dity 

**CityGML-tools**: 
download version 1.3.2: 
https://github.com/citygml4j/citygml-tools
JDK required used version: 8u221 macos 

**3D CityDB**:
- create database in PostgreSQL 
```
create extension postgis;
create extension postgis_sfcgal;
create extension postgis_raster; 
``` 
- install 3DCityDB-Importer-Exporter-4.2.0-Setup.jar from https://www.3dcitydb.org/3dcitydb/downloads/
JDK required used version: 8u221 macos 
```
cd /Applications/3DCityDB-Importer-Exporter/3dcitydb/postgresql/ShellScripts/Unix
``` 
alter the connection details 
3DCityDB-Importer-Exporter can be used to add two schema's to the database, namely citydb and citydb_pkg.
```
chmod u+x CREATE_DB.sh
./CREATE_DB.sh
```
The database is now able to make a connection with the graphical interface of 3DCityDB-Importer-Exporter. 
```
cd /Applications/3DCityDB-Importer-Exporter/bin 
chmod u+x 3DCityDB-Importer-Exporter
./3DCityDB-Importer-Exporter
```
alter the Database connection details and import the CityGML file. 

Multiple city models 3DCityDB:
```
chmod u+x CREATE_SCHEMA.sh
./CREATE_SCHEMA.sh
```
The schema obtained the reference system, that was assigned during the creation of the first schema. 
Therefore, the reference system of the schema had to be changed with the following \ac{SQL} query:  
```
select change_schema_srid(25833,'urn:ogc:def:crs:EPSG:25833', 0, 'citydb2')
```

performance testing
```
open /usr/local/bin/jmeter
```
