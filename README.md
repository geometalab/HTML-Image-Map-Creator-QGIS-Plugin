# HTML Image Map Creator QGIS-Plugin

Download the zip file of this repo, unpack it into this directory "%userprofile%/.qgis2/python/plugins" 
using the plugin folder name "html_image_map_creator". 

Copy all files from the "src" directory into the main directory of the plugin. Otherwise QGIS won't be able to detect them.
Open "OSGeo4W Shell", change to the directory of the plugin and enter this command: pyrcc4 -o resources_rc.py resources.qrc

Following this, you can (re)start QGIS. Make sure that the plugin "html_image_map_creator" is listed and activated.
Now you can run the plugin from the menu "Web > HTML Image Map Creator > Create HTML Image Map".
