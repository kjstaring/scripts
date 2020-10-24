from typing import Optional, List, Any, Union, Dict, TypeVar, Callable, Type, cast
from database import * 
from mongoengine import *
from bson.objectid import ObjectId

class Semantic_surfaceModel(DynamicEmbeddedDocument):
    _id = ObjectIdField( required=True, default=lambda: ObjectId() )
    type = StringField() 

class SemanticsModel(DynamicEmbeddedDocument):
    values = ListField(IntField())
    surfaces = ListField(EmbeddedDocumentField(Semantic_surfaceModel))

# GraphQL cannot execute a query without a type system 
class GeometryModel(DynamicEmbeddedDocument):
    _id = ObjectIdField(required=True, default=lambda: ObjectId() )
    type = StringField() 
    boundaries = ListField(ListField(ListField(ListField(FloatField()))))
    lod = IntField()
    semantics = EmbeddedDocumentField(SemanticsModel)

class AttributesModel(DynamicEmbeddedDocument):
    measuredHeight = FloatField() 
    TerrainHeight = FloatField() 
    bron_tex = StringField()
    voll_tex = StringField() 
    bron_geo = StringField()
    status = StringField() 

class MetadataModel(Document):
    _id = StringField(required=True)
    geographicalExtent = ListField(FloatField())
    referenceSystem = StringField()
    type = StringField()
    version = StringField() 
    meta = {'collection': 'metadata'}

#difficult to test address object 
class CityObjectsModel(Document):
    _id  = StringField(required=True) 
    type = StringField()
    geographicalExtent = ListField(FloatField())
    attributes = EmbeddedDocumentField(AttributesModel)
    geometry = ListField(EmbeddedDocumentField(GeometryModel)) 
    metadata_id = StringField() 
    children = ListField(StringField())
    parents = ListField(StringField())
    meta = {'collection':'CityObjects'}

class TransformModel(Document):
    translate = ListField(FloatField())
    scale = ListField(FloatField())
    metadata_id = StringField()
    meta = {'collection': 'transform'}




