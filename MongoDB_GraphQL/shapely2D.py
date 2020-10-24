from shapely.geometry import * 
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
import numpy as np 
from graphql import GraphQLError

# Test data 
geometry_one = [[[[998681.106, 239463.882, 120.568], [998669.771, 239443.359, 120.568], [998654.444, 239415.606, 120.568], [998648.248, 239419.029, 120.568], [998642.023, 239414.741, 120.568], [998635.606, 239418.285, 120.568], [998647.29, 239439.44, 120.568], [998665.536, 239472.481, 120.568], [998668.459, 239477.774, 120.568], [998672.653, 239485.367, 120.568], [998672.982, 239485.185, 120.568], [998673.933, 239484.66, 120.568], [998681.927, 239480.244, 120.568], [998674.81, 239467.358, 120.568]]], [[[998674.81, 239467.358, 170.285], [998665.536, 239472.481, 170.285], [998647.29, 239439.44, 170.285], [998635.606, 239418.285, 170.285], [998642.023, 239414.741, 170.285], [998648.248, 239419.029, 170.285], [998654.444, 239415.606, 170.285], [998669.771, 239443.359, 170.285], [998681.106, 239463.882, 170.285]]], [[[998672.982, 239485.185, 158.172], [998672.653, 239485.367, 158.172], [998668.459, 239477.774, 158.172], [998665.536, 239472.481, 158.172], [998674.81, 239467.358, 158.172], [998681.927, 239480.244, 158.172], [998673.933, 239484.66, 158.172]]], [[[998674.81, 239467.358, 158.172], [998665.536, 239472.481, 158.172], [998665.536, 239472.481, 170.285], [998674.81, 239467.358, 170.285]]], [[[998674.81, 239467.358, 120.568], [998674.81, 239467.358, 170.285], [998681.106, 239463.882, 170.285], [998681.106, 239463.882, 120.568]]], [[[998681.927, 239480.244, 120.568], [998681.927, 239480.244, 158.172], [998674.81, 239467.358, 158.172], [998674.81, 239467.358, 120.568]]], [[[998673.933, 239484.66, 120.568], [998673.933, 239484.66, 158.172], [998681.927, 239480.244, 158.172], [998681.927, 239480.244, 120.568]]], [[[998672.982, 239485.185, 120.568], [998672.982, 239485.185, 158.172], [998673.933, 239484.66, 158.172], [998673.933, 239484.66, 120.568]]], [[[998672.653, 239485.367, 120.568], [998672.653, 239485.367, 158.172], [998672.982, 239485.185, 158.172], [998672.982, 239485.185, 120.568]]], [[[998668.459, 239477.774, 120.568], [998668.459, 239477.774, 158.172], [998672.653, 239485.367, 158.172], [998672.653, 239485.367, 120.568]]], [[[998665.536, 239472.481, 120.568], [998665.536, 239472.481, 158.172], [998668.459, 239477.774, 158.172], [998668.459, 239477.774, 120.568]]], [[[998647.29, 239439.44, 120.568], [998647.29, 239439.44, 170.285], [998665.536, 239472.481, 170.285], [998665.536, 239472.481, 120.568]]], [[[998635.606, 239418.285, 120.568], [998635.606, 239418.285, 170.285], [998647.29, 239439.44, 170.285], [998647.29, 239439.44, 120.568]]], [[[998642.023, 239414.741, 120.568], [998642.023, 239414.741, 170.285], [998635.606, 239418.285, 170.285], [998635.606, 239418.285, 120.568]]], [[[998648.248, 239419.029, 120.568], [998648.248, 239419.029, 170.285], [998642.023, 239414.741, 170.285], [998642.023, 239414.741, 120.568]]], [[[998654.444, 239415.606, 120.568], [998654.444, 239415.606, 170.285], [998648.248, 239419.029, 170.285], [998648.248, 239419.029, 120.568]]], [[[998669.771, 239443.359, 120.568], [998669.771, 239443.359, 170.285], [998654.444, 239415.606, 170.285], [998654.444, 239415.606, 120.568]]], [[[998681.106, 239463.882, 120.568], [998681.106, 239463.882, 170.285], [998669.771, 239443.359, 170.285], [998669.771, 239443.359, 120.568]]]]
geometry_two = [[[[999823.949, 235667.953, 24.72], [999816.629, 235654.271, 24.72], [999801.035, 235625.122, 24.72], [999786.715, 235632.782, 24.72], [999802.813, 235662.875, 24.72], [999809.628, 235675.613, 24.72]]], [[[999823.949, 235667.953, 66.53], [999809.628, 235675.613, 66.53], [999802.813, 235662.875, 66.53], [999786.715, 235632.782, 66.53], [999801.035, 235625.122, 66.53], [999816.629, 235654.271, 66.53]]], [[[999809.628, 235675.613, 24.72], [999809.628, 235675.613, 66.53], [999823.949, 235667.953, 66.53], [999823.949, 235667.953, 24.72]]], [[[999802.813, 235662.875, 24.72], [999802.813, 235662.875, 66.53], [999809.628, 235675.613, 66.53], [999809.628, 235675.613, 24.72]]], [[[999786.715, 235632.782, 24.72], [999786.715, 235632.782, 66.53], [999802.813, 235662.875, 66.53], [999802.813, 235662.875, 24.72]]], [[[999801.035, 235625.122, 24.72], [999801.035, 235625.122, 66.53], [999786.715, 235632.782, 66.53], [999786.715, 235632.782, 24.72]]], [[[999816.629, 235654.271, 24.72], [999816.629, 235654.271, 66.53], [999801.035, 235625.122, 66.53], [999801.035, 235625.122, 24.72]]], [[[999823.949, 235667.953, 24.72], [999823.949, 235667.953, 66.53], [999816.629, 235654.271, 66.53], [999816.629, 235654.271, 24.72]]]]

