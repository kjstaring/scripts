from insertion_PostgreSQL import insert_PostgreSQL
from query_PostgreSQL import query_PostgreSQL
from compare_PostgreSQL import compare_PostgreSQL

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Timer: 
from timeit import default_timer as timer

def create_database():
    #1. Connect to database 
    conn = psycopg2.connect("user=postgres password=1234")
    cur = conn.cursor() 
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT) 

    #2. Create database
    name_database = "insertdb"
    cur.execute("SELECT datname FROM pg_database;")
    list_database = cur.fetchall()
    if (str(name_database), ) in list_database: 
        drop_database = "DROP DATABASE "+ name_database 
        cur.execute(drop_database)
        conn.commit() 
    create_database = "CREATE DATABASE "+ name_database 
    cur.execute(create_database)
    conn.commit()
    conn.close()

    #3. Create extensions
    conn = psycopg2.connect("dbname=insertdb user=postgres password=1234")
    cur = conn.cursor() # Open a cursor to perform database operations

    create_postgis = "CREATE EXTENSION IF NOT EXISTS postgis"
    cur.execute(create_postgis)
    conn.commit()

    create_sfcgal = "CREATE EXTENSION IF NOT EXISTS postgis_sfcgal"
    cur.execute(create_sfcgal)
    conn.commit()
    conn.close() 


def mainStorage(file_name, interval, schema_name, new_or_old, use_index):
    #1. Create database
    if new_or_old == 'new':
        create_database() 

    diff = 0 
    for i in range(interval):
        start = timer() 

        #1. Insert 
        insert_PostgreSQL(file_name, schema_name, new_or_old, use_index)
        insert_sentence = str(file_name + ' is stored in PostgreSQL')
        print(insert_sentence)
        #2. Query and reconstruct 
        query_PostgreSQL(file_name, schema_name)
        query_sentence = str(file_name + ' is queried from PostgreSQL')
        print(query_sentence)

        end = timer() 
        diff = diff + end - start
    
    print('Time interval: ' + str(diff/interval))

    #3. Compare 
    compare_PostgreSQL(file_name)
    compare_sentence = str(file_name + ' is compared')
    print(compare_sentence)

file_name = input('Enter file name: ')
interval = input('Enter interval number: ')
schema_name = input('Enter schema name: ')
new_or_old = input('Enter new or old database and schema: ')
interval_integer = int(interval)
use_index = input('Enter yes or no for using indexes: ')

mainStorage(file_name, interval_integer, schema_name, new_or_old, use_index)


