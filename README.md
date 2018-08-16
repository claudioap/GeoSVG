# GeoSVG
GeoSVG is a simple GUI to help with mapping SVG on top of a geographic map.
You push some vector onto it, mess with a few boxes and get GeoJSON without any sweat.

There are a few other tools to do this, but they all kinda suck, and the majority are browser based with quite some limitations.
This is a standalone desktop app, and with a few easy tweaks you can throw the GUI away and automate it.

![Converter](https://gitlab.com/claudiop/GeoSVG/raw/master/screenshot.png)

## Requirements

This is python based, I think that python 3.6+ will do just fine.
If you edit the code and throw away stuff such as f-strings it is probably safe to go down a few versions.
You'll need the following libraries:
> beautifulsoup4, numpy

In case you run it as it is, GUI included, you'll also need:
> gtk, libchamplain, libglade (in case gtk doesn't bundle it)

## Considerations
Both standard and Inkscape's SVG is fine.
Everything has to be a `path`. Other elements are discarded.
Only polygons made of straight lines are supported, curves are flattened.
Lucky you, Inkscape easily turns everything into paths.

Ratios aren't preserved.
It is up to you to insert proper coordinates, and/or click on the correct places.

Rotation support isn't properly baked in, bounds aren't properly considered when a polygon is rotated.
A few algorithm tweaks are needed.
You can manually adjust rotated stuff.
In case you need precision rotate the SVG itself.
Once again, Inkscape excels with that kinda stuff.

Anything with a translation attached to it will mess up with the output.
Ideally you'd have no groups. Layers might or might not work.
In case you have translations messing up with your stuff please buy [this guy](https://github.com/Klowner/inkscape-applytransforms) a coffee.

MultiPolygons are buggy as hell, and cropped polygons are read as MultiPolygons. Their coordinates are fine, it's just the array hierarchy that isn't correct. A few brackets here and there and it's all good.

There's some weird bug with the boundary fields if you want to manually insert coordinates.
Try to position with the mouse and insert the correct coordinates after it.

Sometimes part of the figure is not drawn. Worry not, the json output is good.
Adjusting the positioning back and forth will sometimes make it draw properly.
I'm not even sure that bug is mine or some issue with libchamplain's/clutter's drawer.

While these remaining bugs aren't nice, all of them have workarounds.
This tool has already served the purpose I had for it, I'll probably leave them unsolved until someone complains.
Pull requests accepted.