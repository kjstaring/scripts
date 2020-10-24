# flask_graphene_mongo/schema.py
import graphene
import shapely2D 
from shapely.geometry import * 
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import AttributesModel, CityObjectsModel, MetadataModel, TransformModel, GeometryModel, SemanticsModel, Semantic_surfaceModel
from graphene import InputObjectType
from graphql import GraphQLError
import sys
import os 
libdir = os.path.dirname(__file__)
root_folder= str(os.path.split(libdir)[0]) 
sys.path.append(root_folder)
from algorithms.replace_transform import transform_boundaries 
from shapely.geometry import Point
import pyproj
from pyproj import Proj, transform

import re #to read integers from string 
from bson.objectid import ObjectId
class MetadataType(MongoengineObjectType):
    class Meta: #Graphene uses a Meta inner class on ObjectType to set different options.
        #camel_case defined here 
        model = MetadataModel 

class TransformType(MongoengineObjectType):
    class Meta:
        model = TransformModel 

class AttributesType(MongoengineObjectType):
    class Meta:
        model = AttributesModel 

class SemanticsType(MongoengineObjectType):
    
    class Meta:
        model = SemanticsModel

#AttributesModel does not have object attributes, but needs to be included 
class Semantic_surfaceType(MongoengineObjectType):
    class Meta:
        model = Semantic_surfaceModel 

class shapely(graphene.Interface):
    area = graphene.Float()
    bounds = graphene.List(graphene.Float) 
    length = graphene.Float()
    geom_type = graphene.String()
    distance = graphene.Float() 

class SurfaceType(graphene.ObjectType):
    surface = graphene.List(graphene.List(graphene.List(graphene.Float)))
    semanticsobject = graphene.Field(Semantic_surfaceType)

class GeometryType(MongoengineObjectType):
    boundarysurfaces = graphene.Field(SurfaceType)

    class Meta:
        #interfaces = (shapely, ) 
        model = GeometryModel

    def resolve_boundarysurfaces(self, info):
        for i, sur in enumerate(self.boundaries):
            value = self.semantics.values[i]
            seman = self.semantics.surfaces[value]
            return SurfaceType(surface = sur, semanticsobject = seman)
            

class CityObjectsType(MongoengineObjectType):

    children = graphene.List(lambda: CityObjectsType)
    count_children = graphene.Int() 
    parents = graphene.List(lambda: CityObjectsType)
    count_parents = graphene.Int() 

    class Meta: 
        model = CityObjectsModel

    def resolve_count_children(self, info):
        return len (self.children)
    
    def resolve_children(self, info):
        children = []
        for child_id in self.children:
            children.extend(list(CityObjectsModel.objects(_id=child_id)))
        return children
    

    def resolve_count_parents(self, info):
        return len (self.parents)

    def resolve_parents(self, info):
        parents = []
        for parent_id in self.parents:
            parents.extend(list(CityObjectsModel.objects(_id=parent_id)))
        return parents

class PositionInput(graphene.InputObjectType):
    lat = graphene.Float(required=True)
    long = graphene.Float(required=True)
    alt = graphene.Float(required=True)

class LocationType(graphene.ObjectType):
    latitude = graphene.Float()
    longitude = graphene.Float() 
    altitude = graphene.Float()

class locationQuery(graphene.ObjectType):
    location = graphene.Field(LocationType, position=PositionInput(required=True))
    
    def resolve_location(self, info, position):
        return LocationType(latitude=position.lat, longitude = position.long, altitude = position.alt)

#https://github.com/graphql-python/graphene/issues/431#issuecomment-284083925
   
class MetadataQuery(graphene.ObjectType):
    metadata = graphene.List(MetadataType)
    def resolve_metadata(self, info, **args):
        return MetadataModel.objects.all()

class TransformQuery(graphene.ObjectType):
    transform = graphene.List(TransformType)
    def resolve_transform(self, info, **args):
        return TransformModel.objects.all()

class CityobjectsQuery(graphene.ObjectType):
    cityobjects = graphene.List(CityObjectsType, Id=graphene.String())
    def resolve_cityobjects(self, info, **args):
        return CityObjectsModel.objects(_id = args['Id'])

