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


if __name__ == '__main__':
    pass
