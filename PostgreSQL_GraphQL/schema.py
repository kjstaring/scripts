import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from models import metadataModel, transformModel, city_objectModel, geometriesModel, engine, semantic_surfaceModel, surfacesModel 
from sqlalchemy import func, Column, Integer, String, cast, Float, ARRAY, or_, and_
from sqlalchemy.orm import aliased
from geoalchemy2.types import Geography
from geoalchemy2.functions import GenericFunction

import json 
import re #to read integers from string 
from geoalchemy2.functions import GenericFunction

class ST_3DDWithin(GenericFunction):
    name = 'ST_3DDWithin'

class metadataType(SQLAlchemyObjectType):
    srs = graphene.Int()
    geographicalExtent = graphene.List(graphene.Float)

    class Meta:
        model = metadataModel

    def resolve_srs(self, info):
        srs = int(re.search(r'\d+', self.object['referenceSystem']).group())
        return srs

    def resolve_geographicalExtent(self, info):
        return self.geographicalExtent 


class transformType(SQLAlchemyObjectType):
    class Meta:
        model = transformModel

class geometriesType(SQLAlchemyObjectType):
    lod = graphene.Int()
    geomtype = graphene.String()

    class Meta:
        model = geometriesModel
    
    def resolve_lod(self, info):
        return self.object["lod"]

    def resolve_geomtype(self, info):
        return self.object["type"]


class city_objectType(SQLAlchemyObjectType):
    maxlod = graphene.Field(geometriesType)
    class Meta:
        model = city_objectModel
    def resolve_maxlod(self, info):
        maxlod = 0
        maxobject = None
        for geometry in self.geometries:
            if geometry.object['lod'] > maxlod:
                maxlod = geometry.object['lod']
                maxobject = geometry 
        return maxobject 

class semantic_surfaceType(SQLAlchemyObjectType):
    class Meta:
        model = semantic_surfaceModel

class surfacesType(SQLAlchemyObjectType):
    class Meta:
        model = surfacesModel
    def resolve_geometry(self, info, **args):
        if self.geometry != None:
            return engine.scalar(self.geometry.St_AsText())
        else:
            return None
    
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

# "Building" has been changed to "BuildingPart: for zürich."
class radius100indexQuery(graphene.ObjectType):
    radius100index = graphene.List(city_objectType, position=PositionInput(required=True))
    def resolve_radius100index(self, info, position):
        query_building = city_objectType.get_query(info)
        building = query_building.filter(func.ST_DWithin(func.ST_SetSRID(func.ST_MakePoint(position.lat, position.long, position.alt), 4979), city_objectModel.globalconvexhull, 100, False), city_objectModel.object['type'].astext == 'Building')
        return building

class radius100Query(graphene.ObjectType):
    radius100 = graphene.List(city_objectType, position=PositionInput(required=True)) 
    def resolve_radius100(self, info, position):
        query_building = city_objectType.get_query(info)
        buildings = query_building.filter(func.ST_DWithin(func.ST_SetSRID(func.ST_MakePoint(position.lat, position.long, position.alt), 4979), func.ST_Transform(city_objectModel.convexhull, 4979), 100, False), city_objectModel.object['type'].astext == 'Building')
        return buildings 
   
class insideindexQuery(graphene.ObjectType):
    insideindex = graphene.List(city_objectType, position=PositionInput(required=True)) 
    def resolve_insideindex(self, info, position):
        query_building = city_objectType.get_query(info)
        building = query_building.filter(func.ST_Intersects(func.ST_SetSRID(func.ST_MakePoint(position.lat, position.long, position.alt), 4979), city_objectModel.globalconvexhull), city_objectModel.object['type'].astext == 'Building')
        return building

class insideQuery(graphene.ObjectType):
    inside = graphene.List(city_objectType, position=PositionInput(required=True)) 
    def resolve_inside(self, info, position):
        query_building = city_objectType.get_query(info)
        buildings = query_building.filter(func.ST_Intersects(func.ST_SetSRID(func.ST_MakePoint(position.lat, position.long, position.alt), 4979), func.ST_Transform(city_objectModel.convexhull, 4979)), city_objectModel.object['type'].astext == 'Building')
        return buildings

class citymodelQuery(graphene.ObjectType):
    citymodel = graphene.List(metadataType, position=PositionInput(required=True))
    def resolve_citymodel(self, info, position):
        query_metadata = metadataType.get_query(info)
        p = metadataModel.object['geographicalExtent']
        query_metadata = query_metadata.filter(func.ST_Intersects(func.ST_SetSRID(func.ST_MakePoint(position.lat, position.long, position.alt), 4979), func.ST_Transform(func.ST_MakeEnvelope(p[0].cast(Float), p[1].cast(Float), p[3].cast(Float), p[4].cast(Float), cast(func.substr(metadataModel.object['referenceSystem'].astext, 23, 10), Integer)), 4979)))
        return query_metadata

class metadataQuery(graphene.ObjectType):
    metadata = graphene.List(metadataType, id = graphene.String()) 
    def resolve_metadata(self, info, **args):
        query = metadataType.get_query(info)
        if "id" in args:
            query = query.filter(metadataModel.id == args['id'])
        print(query)
        return query

class transformQuery(graphene.ObjectType):
    transform = graphene.List(transformType, id = graphene.String()) 
    def resolve_transform(self, info, **args):
        query = transformType.get_query(info)
        if "id" in args:
            query = query.filter(transformModel.id == args['id'])
        return query

class cityobjectsQuery(graphene.ObjectType):
    cityobjects = graphene.List(city_objectType, id = graphene.String(), objtype= graphene.String()) 
    def resolve_cityobjects(self, info, **args):
        query = city_objectType.get_query(info)
        if "id" in args and "objtype" in args:
            query = query.filter(city_objectModel.id == args['id'], city_objectModel.object['type'].astext == args['objtype'])
        elif "id" in args: 
            query = query.filter(city_objectModel.id == args['id'])
        elif "objtype" in args: 
            query = query.filter(city_objectModel.object['type'].astext == args['objtype'])
        
        return query

class geometriesQuery(graphene.ObjectType):
    geometries = graphene.List(geometriesType, id = graphene.String()) 
    def resolve_geometries(self, info, **args):
        query = geometriesType.get_query(info)
        if "id" in args:
            query = query.filter(geometriesModel.id == args['id'])
        return query

class semanticsurfaceQuery(graphene.ObjectType):
    semanticsurface = graphene.List(semantic_surfaceType, id = graphene.String()) 
    def resolve_semanticsurface(self, info, **args):
        query = semantic_surfaceType.get_query(info)
        if "id" in args:
            query = query.filter(semantic_surfaceModel.id == args['id'])
        return query

class surfacesQuery(graphene.ObjectType):
    surfaces = graphene.List(surfacesType, id = graphene.String()) 
    def resolve_surfaces(self, info, **args):
        query = surfacesType.get_query(info)
        if "id" in args:
            query = query.filter(surfacesModel.id == args['id'])
        return query

class Query(metadataQuery, transformQuery, cityobjectsQuery, geometriesQuery, semanticsurfaceQuery, surfacesQuery, locationQuery, radius100Query, insideQuery, citymodelQuery, insideindexQuery, radius100indexQuery):   
    pass 

schema = graphene.Schema(query=Query, types=[metadataType, transformType, city_objectType, geometriesType, semantic_surfaceType, surfacesType])
