"""
/***************************************************************************
ImageMapPlugin

This plugin generates a HTML image map file+img from the active point 
or polygon layer

An adaptation of "imagemapplugin" by Richard Duivenvoorde.

copyright            : (C) 2017 by Emil Sivro and Severin Fritschi
email                : emil.sivro@hsr.ch | severin.fritschi@hsr.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from imagemapplugin import ImageMapPlugin

def name():
    return "HTML Image Map Creator"

def description():
    return "This plugin generates a HTML image map from the active point or polygon layer"

def qgisMinimumVersion():
    return "2.0"

def version():
    return "2.0.1"

def author():
    return "Emil Sivro & Severin Fritschi"

def email():
    return "emil.sivro@hsr.ch | severin.fritschi@hsr.ch"

def category():
  return "Web"

def classFactory(iface):
    return ImageMapPlugin(iface)

