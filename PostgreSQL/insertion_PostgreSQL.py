
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import json 
import re #to read integers from string 
from scipy.spatial import ConvexHull
import sys
import os 
libdir = os.path.dirname(__file__)
root_folder= str(os.path.split(libdir)[0]) 
sys.path.append(root_folder)
from algorithms.replace_transform import from_index_to_vertex
from algorithms.replace_transform import transform_vertices

def create_xyzlist(findlist, verticesList, xyzlist, xylist):
    #needed for every geometry 
    for i, temp_list in enumerate(findlist):
        if not isinstance(temp_list, list):
            index = temp_list
            #always append the vertex to the verticesList 
            x, y, z = verticesList[index]
            vertex = [x, y, z]
            xyzlist.append(vertex)
            xylist.append([x, y])
        else:
            create_xyzlist(temp_list, verticesList, xyzlist, xylist)

def create_envelope_hull_box3d(xyzlist, xylist, referenceSystem):
    xlist = [i[0] for i in xyzlist]
    ylist = [i[1] for i in xyzlist]
    zlist = [i[2] for i in xyzlist]
    minx = min(xlist)
    maxx = max(xlist)
    miny = min(ylist)
    maxy = max(ylist)
    minz = min(zlist)
    maxz = max(zlist)
    extent = [minx, miny, minz, maxx, maxy, maxz]

    #12C. Create convexhull
    try:
        indexeshull = ConvexHull(xylist)
        hull = convert_list_to_hull(indexeshull, referenceSystem, xylist)
    except:
        hull = None 
        
    #12C. Create 3Dbox 
    box3D = '((('+str(minx)+' '+str(miny)+' '+str(minz)+','+str(minx)+' '+str(maxy)+' '+str(minz)+','+str(maxx)+' '+str(maxy)+' '+str(minz)+','+str(maxx)+' '+str(miny)+' '+str(minz)+','+str(minx)+' '+str(miny)+' '+str(minz)+')),'+'(('+str(minx)+' '+str(miny)+' '+str(maxz)+','+str(maxx)+' '+str(miny)+' '+str(maxz)+','+str(maxx)+' '+str(maxy)+' '+str(maxz)+','+str(minx)+' '+str(maxy)+' '+str(maxz)+','+str(minx)+' '+str(miny)+' '+str(maxz)+')),'+'(('+str(minx)+' '+str(miny)+' '+str(minz)+','+str(minx)+' '+str(miny)+' '+str(maxz)+','+str(minx)+' '+str(maxy)+' '+str(maxz)+','+str(minx)+' '+str(maxy)+' '+str(minz)+','+str(minx)+' '+str(miny)+' '+str(minz)+')),'+'(('+str(minx)+' '+str(maxy)+' '+str(minz)+','+str(minx)+' '+str(maxy)+' '+str(maxz)+','+str(maxx)+' '+str(maxy)+' '+str(maxz)+','+str(maxx)+' '+str(maxy)+' '+str(minz)+','+str(minx)+' '+str(maxy)+' '+str(minz)+')),'+'(('+str(maxx)+' '+str(maxy)+' '+str(minz)+','+str(maxx)+' '+str(maxy)+' '+str(maxz)+','+str(maxx)+' '+str(miny)+' '+str(maxz)+','+str(maxx)+' '+str(miny)+' '+str(minz)+','+str(maxx)+' '+str(maxy)+' '+str(minz)+')),'+'(('+str(maxx)+' '+str(miny)+' '+str(minz)+','+str(maxx)+' '+str(miny)+' '+str(maxz)+','+str(minx)+' '+str(miny)+' '+str(maxz)+','+str(minx)+' '+str(miny)+' '+str(minz)+','+str(maxx)+' '+str(miny)+' '+str(minz)+')))'                        
           
    if referenceSystem is None: 
        box3D = 'POLYHEDRALSURFACE Z {}'.format(box3D)
    else:
        box3D = 'SRID={}; POLYHEDRALSURFACE Z {}'.format(referenceSystem, box3D)
    return extent, hull, box3D


def convert_surface_to_polygon(surface, referenceSystem):
    linestring_index = 0 
    linestring_list = []
    for linestring in surface:
        vertex_list = []
        first_vertex = "{0} {1} {2}".format(linestring[0][0], linestring[0][1], linestring[0][2])
        for vertex in linestring:
            vertex = "{0} {1} {2}".format(vertex[0], vertex[1], vertex[2])
            vertex_list.append(vertex)
        vertex_list.append(first_vertex)
        linestring_list.append(tuple(vertex_list)) 
        linestring_index = linestring_index + 1

    if len(linestring_list) == 1:
            polygon = '(' + str(tuple(vertex_list)) + ')'
    else:
        polygon = str(tuple(linestring_list))
    polygon = polygon.replace("'", "")
    polygon = polygon.replace('"', "")
    if referenceSystem is None: 
        polygon = 'POLYGONZ {}'.format(polygon)
    else:
        polygon = 'SRID={}; POLYGONZ {}'.format(referenceSystem, polygon)
    return polygon

