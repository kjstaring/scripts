from database import Base, engine
from sqlalchemy import Column, String, Text, JSON, Numeric, ARRAY ,Integer, ForeignKey, Table, Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, backref
from geoalchemy2 import Geometry

parents_children = Table(
    'parents_children',
    Base.metadata,
    Column('parents_id', Text, ForeignKey('city_object.id')),
    Column('children_id', Text, ForeignKey('city_object.id'))
    )

class metadataModel(Base):
    __tablename__ = 'metadata'
    id = Column(Text, primary_key=True)
    object = Column(postgresql.JSONB)

class transformModel(Base):
    __tablename__ = 'transform'
    id = Column(Text, primary_key=True)
    object = Column(postgresql.JSONB)


class city_objectModel(Base):
    __tablename__ = 'city_object'
    id = Column(Text, primary_key=True)
    object = Column(postgresql.JSONB)
    attributes = Column(JSON)
    convexhull = Column(Geometry, index=True)
    globalconvexhull = Column(Geometry, index=True)
    metadata_id = Column(Text, ForeignKey('metadata.id'))
    citymodel = relationship('metadataModel', 
    primaryjoin = ('metadata.c.id == city_object.c.metadata_id'), 
    backref = 'cityobjects')
    parents = relationship('city_objectModel',
    primaryjoin= id == parents_children.c.children_id,
    secondaryjoin= id == parents_children.c.parents_id,
    secondary = parents_children, 
    backref=backref('children'))
    

class geometriesModel(Base):
    __tablename__ = 'geometries'
    id = Column(Integer, primary_key=True)
    object = Column(postgresql.JSONB)
    city_object_id = Column(Text, ForeignKey('city_object.id'))
    cityobject = relationship('city_objectModel', 
    primaryjoin = ('city_object.c.id == geometries.c.city_object_id'), 
    backref = 'geometries')

class semantic_surfaceModel(Base):
    __tablename__ = 'semantic_surface'
    id = Column(Integer, primary_key=True)
    object = Column(postgresql.JSONB)
    city_object_id = Column(Integer, ForeignKey('city_object.id'))
    cityobject = relationship('city_objectModel', 
    primaryjoin = ('city_object.c.id == semantic_surface.c.city_object_id'), 
    backref = 'semantics')
    geometries_id = Column(Integer, ForeignKey('geometries.id'))
    geometries = relationship('geometriesModel', 
    primaryjoin = ('geometries.c.id == semantic_surface.c.geometries_id'), 
    backref = 'semantics')

class surfacesModel(Base):
    __tablename__ = 'surfaces'
    id = Column(Integer, primary_key=True)
    geometry = Column(Geometry, index=True)
    solid_num = Column(Integer)
    shell_num_void = Column(Integer)
    surface_num = Column(Integer)
    geometries_id = Column(Integer, ForeignKey('geometries.id'))
    geometries = relationship('geometriesModel', 
    primaryjoin = ('geometries.c.id == surfaces.c.geometries_id'), 
    backref = 'surfaces')
    
    semantic_surface_id = Column(Integer, ForeignKey('semantic_surface.id'), index=True)
    semantics = relationship('semantic_surfaceModel', 
    primaryjoin = ('semantic_surface.c.id == surfaces.c.semantic_surface_id'), 
    backref = 'surfaces')
    

# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html


Base.prepare(engine)

