from database import Base, engine, db_session, made_session
from sqlalchemy import Column, String, Text, JSON, Numeric, ARRAY ,Integer, VARCHAR, ForeignKey, DateTime, LargeBinary, Date, Date
from sqlalchemy.orm import relationship, column_property
from geoalchemy2 import * 
#from geoalchemy2 import Geometry, functions 

class database_srsModel(Base): 
    __tablename__ = 'database_srs'
    srid = Column(Integer, primary_key=True)
    gml_srs_name = Column(VARCHAR(1000)) 

class objectclassModel(Base): 
    __tablename__ = 'objectclass'
    id = Column(Integer, primary_key=True)
    is_toplevel = Column(Integer)
    classname = Column(VARCHAR(256)) 
    tablename = Column(VARCHAR(30)) 
    superclass_id = Column(Integer, ForeignKey('objectclass.id'))
    #objectclass_superclass_fk
    superclass = relationship('objectclassModel', 
    primaryjoin = ('objectclass.c.id == objectclass.c.superclass_id'), 
    remote_side = 'objectclassModel.id')
    #objectclass_baseclass_fk 
    baseclass_id = Column(Integer, ForeignKey('objectclass.id'))
    baseclass = relationship('objectclassModel', 
    primaryjoin = ('objectclass.c.id == objectclass.c.baseclass_id'), 
    remote_side = 'objectclassModel.id')
    
class cityobjectModel(Base):
    __tablename__ = 'cityobject'
    id = Column(Integer, primary_key=True) 
    gmlid = Column(VARCHAR(256)) 
    envelope = Column(Geometry) 
    #cityobject_objectclass_fk 
    objectclass_id = Column(Integer, ForeignKey('objectclass.id')) # NOT NULL UPON CREATION 
    objectclass = relationship('objectclassModel')
    genericattrib = relationship('cityobject_genericattribModel', 
    primaryjoin = ('cityobject.c.id == cityobject_genericattrib.c.cityobject_id'))

    data_type = column_property(select([objectclassModel.tablename]).where(objectclassModel.id == objectclass_id)) 
    
    #attributes
    creation_date = Column(Date)
    last_modification_date = Column(Date)
    updating_person = Column(VARCHAR(256))

    __mapper_args__ = {
        'polymorphic_identity':'cityobject',
        'polymorphic_on': data_type
    }
    
class thematic_surfaceModel(cityobjectModel):
    __tablename__ = 'thematic_surface'
    id = Column(Integer, ForeignKey('cityobject.id'), primary_key=True)
    #them_surface_cityobject_fk 
    cityobject = relationship('cityobjectModel', 
    primaryjoin = ('cityobject.c.id == thematic_surface.c.id'), 
    backref='thematic_surface')
    #them_surface_objclass_fk (useless due to the inheritance relationship)
    #them_surface_building_fk
    building_id = Column(Integer, ForeignKey('building.id'))
    buildings = relationship('buildingModel', 
    primaryjoin = ('building.c.id == thematic_surface.c.building_id'), 
    backref='thematic_surfaces')
    #them_surface_lod2msrf_fk
    lod2_multi_surface_id = Column(Integer, ForeignKey('surface_geometry.id'))
    lod2_multi_surface = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == thematic_surface.c.lod2_multi_surface_id'), 
    backref = 'thematic_surface_msrf2')
    
    __mapper_args__ = {
        'polymorphic_identity':'thematic_surface', 
        'inherit_condition': id == cityobjectModel.id
    }
    