def convert_list_to_hull(hull, referenceSystem, xylist):
    hullvertices = []
    first_vertex = "{0} {1}".format(xylist[hull.vertices[0]][0], xylist[hull.vertices[0]][1])
    for vertex in hull.vertices:
        hullvertices.append("{0} {1}".format(xylist[vertex][0], xylist[vertex][1]))
    hullvertices.append(first_vertex)
    polygon = '(' + str(tuple(hullvertices)) + ')'
    polygon = polygon.replace("'", "")
    polygon = polygon.replace('"', "")
    if referenceSystem is None: 
        polygon = 'POLYGON {}'.format(polygon)
    else:
        polygon = 'SRID={}; POLYGON {}'.format(referenceSystem, polygon)
    return polygon

def create_schema(conn, cur, data, schema_referenceSystem, schema_name, use_index):
    #5. Create schema called City_schema
    command_drop = """DROP SCHEMA if exists {} CASCADE""".format(schema_name)
        
    
    #6. Create schema 
    command_create = """
        CREATE SCHEMA {}
        CREATE SEQUENCE geometry_seq INCREMENT BY 1 START WITH 1 NO CYCLE
        CREATE SEQUENCE semantic_surface_seq INCREMENT BY 1 START WITH 1 NO CYCLE
        CREATE SEQUENCE surfaces_seq INCREMENT BY 1 START WITH 1 NO CYCLE

        CREATE TABLE metadata (
            id text PRIMARY KEY,
            object jsonb
        )
        CREATE TABLE transform (
            id text PRIMARY KEY,
            object jsonb
        )

        CREATE TABLE city_object (
            id text PRIMARY KEY,
            object jsonb,
            attributes jsonb,
            convexhull geometry(POLYGON),
            globalconvexhull geometry(POLYGON), 
            metadata_id text REFERENCES metadata (id)
        )
            
        CREATE TABLE geometries (
            id integer DEFAULT nextval('geometry_seq') PRIMARY KEY, 
            object jsonb,
            city_object_id text REFERENCES city_object (id)
        )

        CREATE TABLE semantic_surface (
            id integer DEFAULT nextval('semantic_surface_seq') PRIMARY KEY, 
            object jsonb,
            city_object_id text REFERENCES city_object (id),
            geometries_id integer REFERENCES geometries (id)
        )

        CREATE TABLE surfaces (
            id integer DEFAULT nextval('surfaces_seq') PRIMARY KEY,
            geometry geometry(POLYGONZ),
            solid_num integer, 
            shell_num_void integer, 
            surface_num integer,
            geometries_id integer REFERENCES geometries (id),
            semantic_surface_id integer REFERENCES semantic_surface (id),
            city_object_id text REFERENCES city_object (id)
        )

        CREATE TABLE parents_children (
            parents_id text, 
            children_id text, 
            PRIMARY KEY (parents_id, children_id), 
            FOREIGN KEY (parents_id) REFERENCES city_object (id) ON UPDATE CASCADE, 
            FOREIGN KEY (children_id) REFERENCES city_object (id) ON UPDATE CASCADE
            )
                    """.format(schema_name, schema_referenceSystem)

    commands = [command_drop, command_create]
    
    for command in commands:
        cur.execute(command)
        conn.commit() 

    #7. Alter sequence 
    command_alter = """
        SET search_path to {}, public;
        ALTER SEQUENCE geometry_seq OWNED BY geometries.id;
        ALTER SEQUENCE surfaces_seq OWNED BY surfaces.id;
        ALTER SEQUENCE semantic_surface_seq OWNED BY semantic_surface.id; 
        
        """.format(schema_name)
    cur.execute(command_alter)
    conn.commit()

    if use_index == 'yes':
        command_alter = """
        SET search_path to {}, public;
        CREATE INDEX geometry_index ON surfaces USING GIST(geometry);
        CREATE INDEX convexhull_index ON city_object USING GIST(convexhull);
        CREATE INDEX semantic_surface_index ON surfaces USING BTREE (semantic_surface_id)
        """.format(schema_name)
        cur.execute(command_alter)
        conn.commit()
        

