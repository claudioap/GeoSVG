import json

import numpy as np


class GeoJSON:
    def __init__(self, svg):
        self.svg = svg
        self.feature_collections = {}
        self.polygons = []

    def calculate(self, layers: [str], map_bounding: (float, float, float, float), rotation: float) -> str:
        top, bottom, left, right = self.svg.get_bounding_box()
        width = right - left
        height = bottom - top

        theta = np.radians(rotation)
        scaling_matrix = np.matrix(f'{1/width}     0      0;'
                                   f'0         {1/height} 0;'
                                   ' 0,            0,     1')
        rotation_matrix = np.matrix(('{cos} -{sin}  0;'
                                     '{sin}  {cos}  0;'
                                     '  0      0    1').format(cos=np.cos(theta), sin=np.sin(theta)))
        translation_matrix = np.matrix(f'1 0 {(top-bottom)/2-bottom};'
                                       f'0 1 {(right-left)/2 -left};'
                                       ' 0 0 1')
        transformation_matrix = scaling_matrix * rotation_matrix * translation_matrix

        top, bottom, left, right = map_bounding
        center = (right - left) / 2, (top - bottom) / 2
        x_scale = right - left
        y_scale = bottom - top
        del top, bottom, left, right

        feature_collections = []
        for layer in layers:
            paths = self.svg.get_paths_as_polygons(layer)
            feature_collection = {'type': 'FeatureCollection', 'features': [], 'properties': [{'id': layer}]}
            for name, path in paths.items():
                coordinates = []
                for polygon in path:
                    poly_coordinates = []
                    for point in polygon:
                        vector = np.matrix((*point, 1)).transpose()
                        result = (transformation_matrix * vector).transpose()[0, :2].tolist()[0]
                        result = result[0] + center[0], result[1] + center[0]
                        poly_coordinates.append(result)
                    self.polygons.append(poly_coordinates)
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
        return json.dumps(feature_collections, indent=2)