class buildingModel(cityobjectModel):  
    __tablename__ = 'building'
    id = Column(Integer, ForeignKey('cityobject.id'),primary_key=True)
    #building_cityobject_fk
    cityobject = relationship('cityobjectModel', backref='building') 
    #building_objectclass_fk (useless due to the inheritance relationship)
    #building_parent_fk
    building_parent_id = Column(Integer, ForeignKey('building.id'))
    building_parent = relationship('buildingModel', 
    primaryjoin = ('building.c.id == building.c.building_parent_id'),
    remote_side = 'buildingModel.id')
    #building_root_fk
    building_root_id = Column(Integer, ForeignKey('building.id'))
    building_root = relationship('buildingModel', 
    primaryjoin = ('building.c.id == building.c.building_root_id'),
    remote_side = 'buildingModel.id') 
    
    #building_lod1msrf_fk
    lod1_multi_surface_id = Column(Integer, ForeignKey('surface_geometry.id'))
    lod1_multi_surface = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == building.c.lod1_multi_surface_id'), 
    backref = 'building_msrf1')
    #building_lod2msrf_fk
    lod2_multi_surface_id = Column(Integer, ForeignKey('surface_geometry.id'))
    lod2_multi_surface = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == building.c.lod2_multi_surface_id'), 
    backref = 'building_msrf2')
    #building_lod2solid_fk
    lod1_solid_id = Column(Integer, ForeignKey('surface_geometry.id'))
    lod1_solid = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == building.c.lod1_solid_id'), 
    backref= 'building_solid1')
    #building_lod2solid_fk
    lod2_solid_id = Column(Integer, ForeignKey('surface_geometry.id'))
    lod2_solid = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == building.c.lod2_solid_id'),
    backref= 'building_solid2')

    
    __mapper_args__ = {
        'polymorphic_identity':'building', 
        'inherit_condition': id == cityobjectModel.id
    }

class surface_geometryModel(Base): 
    __tablename__ = 'surface_geometry'
    id = Column(Integer, primary_key=True)
    #surface_geom_parent_fk
    parent_id = Column(Integer, ForeignKey('surface_geometry.id'))
    parent = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == surface_geometry.c.parent_id'), 
    remote_side = 'surface_geometryModel.id')
    #surface_geom_root_fk
    root_id = Column(Integer, ForeignKey('surface_geometry.id'))
    root = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == surface_geometry.c.root_id'), 
    remote_side = 'surface_geometryModel.id', backref='children')
    is_solid = Column(Numeric)
    is_composite = Column(Numeric)
    solid_geometry = Column(Geometry)
    geometry = Column(Geometry)
    #surface_geom_cityobject_fk
    cityobject_id = Column(Integer, ForeignKey('cityobject.id'))
    cityobject = relationship('cityobjectModel', 
    primaryjoin = ('cityobject.c.id == surface_geometry.c.cityobject_id'), 
    backref = 'surfaces')

class cityobject_genericattribModel(Base):
    __tablename__ = 'cityobject_genericattrib'
    id = Column(Integer, primary_key=True)
    attrname = Column(VARCHAR(256)) 
    datatype = Column(Integer) 

    # TODO: the selection of a column based on datatype 
    strval = Column(VARCHAR(4000)) 
    intval = Column(Integer)
    realval = Column(Numeric) #double precision 
    urival = Column(VARCHAR(4000))
    dateval = Column(DateTime(timezone=True))
    unit = Column(VARCHAR(4000)) 
    genattribset_codespace = Column(VARCHAR(4000))
    blobval = Column(LargeBinary)
    geomval = Column(Geometry)
        
    #genericattrib_geom_fk
    surface_geometry_id = Column(Integer, ForeignKey('surface_geometry.id'))
    surface_geometry = relationship('surface_geometryModel', 
    primaryjoin = ('surface_geometry.c.id == cityobject_genericattrib.c.surface_geometry_id'), 
    backref = 'attributes')
    #genericattrib_cityobj_fk
    cityobject_id = Column(Integer, ForeignKey('cityobject.id'))
    cityobject = relationship('cityobjectModel', 
    primaryjoin = ('cityobject.c.id == cityobject_genericattrib.c.cityobject_id'))

    
class aggregation_infoModel(Base):
    __tablename__ = 'aggregation_info'
    #aggregation_info_fk1
    child_id = Column(Integer, ForeignKey('objectclass.id'), primary_key = True)
    child = relationship('objectclassModel', 
    primaryjoin = ('objectclass.c.id == aggregation_info.c.child_id'))
    #aggregation_info_fk2
    parent_id = Column(Integer, ForeignKey('objectclass.id'), primary_key = True)
    parent = relationship('objectclassModel', 
    primaryjoin = ('objectclass.c.id == aggregation_info.c.parent_id'))
    join_table_or_column_name = Column(VARCHAR(30), primary_key = True) 
    min_occurs = Column(Integer)
    max_occurs = Column(Integer)
    is_composite = Column(Numeric)


Base.prepare(engine)