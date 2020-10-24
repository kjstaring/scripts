import pymongo
import json 
from pymongo import MongoClient
from bson.objectid import ObjectId
import pprint
from cjio.cityjson import CityJSON
import sys
import os 
libdir = os.path.dirname(__file__)
root_folder= str(os.path.split(libdir)[0]) 
sys.path.append(root_folder)
from algorithms.replace_transform import from_vertex_to_index
from algorithms.replace_transform import transform_vertices_back
from algorithms.replace_transform import from_surface_to_index
import gridfs
import ast 

def extract_in_MongoDB(file_name): 
    client = MongoClient('mongodb://localhost:27017/CityJSONObject')
    outputCityJSON = {}
    
    # metadata 
    collection_metadata = client['CityJSON']['metadata']
    
    for key in collection_metadata.find():
        key.pop('_id')
        outputCityJSON['type'] = key['type']
        key.pop('type')
        outputCityJSON['version'] = key['version']
        key.pop('version')
        outputCityJSON['metadata'] = key
    
    outputCityJSON['CityObjects'] = {}
    collection_names = client['CityJSON'].list_collection_names()

    # transform 
    if "transform" in collection_names:
        collection_transform = client['CityJSON']['transform']
        # for-loop needed to get access to the data 
        for key in collection_transform.find(): 
            key.pop('_id')
            key.pop('metadata_id')
            outputCityJSON['transform'] = key 
        
    # vertices 
    verticesList = []

    collection_CityObjects = client['CityJSON']['CityObjects']

    for ID in collection_CityObjects.find(no_cursor_timeout = True):
        keyID = ID['_id']
        ID.pop('_id')
        ID.pop('metadata_id')
        outputCityJSON['CityObjects'][keyID] = ID
           
        geometries = outputCityJSON['CityObjects'][keyID]['geometry']
        for geom in geometries: 
            geom['boundaries'] = from_vertex_to_index(geom['boundaries'], verticesList)

    if 'transform' in outputCityJSON.keys():
        verticesList = transform_vertices_back(outputCityJSON['transform'], verticesList)


    outputCityJSON['vertices'] = verticesList 

    # Remove the duplicate vertices with cjio 
    cityjson = CityJSON(j=outputCityJSON)
    cityjson.remove_duplicate_vertices()

    # Write CityJSON file 
    stringName = str('/Users/karinstaring/GeomaticsThesis/datasets/new/' + file_name + '.json')
    with open(stringName, 'w') as output_file:
        json.dump(cityjson.j, output_file)
        output_file.close()
