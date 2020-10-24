import json
import pymongo
from collections.abc import Iterable
from collections import OrderedDict
from pymongo import MongoClient
import sys
import os 
libdir = os.path.dirname(__file__)
root_folder= str(os.path.split(libdir)[0]) 
sys.path.append(root_folder)
from algorithms.replace_transform import from_index_to_vertex
from algorithms.replace_transform import transform_vertices
from algorithms.replace_transform import from_index_to_surface 

def store_in_MongoDB(file_name, new_old): 
    client = MongoClient('mongodb://localhost:27017')
    #client = pymongo.MongoClient("mongodb://karinstaring:8DPHijv8@cluster0-shard-00-00-ilon5.mongodb.net:27017,cluster0-shard-00-01-ilon5.mongodb.net:27017,cluster0-shard-00-02-ilon5.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority")

    if new_old == 'new':
        # drop database if exists  
        database_names = client.database_names()
        for name in database_names:
            if name == 'CityJSON':
                client.drop_database('CityJSON')

        # collection CityObjects, metadata and transform always 
        collection_CityObjects = client['CityJSON'].create_collection('CityObjects')
        collection_metadata = client['CityJSON'].create_collection('metadata') 
        collection_transform = client['CityJSON'].create_collection('transform')
    else:
        # collection CityObjects, metadata and transform always 
        collection_CityObjects = client['CityJSON']['CityObjects']
        collection_metadata = client['CityJSON']['metadata']
        collection_transform = client['CityJSON']['transform']

    stringName = str('/Users/karinstaring/GeomaticsThesis/datasets/old/' + file_name + '.json')
    
    # metadata validator 
    ms = open('CityJSON_schemas/metadata.schema.json')
    metadata_schema = json.load(ms)
    metadata_query = [('collMod', 'metadata'),('validator', metadata_schema),('validationLevel', 'strict')]
    metadata_query = OrderedDict(metadata_query)
    client['CityJSON'].command(metadata_query)

    # transform validator 
    ts = open('CityJSON_schemas/transform.schema.json')
    transform_schema = json.load(ts)
    transform_query = [('collMod', 'transform'),('validator', transform_schema),('validationLevel', 'strict'), ('validationAction', 'warn')]
    transform_query = OrderedDict(transform_query)
    client['CityJSON'].command(transform_query)
  
    with open(stringName, encoding='utf-8-sig') as CityJSON_file:
        data = json.load(CityJSON_file)
        metadata = {}
        metadata['_id'] = 'metadata_' + str(file_name)
        metadata['type'] = data['type']
        metadata['version'] = data['version']

        if 'metadata' in data.keys():
            if "presentLoDs" in  data['metadata'].keys():
                print('presentLoDs is removed from the metadata.')
                del data['metadata']['presentLoDs']
            for key in data['metadata']:
                metadata[key] = data['metadata'][key]
        metadata_id = collection_metadata.insert_one(metadata)

        vertices = data['vertices']

        if 'transform' in data.keys():
            print('transform is present')
            transform = data['transform']
            
            transform['_id'] = 'transform_' + str(file_name)
            transform['metadata_id'] = metadata_id.inserted_id

            # transform the vertices 
            print("Vertices are transformed before considering the cityobjects.")
            vertices = transform_vertices(transform, vertices)
            transform_id = collection_transform.insert_one(transform)

        for ID in data['CityObjects']:
            document = data['CityObjects'][ID]
            document['_id'] = ID
            document['metadata_id'] = metadata_id.inserted_id

            keys = document.keys()

            for geometry in document['geometry']:
                # replace index with vertex        
                boundaries = geometry['boundaries']
                from_index_to_vertex(boundaries, vertices)

            # delete certain geometry types 
            index = 0 
            for geometry in document['geometry']: 
                if geometry['type'] != 'MultiSurface':
                    del document['geometry'][index]
                    index = index + 1 
                else:
                    index = index + 1 

            cityobject_id = collection_CityObjects.insert_one(document)
            
