from svg import SVG
from ui import UserInterface


class Controller:
    def __init__(self):
        self.ui = UserInterface(self)
        self.svg = None
        self.ui.run()
        self.layer_output = {}

    def load_svg(self, path):
        with open(path) as file:
            self.svg = SVG(file.read())
            print(self.svg.get_layers())

        self.ui.load_preview(path)
        layers = self.svg.get_layers()
        self.ui.load_layers(layers)
        for layer in layers:
            self.layer_output[layer] = True

    def set_layer_output(self, layer: str, value: bool):
        self.layer_output[layer] = value


if __name__ == "__main__":
    Controller()
