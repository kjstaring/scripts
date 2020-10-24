import json 
# load the minimum cityjson schema from cityjson.org 
ms = open('CityJSON_schemas/cityjson.min.schema.json', 'r')
cityjson_schema = json.load(ms) 

# $schema is not allowed in MongoDB 
del cityjson_schema['$schema']

# title is allowed in MongoDB
cityjson_schema['title']

def replace_integer(schema_object):
    for key in schema_object.keys():
        value = schema_object[key]
        if not isinstance(value, dict): 
            # oneOf contains one list with a dictionary in it 
            if key == 'oneOf':
                schema_object[key] = [replace_integer(value[0])]
            elif key == 'type': 
                # according to del and adding a new key, the dictionary does not change its size during iteration 
                del schema_object[key]
                key = 'bsonType'
                if value == 'integer': 
                    # type: integer becomes bsonType: int 
                    schema_object[key] = 'int'
                else: 
                    schema_object[key] = value 
        else: 
            schema_object[key] = replace_integer(value)
    return schema_object 

def remove_formatKeys(schema_object):
    # the schema becomes a list to change the size of the dictionary during iteration 
    for key in list(schema_object):
        value = schema_object[key]
        if not isinstance(value, dict): 
            if key == 'format':
                del schema_object[key]
            elif key == 'oneOf':
                schema_object[key] = [remove_formatKeys(value[0])]
        else: 
            schema_object[key] = remove_formatKeys(value)
    return schema_object 

##### METADATA SCHEMA #####
# create a new metadata schema 
metadata_schema = {}
metadata_schema['$jsonSchema'] = {}
metadata_schema['$jsonSchema']['type'] = 'object'
# type added: no type and format 
type_keys = {'type': cityjson_schema['properties']['type']}
# version added: type and no format 
replaced_version = replace_integer(cityjson_schema['properties']['version']) 
version_keys = {'version': replaced_version}
#add metadata: type and format 
replaced_metadata = replace_integer(cityjson_schema['properties']['metadata']['properties']) 
removed_format = remove_formatKeys(replaced_metadata)
# update the dictionary 
type_keys.update(version_keys)
type_keys.update(removed_format)

# add metadata properties and requirements 
metadata_schema['$jsonSchema']['properties'] = type_keys 
metadata_schema['$jsonSchema']['required'] = ['type', 'version']

# store metadata 
metadata_schema_stringName = str('CityJSON_schemas/metadata.schema.json')
with open(metadata_schema_stringName, 'w') as output_file:
    json.dump(metadata_schema, output_file, sort_keys=True, indent=4, separators=(',', ': '))

##### TRANSFORM SCHEMA #####
transform_schema = {}
transform_schema['$jsonSchema'] = {}
transform_schema['$jsonSchema']['type'] = 'object'
replaced_transform = replace_integer(cityjson_schema['properties']['transform']['properties']) 
transform_schema['$jsonSchema']['properties'] = replaced_transform
transform_schema['$jsonSchema']['required'] = cityjson_schema['properties']['transform']['required']

transform_schema_stringName = str('CityJSON_schemas/transform.schema.json')
with open(transform_schema_stringName, 'w') as output_file:
    json.dump(transform_schema, output_file, sort_keys=True, indent=4, separators=(',', ': '))

