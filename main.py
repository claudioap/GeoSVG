from svg import SVG
from ui import UserInterface
from geojson import GeoJSON


class Controller:
    def __init__(self):
        self.ui = UserInterface(self)
        self.svg = None
        self.geojson = None
        self.layer_output = []
        self.bounds = [0.0, 0.0, 0.0, 0.0]
        self.rotation = 0.0
        self.last_click = None
        self.ui.run()

    def load_svg(self, path):
        with open(path) as file:
            svg = SVG(file.read())
            self.svg = svg
            self.geojson = GeoJSON(self.svg)
            self.layer_output = list(self.svg.get_layers())
            self.update_result()

        self.ui.load_preview(path)
        layers = self.svg.get_layers()
        self.ui.load_layers(layers)

    def set_layer_output(self, layer: str, enable: bool):
        if enable:
            self.layer_output.append(layer)
        else:
            self.layer_output.remove(layer)

    def update_bound(self, direction: chr, value):
        if direction == 'N':
            self.bounds[0] = value
        elif direction == 'S':
            self.bounds[1] = value
        elif direction == 'E':
            self.bounds[2] = value
        elif direction == 'W':
            self.bounds[3] = value

        self.ui.set_boundaries(self.bounds)
        self.update_result()

    def update_rotation(self, rotation):
        self.rotation = rotation
        self.update_result()

    def update_result(self):
        print(f'Updating to match the bounds {self.bounds} with {self.rotation}º of rotation.')
        geojson = self.geojson.calculate(self.layer_output, self.bounds, self.rotation)
        self.ui.set_output(geojson)
        self.ui.draw_polygons(self.geojson.polygons)

    def record_click(self, lon: float, lat: float):
        self.last_click = lon, lat
        self.ui.set_last_click(lon, lat)

    def replace_lim(self, direction: chr):
        if direction in ('N', 'S'):
            self.update_bound(direction, self.last_click[1])
        else:
            self.update_bound(direction, self.last_click[0])


if __name__ == "__main__":
    Controller()
