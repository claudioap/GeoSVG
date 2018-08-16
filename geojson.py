import json

import numpy as np


class GeoJSON:
    def __init__(self, svg):
        self.svg = svg
        self.feature_collections = {}
        self.polygons = []

    def calculate(self, layers: [str], map_bounding: (float, float, float, float), rotation: float) -> str:
        i_bot, i_top, i_left, i_right = self.svg.get_bounding_box()  # Top and bottom swapped due to SVG coord system
        i_width = i_right - i_left
        i_height = i_top - i_bot

        f_top, f_bot, f_left, f_right = map_bounding
        f_width = f_right - f_left
        f_height = f_top - f_bot

        theta = np.radians(rotation+180)

        center_translation_matrix = np.matrix(('1 0 {x};'
                                               '0 1 {y};'
                                               '0 0  1')
                                              .format(x=-(i_left + i_right) / 2, y=-(i_top + i_bot) / 2))

        rotation_matrix = np.matrix(('{cos} -{sin}  0;'
                                     '{sin}  {cos}  0;'
                                     '  0      0    1')
                                    .format(cos=np.cos(theta), sin=np.sin(theta)))

        scaling_matrix = np.matrix(('{x_scale}  0      0;'
                                    '0      {y_scale}  0;'
                                    '0,         0,     1')
                                   .format(x_scale=f_width / i_width, y_scale=f_height / i_height))

        final_translation_matrix = np.matrix(('1 0 {x};'
                                              '0 1 {y};'
                                              '0 0  1')
                                             .format(x=(f_left + f_right) / 2, y=(f_top + f_bot) / 2))

        transformation_matrix = final_translation_matrix * scaling_matrix * rotation_matrix * center_translation_matrix

        del i_bot, i_top, i_left, i_right, i_width, i_height, f_top, f_bot, f_left, f_right, f_width, f_height, theta
        del center_translation_matrix, rotation_matrix, scaling_matrix, final_translation_matrix

        feature_collections = []
        self.polygons.clear()
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
