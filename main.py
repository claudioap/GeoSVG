from svg import SVG
from ui import UserInterface


class Controller:
    def __init__(self):
        self.ui = UserInterface(self)
        self.svg = None
        self.ui.run()

    def load_svg(self, path):
        with open(path) as file:
            self.svg = SVG(file.read())
            print(self.svg.get_layers())

        self.ui.load_preview(path)


if __name__ == "__main__":
    Controller()
