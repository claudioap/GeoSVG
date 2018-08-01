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
        renderer_toggle = Gtk.CellRendererToggle()
        column_toggle = Gtk.TreeViewColumn("Enable", renderer_toggle, active=1)
        self.layers_tree.append_column(column_toggle)

        self.window.show_all()

        # Events
        renderer_toggle.connect("toggled", self.on_cell_toggled)
        self.window.connect("destroy", Gtk.main_quit)
        open_btn.connect('clicked', self.open_file)

    def run(self):
        Gtk.main()

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

    def load_preview(self, path):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=path,
            width=256,
            height=256,
            preserve_aspect_ratio=True)
        self.preview.set_from_pixbuf(pixbuf)

    def load_layers(self, layers):
        self.layers_liststore.clear()
        for layer in layers:
            self.layers_liststore.append([layer, True])

    def on_cell_toggled(self, widget, index):
        self.layers_liststore[index][1] = not self.layers_liststore[index][1]
        self.controller.set_layer_output(self.layers_liststore[index][0], self.layers_liststore[index][1])
