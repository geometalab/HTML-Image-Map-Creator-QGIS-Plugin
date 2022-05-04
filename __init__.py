from html_image_map_creator_plugin import HTMLImageMapCreatorPlugin

def name():
    return "HTML Image Map Creator"

def description():
    return "This plugin creates a static image map (HTML5/CSS/JavaScript) with interactive features"

def qgisMinimumVersion():
    return "3.0.0"

def version():
    return "1.1"

def author():
    return "geometalab"

def email():
    return "geometalab@gmail.com"

def category():
  return "Web"

def classFactory(iface):
    return HTMLImageMapCreatorPlugin(iface)

