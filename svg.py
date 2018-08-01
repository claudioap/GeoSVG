import re

from bs4 import BeautifulSoup, Tag


class SVG:
    def __init__(self, source):
        self.source = BeautifulSoup(source, 'html.parser')
        self.root = self.source.find('svg')
        self.layers = {}
        self.bounding = None
        for element in list(self.root.children):
            if not isinstance(element, Tag):
                continue
            if element.name == 'g':
                self.layers[element.attrs['id']] = element

    def get_layers(self) -> [str]:
        return self.layers.keys()

    def get_paths_as_polygons(self, layer: str = None):
        layers = self.layers.values() if layer is None else (self.layers[layer],)

        result = {}
        for layer in layers:
            paths = {}
            for path in layer.find_all('path'):
                paths[path.attrs['id']] = self.parse_path_data(path.attrs['d'])
            result[layer.attrs['id']] = paths
        return result

    def _calc_bounding_box(self):
        top, bottom, left, right = float("-inf"), float("inf"), float("inf"), float("-inf")
        for layer in self.layers.keys():
            paths = self.get_paths_as_polygons(layer)
            for path in paths.values():
                for point in path:
                    x, y = point
                    if x < left:
                        left = x
                    elif x > right:
                        right = x

                    if y > top:
                        top = y
                    elif y < bottom:
                        bottom = y
        self.bounding = top, bottom, left, right

    def get_bounding_box(self):
        if self.bounding is None:
            self._calc_bounding_box()

        return self.bounding

    @staticmethod
    def parse_path_data(d: str) -> [[(float, float)]]:
        """
        Guetto parser, not even sure that it totally conforms to the spec, just barely good enough for what it does.
        :param d: SVG path d attribute
        :return: List of sections, with each section being a disjoint list of points.
        """
        print(d)
        if d[0].lower() != 'm':
            raise Exception("Path start command not present")

        if d[-1].lower() != 'z':
            raise Exception("Path end command not present")

        sections = []
        section = []

        current_position = 0.0, 0.0

        coord_exp = re.compile('([-e\d.]+)(?: |,)')
        coordinates = coord_exp.findall(d)
        coordinate_index = 0

        skips = 0

        new_number = True
        for char in d:
            if skips > 0:
                skips -= 1
                continue

            if char == ' ':
                new_number = True
                continue

            elif char.isnumeric():
                if not new_number:
                    continue
                section.append(current_position)
                x = coordinates[coordinate_index]
                y = coordinates[coordinate_index + 1]
                coordinate_index += 2
                skips = len(x) + len(y) + 1
                current_position = float(x), float(y)
                new_number = False

            elif char == ',':
                raise Exception("Invalid path data string")
            elif char.isalpha():
                new_number = True
                if char == 'M':
                    x = coordinates[coordinate_index]
                    y = coordinates[coordinate_index + 1]
                    coordinate_index += 2
                    skips = len(x) + len(y) + 1
                    current_position = float(x), float(y)
                    if section:
                        sections.append(section)
                    sections = []
                elif char == 'L':
                    section.append(current_position)
                    x = coordinates[coordinate_index]
                    y = coordinates[coordinate_index + 1]
                    coordinate_index += 2
                    skips = len(x) + len(y) + 1
                    current_position = float(x), float(y)
                elif char == 'H':
                    section.append(current_position)
                    x = coordinates[coordinate_index]
                    coordinate_index += 1
                    skips = len(x) + 1
                    current_position = float(x), current_position[1]
                elif char == 'V':
                    section.append(current_position)
                    y = coordinates[coordinate_index]
                    coordinate_index += 1
                    skips = len(y) + 1
                    current_position = current_position[0], float(y)
                elif char == 'l':
                    section.append(current_position)
                    x = coordinates[coordinate_index]
                    y = coordinates[coordinate_index + 1]
                    coordinate_index += 2
                    skips = len(x) + len(y) + 1
                    current_position = current_position[0] + float(x), current_position[1] + float(y)
                elif char == 'h':
                    section.append(current_position)
                    x = coordinates[coordinate_index]
                    coordinate_index += 1
                    skips = len(x) + 1
                    current_position = current_position[0] + float(x), current_position[1]
                elif char == 'v':
                    section.append(current_position)
                    y = coordinates[coordinate_index]
                    coordinate_index += 1
                    skips = len(y) + 1
                    current_position = current_position[0], current_position[1] + float(y)
                elif char in ('z', 'Z'):
                    section.append(current_position)
                    if section:
                        sections.append(section)
                    section = []
                else:
                    raise Exception("Sting has unimplemented commands. Data: " + d)
