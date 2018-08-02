from svg import SVG
from ui import UserInterface
from geojson import GeoJSON


class Controller:
    def __init__(self):
        self.ui = UserInterface(self)
        self.svg = None
        self.geojson = None
        self.layer_output = []
        self.ui.run()

    def load_svg(self, path):
        with open(path) as file:
            svg = SVG(file.read())
            self.svg = svg
            self.geojson = GeoJSON(self.svg)
            self.layer_output = list(self.svg.get_layers())

        self.ui.load_preview(path)
        layers = self.svg.get_layers()
        self.ui.load_layers(layers)

    def set_layer_output(self, layer: str, enable: bool):
        if enable:
            self.layer_output.append(layer)
        else:
            self.layer_output.remove(layer)

        self.geojson.calculate(self.layer_output, (0.0, 1.0, 0.0, 1.0), 0.0)


if __name__ == "__main__":
    Controller()