class citymodelQuery(graphene.ObjectType):
    citymodel = graphene.List(MetadataType, position=PositionInput(required=True))
    def resolve_citymodel(self, info, position):
        obj_list = []

        metadatas = list(MetadataModel.objects.all())
        for metadata in metadatas:
            # referenceSystem of the citymodel 
            referenceSystem = metadata['referenceSystem']
            referenceSystem = int(re.search(r'\d+', referenceSystem).group())

            #to use shapely the coordinates have to be provided in meters 
            inProj = Proj(init='epsg:4326')
            crs = 'epsg:' + str(referenceSystem)
            outProj = Proj(init=crs)
            lat, long, alt= pyproj.transform(inProj,outProj, position.lat, position.long, position.alt) 
            point = Point(lat, long)

            geographicalExtent = metadata['geographicalExtent']
            geographicalExtent_polygon = Polygon([[geographicalExtent[0], geographicalExtent[1]], [geographicalExtent[0], geographicalExtent[4]], [geographicalExtent[3], geographicalExtent[4]], [geographicalExtent[3], geographicalExtent[1]]])

            result = point.intersects(geographicalExtent_polygon)
            if result == True:
                obj_list.append(metadata)

        return obj_list 

class radius100Query(graphene.ObjectType):
    radius100 = graphene.List(CityObjectsType, position=PositionInput(required=True))
    def resolve_radius100(self, info, position):
        obj_list = []
        metadatas = list(MetadataModel.objects.all())
        for metadata in metadatas:
            # id and referenceSystem of the citymodel 
            meta_id = metadata['_id']
            referenceSystem = metadata['referenceSystem']
            referenceSystem = int(re.search(r'\d+', referenceSystem).group())
            # cityobjects of the citymodel 
            objs = list(CityObjectsModel.objects(metadata_id=meta_id, type='Building'))

            #to use shapely the coordinates have to be provided in meters 
            inProj = Proj(init='epsg:4326')
            crs = 'epsg:' + str(referenceSystem)
            outProj = Proj(init=crs)
            lat, long, alt = pyproj.transform(inProj,outProj, position.lat, position.long, position.alt) 
            point = Point(lat, long)

            for obj in objs:
                for geom in obj['geometry']:
                    geom.distance = shapely2D.distance(point, geom['boundaries'])
                    if geom.distance < 100:
                        obj_list.append(obj)

        return obj_list 

class insideQuery(graphene.ObjectType):
    inside = graphene.List(CityObjectsType, position=PositionInput(required=True))
    def resolve_inside(self, info, position):

        obj_list = []
        metadatas = list(MetadataModel.objects.all())
        for metadata in metadatas:
            # id and referenceSystem of the citymodel 
            meta_id = metadata['_id']
            referenceSystem = metadata['referenceSystem']
            referenceSystem = int(re.search(r'\d+', referenceSystem).group())
            
            # cityobjects of the citymodel 
            objs = list(CityObjectsModel.objects(metadata_id=meta_id, type='Building'))

            #to use shapely the coordinates have to be provided in meters 
            inProj = Proj(init='epsg:4326')
            crs = 'epsg:' + str(referenceSystem)
            outProj = Proj(init=crs)
            lat, long, alt = pyproj.transform(inProj,outProj, position.lat, position.long, position.alt) 
            point = Point(lat, long)

            for obj in objs:
                for geom in obj['geometry']:
                    result = shapely2D.intersects(point, geom['boundaries'])
                    if result == True: 
                        obj_list.append(obj)
            
        return obj_list 

class MaxLoDQuery(graphene.ObjectType):
    maxlod = graphene.Field(GeometryType, Id=graphene.String(required=True))
    def resolve_maxlod(self, info, Id):
        obj = list(CityObjectsModel.objects(_id=Id))[0]
        maxlod_list = []
        for geom in obj['geometry']:
            maxlod_list.append(geom['lod'])

        for geom in obj['geometry']:
            if geom['lod'] == max(maxlod_list):
                return geom

class Query(CityobjectsQuery, MetadataQuery, TransformQuery, locationQuery, radius100Query, citymodelQuery, insideQuery, MaxLoDQuery):   
    pass 

schema = graphene.Schema(query=Query, auto_camelcase=False)
