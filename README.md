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
Both standard and inkscape's SVG is fine.
Everything has to be a `path`. Other elements are discarded.
Only polygons made of straight lines are supported.
Lucky you, inkscape easily turns everything into paths.

Ratios aren't preserved.
It is up to you to insert proper coordinates, and/or click on the correct places.

Rotation support isn't properly baked in, and bounds aren't considered.
A few algorithm tweaks are needed.
You can manually adjust rotated stuff.
In case you need precision rotate the SVG itself.
Once again, Inkscape excels with that kinda stuff.