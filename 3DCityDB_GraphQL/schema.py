import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
from models import database_srsModel, cityobjectModel, buildingModel, objectclassModel, surface_geometryModel, cityobject_genericattribModel, aggregation_infoModel, thematic_surfaceModel, engine, db_session, made_session
from geoalchemy2 import * 
from sqlalchemy import func, Column, Integer, String
import json 

class database_srsType(SQLAlchemyObjectType):
    class Meta:
        model = database_srsModel
class objectclassType(SQLAlchemyObjectType):
    class Meta:
        model = objectclassModel
class aggregation_infoType(SQLAlchemyObjectType):
    class Meta:
        model = aggregation_infoModel

class surface_geometryType(SQLAlchemyObjectType):
    class Meta:
        model = surface_geometryModel

    def resolve_solid_geometry(self, info, **args):
        if self.solid_geometry != None:
            return engine.scalar(self.solid_geometry.St_AsText())
        else:
            return None

    def resolve_geometry(self, info, **args):
        if self.geometry != None:
            return engine.scalar(self.geometry.ST_AsText())
        else:
            return None

class buildingType(SQLAlchemyObjectType):
    maxlod = graphene.List(surface_geometryType)

    class Meta:
        model = buildingModel    

    def resolve_envelope(self, info):
        if self.envelope != None:
            return engine.scalar(self.envelope.St_AsText())
        else:
            return None

    def resolve_maxlod(self, info):
        max_lod = 0 
        high_geom = [] 

        if self.lod2_multi_surface != None:
            lod2 = 2
            if max_lod <= lod2:
                max_lod = lod2
                high_geom.append(self.lod2_multi_surface)

        elif self.lod2_solid != None: 
            lod = 2
            if max_lod <= lod2:
                max_lod = lod2 
                high_geom.append(self.lod2_solid) 
        elif self.thematic_surfaces != None: 
            for thematic_surface in self.thematic_surfaces:
                if thematic_surface.lod2_multi_surface != None:
                    lod2 = 2
                    if max_lod <= lod2:
                        max_lod = lod2
                        high_geom.append(thematic_surface.lod2_multi_surface) 
        elif self.lod1_multi_surface != None:
            lod1 = 1 
            if max_lod <= lod1:
                max_lod = lod1
                high_geom.append(self.lod1_multi_surface)
          
        elif self.lod1_solid != None:
            lod1 = 1 
            if max_lod <= lod1:
                max_lod = lod1
                high_geom.append(self.lod1_solid)
     
        return high_geom


class cityobjectType(SQLAlchemyObjectType):
    
    class Meta:
        model = cityobjectModel

    def resolve_envelope(self, info):
        if self.envelope != None:
            return engine.scalar(self.envelope.St_AsText())
        else:
            return None

class cityobject_genericattribType(SQLAlchemyObjectType):
    value = graphene.Field(graphene.String)
    
    class Meta:
        model = cityobject_genericattribModel

    def resolve_value(self, info):
        if self.datatype == 1:
            return str(self.strval)
        elif self.datatype == 2:
            return str(self.intval)
        elif self.datatype == 3:
            return str(self.realval)
        else:
            return 'unresolved value'

class thematic_surfaceType(SQLAlchemyObjectType):
    class Meta:
        model = thematic_surfaceModel
    

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
        
class radius100Query(graphene.ObjectType):
    radius100 = graphene.List(buildingType, position=PositionInput(required=True)) 
    def resolve_radius100(self, info, position):
        query_building = buildingType.get_query(info)
        buildings = query_building.filter(func.ST_DWithin(func.ST_SetSRID(func.ST_MakePoint(position.lat, position.long, position.alt), 4979), func.ST_Transform(buildingModel.envelope, 4979), 100, False))
        return buildings

class insideQuery(graphene.ObjectType):
    inside = graphene.List(buildingType, position=PositionInput(required=True)) 
    def resolve_inside(self, info, position):
        query_building = buildingType.get_query(info)
        buildings = query_building.filter(func.ST_Intersects(func.ST_SetSRID(func.ST_MakePoint(position.lat, position.long, position.alt), 7415), buildingModel.envelope))

        return buildings

class buildingidQuery(graphene.ObjectType):
    buildingid = graphene.List(cityobjectType, id = graphene.String()) 
    def resolve_buildingid(self, info, **args):
        query = cityobjectType.get_query(info)
        if "id" in args:
            query = query.filter(cityobjectModel.id == args['id'])
        return query

######################################################## 
##################     STANDARD      ###################
########################################################


class buildingQuery(graphene.ObjectType):
    buildings = graphene.List(buildingType, id = graphene.String()) 
    def resolve_buildings(self, info, **args):
        query = buildingType.get_query(info)
        if "id" in args: 
            query = query.filter(buildingModel.id == args['id'])
        return query

class database_srsQuery(graphene.ObjectType):
    srs = graphene.List(database_srsType, srid=graphene.Int())  
    def resolve_srs(self, info, **args):
        query = database_srsType.get_query(info)
        if "srid" in args: 
            query = query.filter(database_srsModel.srid == args['srid'])
        return query

class objectclassQuery(graphene.ObjectType):
    objectclasses = graphene.List(objectclassType, id = graphene.String()) 
    def resolve_objectclasses(self, info, **args):
        query = objectclassType.get_query(info)
        if "id" in args: 
            query = query.filter(objectclassModel.id == args['id'])
        return query

class aggregation_infoQuery(graphene.ObjectType):
    aggregation_info = graphene.List(aggregation_infoType, id = graphene.String()) 
    def resolve_aggregation_info(self, info, **args):
        query = aggregation_infoType.get_query(info)
        return query

class cityobjectQuery(graphene.ObjectType):
    cityobjects = graphene.List(cityobjectType, id = graphene.String()) 
    def resolve_cityobjects(self, info, **args):
        query = cityobjectType.get_query(info)
        if "id" in args:
            query = query.filter(cityobjectModel.id == args['id'])
        return query

class surface_geometryQuery(graphene.ObjectType):
    surface_geometry = graphene.List(surface_geometryType, id = graphene.String()) 

    def resolve_surface_geometry(self, info, **args):
        query = surface_geometryType.get_query(info)
        if "id" in args: 
            query = query.filter(surface_geometryModel.id == args['id'])
        return query
    
class cityobject_genericattribQuery(graphene.ObjectType):
    cityobject_genericattributes = graphene.List(cityobject_genericattribType, id=graphene.String()) 
    def resolve_cityobject_genericattributes(self, info, **args):
        query = cityobject_genericattribType.get_query(info)
        if "id" in args: 
            query = query.filter(cityobject_genericattribModel.id == args['id'])
        return query

class thematic_surfaceQuery(graphene.ObjectType):
    thematic_surfaces = graphene.List(thematic_surfaceType, id = graphene.String()) 
    def resolve_thematic_surfaces(self, info, **args):
        query = thematic_surfaceType.get_query(info)
        if "id" in args: 
            query = query.filter(thematic_surfaceModel.id == args['id'])
        return query
        
######################################################## 
##################     STANDARD      ###################
########################################################

class Query(database_srsQuery, cityobjectQuery, buildingQuery, objectclassQuery, surface_geometryQuery, cityobject_genericattribQuery, aggregation_infoQuery, thematic_surfaceQuery, insideQuery, locationQuery, radius100Query, buildingidQuery):   
    pass 

schema = graphene.Schema(query=Query, types=[database_srsType, cityobjectType, buildingType, objectclassType, surface_geometryType, cityobject_genericattribType])