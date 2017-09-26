import arcpy
from time import clock
import json


def union_segments(lines, route_table):
    segment_routes = None
    route_segments = {}
    print 'segments'
    with arcpy.da.SearchCursor(route_table, ['SegmentId', 'RouteId']) as cursor:
        segment_routes = dict(cursor)
    print 'routes'
    with arcpy.da.SearchCursor(lines, ['SegmentId', 'SHAPE@']) as cursor:
        for seg_id, shape in cursor:
            route_id = segment_routes.get(seg_id, None)
            if route_id is not None:
                if route_id not in route_segments:
                    route_segments[route_id] = shape
                else:
                    route_segments[route_id] = route_segments[route_id].union(shape)

    for route in route_segments:
        if route_segments[route].isMultipart:
            print('Route: {} is multipart'.format(route))
        if type(route_segments[route]) is not arcpy.Polyline:
            print('Route: {} is not single Polyline'.format(route))

    return route_segments


def get_z_distances(line, surface, densification_factor=0.995):
    if densification_factor > 1:
        densification_factor = densification_factor * 0.01
    d_multiplier = 1 - densification_factor
    dense_line = line.densify('DISTANCE', line.length * d_multiplier, 5)
    # points = [arcpy.PointGeometry(p, dense_line.spatialRefernce, has_z=True)]
    try:
        interp_time = clock()
        arcpy.CheckOutExtension("3D")
        z_line = arcpy.InterpolateShape_3d(surface, dense_line, arcpy.Geometry())[0]
        print 'Interpolate time', clock() - interp_time
    except Exception as e:
        print e
    finally:
        print 'check in'
        arcpy.CheckInExtension("3D")

    z_points = z_line.getPart(0)

    distance_elevations = []
    for point in z_points:
        dist = line.measureOnLine(point)
        elevation = point.Z
        distance_elevations.append((dist, elevation))

    return distance_elevations

    # arcpy.TruncateTable_management('data/temp.gdb/output_points')
    # with arcpy.da.InsertCursor('data/temp.gdb/output_points', ['dist', 'elevation', 'SHAPE@']) as cursor:
    #     for point in z_points:
    #         dist = line.measureOnLine(point, use_percentage=True)
    #         elevation = point.Z
    #         shape = arcpy.PointGeometry(point, elevation, dense_line.spatialReference, True)
    #         cursor.insertRow((dist, elevation, shape))


if __name__ == '__main__':
    trails = r'C:\GisWork\Trails\ElevationTrails.gdb\Elevation_trails'
    routes_table = 'C:\GisWork\Trails\ElevationTrails.gdb\TrailRoutes'
    surface = r'C:\GisWork\Trails\ProfileTest.gdb\DEM_10METER'
    # line = None
    # where = None
    # with arcpy.da.SearchCursor(trails, 'SHAPE@', where_clause=where) as cursor:
    #     line = cursor.next()[0]
    start = clock()
    route_segments = union_segments(trails, routes_table)
    route_profiles = {}
    output_file = 'data/csvs/elevation_profiles.json'
    for route in route_segments:
        line = route_segments[route]
        route_profiles[route] = get_z_distances(line, surface)

    with open(output_file, 'w') as f_out:
        f_out.write(json.dumps(route_profiles, sort_keys=True, indent=4))
    print 'Time', clock() - start
