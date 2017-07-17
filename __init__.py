from html_image_map_creator_plugin import HTMLImageMapCreatorPlugin

def name():
    return "HTML Image Map Creator"

def description():
    return "This plugin generates a HTML image map from the active point or polygon layer"

def qgisMinimumVersion():
    return "2.14.16"

def version():
    return "0.4"

def author():
    return "geometalab"

def email():
    return "geometalab@gmail.com"

def category():
  return "Web"

def classFactory(iface):
    return HTMLImageMapCreatorPlugin(iface)