insidePolygon = Polygon([[999800, 235640], [999800, 235650], [999805, 235650], [999805, 235640]])
outsidePolygon = Polygon([[999825, 235640], [999825, 235650], [999830, 235650], [999830, 235640]])

# delfshaven
insidePolygon = Polygon([[90430, 436060], [90430, 436090], [90450, 436090], [90450, 436060]])
# vienna
insidePolygon = Polygon([[1000, 340560], [1000, 340590], [1250, 340590], [1250, 340560]])
# potsdam 
insidePolygon = Polygon([[3367000, 5808000], [3367000, 5809000], [3368000, 5809000], [3368000, 5808000]])
# newyork
insidePolygon = Polygon([[998000, 239000], [998000, 240000], [999000, 240000], [999000, 239000]])

def from_surfaces_to_points(boundaries, xyPoints):
    for i, temp_list in enumerate(boundaries):
        if not isinstance(temp_list[0], list):
            xyVertex = temp_list[:2]
            xyPoints.append(xyVertex)
        else:
            boundaries[i] = from_surfaces_to_points(temp_list, xyPoints)
    return boundaries 

# attributes and methods 
def area(geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    return geom2D.area 

def bounds(geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    return geom2D.bounds

def length(geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    return geom2D.length

def geom_type(geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    return geom2D.geom_type

def distance(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Check if input2D is a point 
    if type(input2D) is not Point:
        print('input is not shapely.geometry.point.Point')
    else:
        return input2D.distance(geom2D)

# Binary predicates 
def equals(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.equals(geom2D)
    return result 

def almost_equals(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.almost_equals(geom2D)
    return result 

def contains(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.contains(geom2D)
    return result 

def crosses(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.crosses(geom2D)
    return result 

def disjoint(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.disjoint(geom2D)
    return result 

def intersects(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    if type(input2D) is not Point:
        print('input is not shapely.geometry.point.Point')
    else:
        return input2D.intersects(geom2D)

def overlaps(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.overlaps(geom2D)
    return result 

def touches(input2D, geom3D): 
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.touches(geom2D)
    return result 

def within(input2D, geom3D): # geometry within input
    # create ConvexHull as Polygon out of surfaces
    xyPoints = [] 
    from_surfaces_to_points(geom3D, xyPoints)
    hull = ConvexHull(xyPoints)
    coordinates2D = np.array(xyPoints)[hull.vertices].tolist()
    geom2D = Polygon(coordinates2D) 
    # Create a polygon from the MultiSurface input 
    input2D = Polygon(list(map(tuple, input2D))) 
    result = input2D.within(geom2D)
    return result 

# Visualization 

#xyPoints = np.array(xyPoints)
#plt.plot(xyPoints[:,0], xyPoints[:,1], 'o')
#for simplex in hull.simplices:
#    plt.plot(xyPoints[simplex, 0], xyPoints[simplex, 1], 'k-')
#plt.plot(xyPoints[hull.vertices,0], xyPoints[hull.vertices,1], 'r--', lw=2)
#plt.plot(xyPoints[hull.vertices[0],0], xyPoints[hull.vertices[0],1], 'ro')
#plt.show()
