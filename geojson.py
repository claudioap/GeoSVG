import json


class GeoJSON:
    def __init__(self, svg):
        self.svg = svg
        self.feature_collections = {}

    def calculate(self, layers: [str], map_bounding: (float, float, float, float), rotation: float) -> str:
        top, bottom, left, right = self.svg.get_bounding_box()
        feature_collections = []
        for layer in layers:
            paths = self.svg.get_paths_as_polygons(layer)
            feature_collection = {'type': 'FeatureCollection', 'features': [], 'properties': [{'id': layer}]}
            for name, path in paths.items():
                coordinates = []
                for polygon in path:
                    poly_coordinates = []
                    for point in polygon:
                        poly_coordinates.append([*point])
                    coordinates.append(poly_coordinates)

                polygon_count = len(path)
                if polygon_count > 1:
                    feature = {'type': 'Feature',
                               'properties': {'name': name},
                               'geometry':
                                   {'type': 'MultiPolygon',
                                    'coordinates': coordinates}}
                elif polygon_count == 1:
                    feature = {'type': 'Feature',
                               'properties': {'name': name},
                               'geometry':
                                   {'type': 'Polygon',
                                    'coordinates': coordinates}}
                else:
                    raise Exception("Found a path without polygons")

                feature_collection['features'].append(feature)
            feature_collections.append(feature_collection)
        return json.dumps(feature_collections)
