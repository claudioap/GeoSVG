import gi

gi.require_version('Champlain', '0.12')
gi.require_version('GtkClutter', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GtkChamplain', '0.12')
from gi.repository import GtkClutter, Gtk, Champlain, Clutter, GdkPixbuf

GtkClutter.init([])  # Must be initialized before importing those:
from gi.repository import GObject, Gtk, Champlain, GtkChamplain, Pango


class UserInterface:
    def __init__(self, controller):
        self.controller = controller

        GObject.threads_init()

        # Glade
        builder = Gtk.Builder()
        builder.add_from_file("GeoSVG.glade")
        self.window = builder.get_object("window")
        boxes = builder.get_object("boxes")
        open_btn = builder.get_object("open_btn")
        self.preview = builder.get_object("preview")
        self.layers_tree = builder.get_object("layers_tree")
        self.lim_north = builder.get_object("lim_north")
        self.lim_south = builder.get_object("lim_south")
        self.lim_east = builder.get_object("lim_east")
        self.lim_west = builder.get_object("lim_west")
        self.rotation = builder.get_object("rotation")
        self.output = builder.get_object("output")
        self.last_click = builder.get_object("last_click")
        replace_north_lim = builder.get_object("replace_north_lim")
        replace_south_lim = builder.get_object("replace_south_lim")
        replace_east_lim = builder.get_object("replace_east_lim")
        replace_west_lim = builder.get_object("replace_west_lim")

        # Map
        embed = GtkChamplain.Embed()
        self.map_view = embed.get_view()
        self.map_view.set_reactive(True)
        self.map_view.set_property('kinetic-mode', True)
        self.map_view.set_property('zoom-level', 16)
        scale = Champlain.Scale()
        scale.connect_view(self.map_view)
        self.map_view.bin_layout_add(scale, Clutter.BinAlignment.START, Clutter.BinAlignment.END)
        self.map_view.center_on(38.66, -9.20523)
        boxes.add(embed)

        # Layers pane
        self.layers_liststore = Gtk.ListStore(str, bool)
        self.layers_tree.set_model(self.layers_liststore)
        column_text = Gtk.TreeViewColumn("Name", Gtk.CellRendererText(), text=0)
        self.layers_tree.append_column(column_text)
        renderer_toggle = Gtk.CellRendererToggle()
        column_toggle = Gtk.TreeViewColumn("Enable", renderer_toggle, active=1)
        self.layers_tree.append_column(column_toggle)

        self.window.show_all()

        # Events
        renderer_toggle.connect("toggled", self.__on_layer_toggled)
        self.window.connect("destroy", Gtk.main_quit)
        open_btn.connect('clicked', self.open_file)
        self.lim_north.connect('changed', self.__update_north_lim)
        self.lim_south.connect('changed', self.__update_south_lim)
        self.lim_east.connect('changed', self.__update_east_lim)
        self.lim_west.connect('changed', self.__update_west_lim)
        self.rotation.connect('changed', lambda w: self.controller.update_rotation(w.get_value()))
        self.map_view.connect('button-release-event', self.__on_map_mouse_click, self.map_view)
        replace_north_lim.connect('clicked', lambda _: self.controller.replace_lim('N'))
        replace_south_lim.connect('clicked', lambda _: self.controller.replace_lim('S'))
        replace_east_lim.connect('clicked', lambda _: self.controller.replace_lim('E'))
        replace_west_lim.connect('clicked', lambda _: self.controller.replace_lim('W'))

        # Drawn layers
        self.layers = []

    def run(self):
        Gtk.main()

    # Event Handlers
    def open_file(self, _):
        dialog = Gtk.FileChooserDialog("Choose SVG file", self.window, Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_svg = Gtk.FileFilter()
        filter_svg.set_name("SVG files")
        filter_svg.add_mime_type("image/svg+xml")
        dialog.add_filter(filter_svg)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.controller.load_svg(dialog.get_filename())
        dialog.destroy()

    # TODO validate N>S, E>W
    def __update_north_lim(self, widget):
        val = widget.get_value()
        self.controller.update_boundaries('N', val, update_ui=False)

    def __update_south_lim(self, widget):
        val = widget.get_value()
        self.controller.update_boundaries('S', val, update_ui=False)

    def __update_east_lim(self, widget):
        val = widget.get_value()
        self.controller.update_boundaries('E', val, update_ui=False)

    def __update_west_lim(self, widget):
        val = widget.get_value()
        self.controller.update_boundaries('W', val, update_ui=False)

    def __on_layer_toggled(self, _, index):
        self.layers_liststore[index][1] = not self.layers_liststore[index][1]
        self.controller.set_layer_output(self.layers_liststore[index][0], self.layers_liststore[index][1])

    def __on_map_mouse_click(self, _, event, view):
        x, y = event.x, event.y
        self.controller.record_click(view.x_to_longitude(x), view.y_to_latitude(y))
        return True

    # Action methods
    def load_layers(self, layers):
        self.layers_liststore.clear()
        for layer in layers:
            self.layers_liststore.append([layer, True])

    def load_preview(self, path):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=path,
            width=256,
            height=256,
            preserve_aspect_ratio=True)
        self.preview.set_from_pixbuf(pixbuf)

    def set_output(self, value):
        textbuffer = self.output.get_buffer()
        textbuffer.set_text(value)

    def set_last_click(self, lon, lat):
        self.last_click.set_text(f'Lon: {lon}\nLat: {lat}')

    def draw_polygons(self, polygons):
        for layer in self.layers:
            self.map_view.remove_layer(layer)
        self.layers.clear()
        for polygon in polygons:
            polygon_layer = Champlain.PathLayer()
            for point in polygon:
                lat, lon = point
                coord = Champlain.Coordinate.new_full(lon, lat)
                polygon_layer.add_node(coord)
            self.map_view.add_layer(polygon_layer)
            self.layers.append(polygon_layer)

    def set_boundaries(self, boundaries):
        n, s, e, w = boundaries
        if self.lim_north.get_value() != n:
            self.lim_north.set_value(n)

        if self.lim_south.get_value() != s:
            self.lim_south.set_value(s)

        if self.lim_east.get_value() != e:
            self.lim_east.set_value(e)

        if self.lim_west.get_value() != w:
            self.lim_west.set_value(w)
