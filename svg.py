import re
from typing import Dict

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

    def get_paths_as_polygons(self, layer: str) -> Dict[str, any]:
        paths = {}
        layer = self.layers[layer]
        for path in layer.find_all('path'):
            paths[path.attrs['id']] = self.parse_path_data(path.attrs['d'])
        return paths

    def _calc_bounding_box(self):
        top, bottom, left, right = float("inf"), float("-inf"), float("inf"), float("-inf")
        for layer in self.layers.keys():
            paths = self.get_paths_as_polygons(layer)
            for path in paths.values():
                for section in path:
                    for point in section:
                        x, y = point
                        if x < left:
                            left = x
                        elif x > right:
                            right = x

                        if y < top:
                            top = y
                        elif y > bottom:
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
        if d[0].lower() != 'm':
            raise Exception("Path start command not present")

        sections = []
        section = []

        current_position = 0.0, 0.0

        command_exp = re.compile('(?P<command>[MmLlHhVvZzc])(?P<argument>[-e.,\d ]+)')
        coord_exp = re.compile('([-e\d.]+)[ ,]?')
        commands = command_exp.findall(d)

        for command in commands:
            command, arguments = command
            coordinates = coord_exp.findall(arguments)
            coordinate_count = len(coordinates)

            if command == 'M':
                if coordinate_count < 2:
                    raise MissingPathArgument(d, command)
                if coordinate_count % 2 != 0:
                    raise InvalidPath(d, 'M command with odd number of coordinates')
                if section:
                    sections.append(section)
                sections = []

                current_position = float(coordinates[0]), float(coordinates[1])
                additional = coordinates[2:]
                odd = False
                for index, _ in enumerate(additional):
                    if odd:
                        odd = False
                        continue
                    section.append(current_position)
                    current_position = float(additional[index]), float(additional[index + 1])

                    odd = True
            elif command == 'm':
                if coordinate_count < 2:
                    raise MissingPathArgument(d, command)
                if coordinate_count % 2 != 0:
                    raise InvalidPath(d, 'M command with odd number of coordinates')
                if section:
                    sections.append(section)
                sections = []

                new_x = current_position[0] + float(coordinates[0])
                new_y = current_position[1] + float(coordinates[1])
                current_position = new_x, new_y
                additional = coordinates[2:]
                odd = False
                for index, _ in enumerate(additional):
                    if odd:
                        odd = False
                        continue
                    section.append(current_position)
                    new_x = current_position[0] + float(additional[index])
                    new_y = current_position[1] + float(additional[index + 1])
                    current_position = new_x, new_y
                    odd = True
            elif command == 'l':
                if coordinate_count < 2:
                    raise MissingPathArgument(d, command)

                if coordinate_count % 2 != 0:
                    raise InvalidPath(d, 'l command with odd number of coordinates')

                section.append(current_position)
                new_x = current_position[0] + float(coordinates[0])
                new_y = current_position[1] + float(coordinates[1])
                current_position = new_x, new_y
                additional = coordinates[2:]
                odd = False
                for index, _ in enumerate(additional):
                    if odd:
                        odd = False
                        continue
                    section.append(current_position)
                    new_x = current_position[0] + float(additional[index])
                    new_y = current_position[1] + float(additional[index + 1])
                    current_position = new_x, new_y
                    odd = True
            elif command == 'L':
                if coordinate_count < 2:
                    raise MissingPathArgument(d, command)
                if coordinate_count % 2 != 0:
                    raise InvalidPath(d, 'L command with odd number of coordinates')

                section.append(current_position)
                new_x = float(coordinates[0])
                new_y = float(coordinates[1])
                current_position = new_x, new_y
                additional = coordinates[2:]
                odd = False
                for index, _ in enumerate(additional):
                    if odd:
                        odd = False
                        continue
                    section.append(current_position)
                    new_x = float(additional[index])
                    new_y = float(additional[index + 1])
                    current_position = new_x, new_y
                    odd = True
            elif command == 'H':
                if coordinate_count < 1:
                    raise MissingPathArgument(d, command)

                section.append(current_position)
                current_position = float(coordinates[-1]), current_position[1]
            elif command == 'h':
                if coordinate_count < 1:
                    raise MissingPathArgument(d, command)

                section.append(current_position)
                horizontal_distance = 0.0
                for coordinate in coordinates:
                    horizontal_distance += float(coordinate)
                current_position = current_position[0] + horizontal_distance, current_position[1]
            elif command == 'V':
                if coordinate_count < 1:
                    raise MissingPathArgument(d, command)

                section.append(current_position)
                current_position = current_position[0], float(coordinates[-1])
            elif command == 'v':
                if coordinate_count < 1:
                    raise MissingPathArgument(d, command)

                section.append(current_position)
                horizontal_distance = 0.0
                for coordinate in coordinates:
                    horizontal_distance += float(coordinate)
                current_position = current_position[0], current_position[1] + horizontal_distance
            elif command in ('z', 'Z'):
                section.append(current_position)
                section.append(section[0])
                if section:
                    sections.append(section)
                section = []
            elif command == 'c':  # Not compliant, just flattens the curve
                if coordinate_count < 6:
                    raise MissingPathArgument(d, command)
                if coordinate_count % 6 != 0:
                    raise InvalidPath(d, 'c command with wrong number of coordinates')
                if section:
                    sections.append(section)
                for index, _ in enumerate(coordinates):
                    if index % 6 != 0:
                        continue
                    section.append(current_position)
                    new_x = current_position[0] + float(coordinates[index + 4])
                    new_y = current_position[1] + float(coordinates[index + 5])
                    current_position = new_x, new_y
            else:
                raise InvalidPath(d, "Sting has unimplemented commands: " + command)

        # Close last section
        section.append(current_position)
        if current_position != section[0]:
            section.append(section[0])
        sections.append(section)

        return sections


class InvalidPath(Exception):
    def __init__(self, d, description):
        super().__init__(f'Unable to parse a path with the following data: {d}\n Cause: {description}')


class MissingPathArgument(InvalidPath):
    def __init__(self, d, command):
        super().__init__(d, f'{command} command without argument')
