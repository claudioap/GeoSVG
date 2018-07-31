import re

import gi

from SVGParser import SVG

gi.require_version('Champlain', '0.12')
gi.require_version('GtkClutter', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GtkChamplain', '0.12')
from gi.repository import GtkClutter, Gtk, Champlain, Clutter, GdkPixbuf

GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import GObject, Gtk, Champlain, GtkChamplain, Pango
from bs4 import BeautifulSoup, NavigableString, Tag


class Controller:
    def __init__(self):
        self.window, self.map_view, self.preview, self.layers_tree, self.svg_bounding_top, self.svg_bounding_bottom, \
        self.svg_bounding_left, self.svg_bounding_right = None, None, None, None, None, None, None, None
        self.initialize_ui()
        # -----------------

        self.layers = {}
        self.bounding = (0.0, 0.0, 0.0, 0.0)

    def initialize_ui(self):
        builder = Gtk.Builder()
        builder.add_from_file("GeoSVG.glade")

        self.window = builder.get_object("window")
        boxes = builder.get_object("boxes")
        open_btn = builder.get_object("open_btn")
        self.preview = builder.get_object("preview")
        self.layers_tree = builder.get_object("layers_tree")
        self.svg_bounding_top = builder.get_object("b_top")
        self.svg_bounding_bottom = builder.get_object("b_bottom")
        self.svg_bounding_left = builder.get_object("b_left")
        self.svg_bounding_right = builder.get_object("b_right")

        # Map
        embed = GtkChamplain.Embed()
        self.map_view = embed.get_view()
        self.map_view.set_reactive(True)
        self.map_view.set_property('kinetic-mode', True)
        self.map_view.set_property('zoom-level', 12)
        scale = Champlain.Scale()
        scale.connect_view(self.map_view)
        self.map_view.bin_layout_add(scale, Clutter.BinAlignment.START, Clutter.BinAlignment.END)
        self.map_view.center_on(38.5775474, -9.1254975)
        boxes.add(embed)

        # Layers pane
        self.layers_liststore = Gtk.ListStore(str, bool)
        self.layers_tree.set_model(self.layers_liststore)
        column_text = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
        self.layers_tree.append_column(column_text)
        # renderer_toggle.connect("toggled", self.on_cell_toggled)
        column_toggle = Gtk.TreeViewColumn("Enable", Gtk.CellRendererToggle(), active=1)
        self.layers_tree.append_column(column_toggle)

        self.window.show_all()

        # Events
        self.window.connect("destroy", Gtk.main_quit)
        open_btn.connect('clicked', self.open_file)

    def open_file(self, widget):
        dialog = Gtk.FileChooserDialog("Choose SVG file", self.window, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_svg = Gtk.FileFilter()
        filter_svg.set_name("SVG files")
        filter_svg.add_mime_type("image/svg+xml")
        dialog.add_filter(filter_svg)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            with open(path) as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                svg_root = soup.find('svg')
                svg_layers = []
                for element in list(svg_root.children):
                    if not isinstance(element, Tag):
                        continue
                    if element.name == 'g':
                        svg_layers.append(element)

            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=path,
                width=256,
                height=256,
                preserve_aspect_ratio=True)
            self.preview.set_from_pixbuf(pixbuf)
            self.load_layers(svg_layers)

        dialog.destroy()

    def load_layers(self, svg_layers):
        coord_ext = re.compile('(-?[\d]+\.[\d]*),(-?[\d]+\.[\d]*)')
        layers = {}
        top, bottom, left, right = 0.0, 0.0, 0.0, 0.0
        for layer in svg_layers:
            objects = {}
            for path in layer.find_all('path'):
                coord_pairs = []
                for coordinate in coord_ext.findall(path.attrs['d']):
                    x = float(coordinate[0])
                    y = float(coordinate[1])
                    if x < left:
                        left = x
                    if x > right:
                        right = x
                    if y < top:
                        top = y
                    if y > bottom:
                        bottom = y
                    coord_pairs.append((x, y))
                objects[path.attrs['id']] = coord_pairs
            layers[layer.attrs['id']] = objects
        self.layers = layers
        for key in layers.keys():
            self.layers_liststore.append([key, True])
        self.bounding = (top, bottom, left, right)
        self.svg_bounding_top.set_text(str(top))
        self.svg_bounding_bottom.set_text(str(bottom))
        self.svg_bounding_left.set_text(str(left))
        self.svg_bounding_right.set_text(str(right))


if __name__ == "__main__":
    GObject.threads_init()
    MapView()
    Gtk.main()