def insert_PostgreSQL(file_name, schema_name, new_or_old, use_index): 
    #2. Connect to database 
    conn = psycopg2.connect("host=localhost dbname= insertdb user=postgres password=1234")
    cur = conn.cursor() 

    #3. open CityJSON file 
    stringName = str('/Users/karinstaring/GeomaticsThesis/datasets/old/' + file_name + '.json')
    CityJSON_file = open(stringName, encoding='utf-8-sig') 
    data = json.load(CityJSON_file)
    
    #4. Find referenceSystem 
    if 'metadata' in data.keys():
        if 'referenceSystem' in data['metadata']:
            referenceSystem = int(re.search(r'\d+', data['metadata']['referenceSystem']).group())
            schema_referenceSystem = ', ' + str(referenceSystem)
        else:
            # (The reference system has been changed to 2056 for zürich)
            referenceSystem = None
            schema_referenceSystem = '' 
    
    #5. Create schema 
    if new_or_old == 'new':
        create_schema(conn, cur, data, schema_referenceSystem, schema_name, use_index)
    else:
        command_alter = """
        SET search_path to {};
        """.format(schema_name)
        cur.execute(command_alter)
        conn.commit()

    #8. metadata 
    id_metadata = 'metadata_' + str(file_name)
    metadata = {} 
    metadata['type'] = data['type']
    metadata['version'] = data['version']
    if 'metadata' in data.keys():
        for key in data['metadata']:
            metadata[key] = data['metadata'][key]

    insert_metadata = """INSERT INTO {}.metadata (id, object) VALUES (%s, %s)""".format(schema_name)
    cur.execute(insert_metadata, (id_metadata, json.dumps(metadata)))
    conn.commit() 

    #9. transform
    if 'transform' in data.keys():  
        id_transform = 'transform_' + str(file_name)
        transform = data['transform']

        insert_transform = """INSERT INTO {}.transform (id, object) VALUES (%s, %s)""".format(schema_name)
        cur.execute(insert_transform, (id_transform, json.dumps(transform))) 
        conn.commit() 

        #10. transform vertices 
        vertices = transform_vertices(transform, data['vertices'])
    else:
        vertices =  data['vertices']

    #11. CityObjects 
    for ID in data['CityObjects']:
        id_cityobject = ID
        cityobject = data['CityObjects'][ID]

        #11.A geometry 
        geometry_list = []
        for geometry in cityobject['geometry']:
            geometry_list.append(geometry)
        del cityobject['geometry']

        #11.B attributes 
        attributes = {}
        if 'attributes' in cityobject.keys():
            attributes = cityobject['attributes']
            del cityobject['attributes']
            
        #12A. Create geographicalExtent
        xyzlist = []
        xylist = [] 

        for geometry in geometry_list: 
            boundaries = geometry['boundaries']
            findlist = boundaries
            create_xyzlist(findlist, vertices, xyzlist, xylist)
        if xyzlist != []:
             extent, hull, box3D = create_envelope_hull_box3d(xyzlist, xylist, referenceSystem)
        else:
            extent = None
            hull = None
            box3D = None
        
        insert_cityobjects = """INSERT INTO {}.city_object (id, object, attributes, convexhull, globalconvexhull, metadata_id) VALUES (%s, %s, %s, %s, %s, %s)""".format(schema_name)
        cur.execute(insert_cityobjects, (id_cityobject, json.dumps(cityobject), json.dumps(attributes), hull, hull, id_metadata))
        conn.commit() 
       
        #12B. geometries 
        for geometry in geometry_list: 
            
            geom_type = geometry['type']
            #12C. boundaries
            boundaries = geometry['boundaries']
            
            del geometry['boundaries']
            
            #12D. semantics 
            semantics = None
            if 'semantics' in geometry.keys():
                semantics = geometry['semantics']
                del geometry['semantics']

            #12E. object without semantics 
            insert_geometry = """INSERT INTO {}.geometries (id, object, city_object_id) VALUES (DEFAULT, %s, %s)""".format(schema_name)
            cur.execute(insert_geometry, (json.dumps(geometry), id_cityobject)) 
            conn.commit() 

            #12F. geometries id 
            geometry_value_id = """SELECT currval(pg_get_serial_sequence('geometries', 'id'))"""
            cur.execute(geometry_value_id)
            currval = cur.fetchall()
            id_geometries = currval[0][0]

             #12G. semantics 
            if semantics != None: 
                id_list_semantics = []
                for semantic_object in semantics['surfaces']:
                    insert_semantics = """INSERT INTO {}.semantic_surface (id, object, city_object_id, geometries_id) VALUES (DEFAULT, %s, %s, %s)""".format(schema_name)
                    cur.execute(insert_semantics, (json.dumps(semantic_object), id_cityobject, id_geometries))
                    conn.commit() 

                    semantics_value_id = """SELECT currval(pg_get_serial_sequence('semantic_surface', 'id'))"""
                    cur.execute(semantics_value_id)
                    currval = cur.fetchall()
                    semantics_id = currval[0][0]
                    id_list_semantics.append(semantics_id)

                    semantics['surfaces'] = id_list_semantics 
            else:
                semantics = ''

            #13.A replace indexes 
            boundaries = from_index_to_vertex(boundaries, vertices)

            if geom_type == 'MultiSurface' or geom_type == 'CompositeSurface':
                solid_index = None 
                shell_index = 0
                surface_index = 0 
                for surface in boundaries:
                    polygon = convert_surface_to_polygon(surface, referenceSystem)
                    if semantics != '':
                        value = semantics['values'][surface_index]
                        semantic_id = semantics['surfaces'][value]
                    else:
                        semantic_id = None
                    insert_geometry = """INSERT INTO {}.surfaces (id, geometry, solid_num, shell_num_void, surface_num, geometries_id, semantic_surface_id, city_object_id) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)""".format(schema_name)
                    cur.execute(insert_geometry, (polygon, solid_index, shell_index, surface_index, id_geometries, semantic_id, id_cityobject)) 
                    conn.commit() 
                    surface_index = surface_index + 1

            elif geom_type == 'Solid':
                solid_index = 0
                shell_index = 0 
                for shell in boundaries:
                    surface_index = 0 
                    for surface in shell:
                        polygon = convert_surface_to_polygon(surface, referenceSystem)
                        if semantics != '':
                            value = semantics['values'][shell_index][surface_index]
                            semantic_id = semantics['surfaces'][value]
                        else: 
                            semantic_id = None
                        insert_geometry = """INSERT INTO {}.surfaces (id, geometry, solid_num, shell_num_void, surface_num, geometries_id, semantic_surface_id, city_object_id) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)""".format(schema_name)
                        cur.execute(insert_geometry, (polygon, solid_index, shell_index, surface_index, id_geometries, semantic_id, id_cityobject)) 
                        conn.commit() 
                        surface_index = surface_index + 1 
                    shell_index = shell_index + 1

            elif geom_type == 'MultiSolid' or geom_type == 'CompositeSolid':
                solid_index = 0 
                for solid in boundaries: 
                    shell_index = 0 
                    for shell in solid:
                        surface_index = 0 
                        for surface in shell:
                            polygon = convert_surface_to_polygon(surface, referenceSystem)
                            if semantics != '':
                                value = semantics['values'][solid_index][shell_index][surface_index]
                                semantic_id = semantics['surfaces'][value]
                            else:
                                semantic_id = None
                            semantic_id = None
                            insert_geometry = """INSERT INTO {}.surfaces (id, geometry, solid_num, shell_num_void, surface_num, geometries_id, semantic_surface_id, city_object_id) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s)""".format(schema_name)
                            cur.execute(insert_geometry, (polygon, solid_index, shell_index, surface_index, id_geometries, semantic_id, id_cityobject)) 
                            conn.commit() 
                            surface_index = surface_index + 1 
                        shell_index = shell_index + 1
                    solid_index = solid_index + 1 

            else:
                print('unknown geometry type')
 
    #13. parents_children 
    for ID in data['CityObjects']:
        id_cityobject = ID
        cityobject = data['CityObjects'][ID]
        if cityobject['type'] == 'BuildingPart':
            if 'parents' in cityobject.keys():
                parents = cityobject['parents']
                for parent in parents: 
                    insert_parents_children = """INSERT INTO {}.parents_children (parents_id, children_id) VALUES (%s, %s)""".format(schema_name)
                    cur.execute(insert_parents_children, (parent, id_cityobject))
                    conn.commit()
    #5. Update schema
    #7. Alter sequence 
    
    command_alter = """
        SET search_path TO {}, public; 
        ALTER TABLE city_object ALTER COLUMN globalconvexhull TYPE geometry(POLYGON) USING ST_Transform(globalconvexhull, 4979);
        """.format(schema_name, schema_name, schema_name)
    cur.execute(command_alter)
    conn.commit()

    if use_index == 'yes':
        if new_or_old == 'new':
            command_alter = """
            CREATE INDEX globalconvexhull_index ON city_object USING GIST(globalconvexhull);
            """.format(schema_name, schema_name, schema_name)
            cur.execute(command_alter)
            conn.commit()
    