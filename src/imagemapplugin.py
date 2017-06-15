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
"""
import os
import platform

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from imagemapplugingui import ImageMapPluginGui

# Initialize Qt resources from file
import imagemapplugin_rc
from shutil import copyfile

class ImageMapPlugin:

  MSG_BOX_TITLE = "QGIS HTML Image Map Creator "

  def __init__(self, iface):
    # Save reference to the QGIS interface and initialize instance variables
    self.iface = iface
    self.filesPath = "/tmp/foo"
    self.attrFields = []
    self.layerName = ""
    self.dimensions = ""
    self.iconFilePath = "/foo/bar.svg"
    self.labels = []
    self.infoBoxes = []
    self.index = 0
    self.featureCount = 0

  def initGui(self):
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/imagemapicon.xpm"), "Create HTML image map...", self.iface.mainWindow())
    self.action.setWhatsThis("Configuration for Image Map Creator")
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)
    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    if hasattr ( self.iface, "addPluginToWebMenu" ):
        self.iface.addPluginToWebMenu("&HTML Image Map Creator", self.action)
    else:
        self.iface.addPluginToMenu("&HTML Image Map Creator", self.action)

    #self.iface.pluginMenu().insertAction(self.action)
    # connect to signal renderComplete which is emitted when canvas rendering is done
    QObject.connect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)

  def unload(self):
    # remove the plugin menu item and icon
    if hasattr ( self.iface, "addPluginToWebMenu" ):
        self.iface.removePluginWebMenu("&HTML Image Map Creator",self.action)
    else:
        self.iface.removePluginMenu("&HTML Image Map Creator",self.action)
    self.iface.removeToolBarIcon(self.action)
    # disconnect form signal of the canvas
    QObject.disconnect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)

  def run(self):
    # check if current active layer is a polygon layer:
    layer =  self.iface.activeLayer()
    if layer == None:
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("No active layer found\n" "Please select a (multi) polygon or point layer first, \n" "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
        return
    # don't know if this is possible / needed
    if not layer.isValid():
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("No VALID layer found\n" "Please select a valid (multi) polygon or point layer first, \n" "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
        return
    if (layer.type()>0): # 0 = vector, 1 = raster
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Wrong layer type, only vector layers may be used...\n" "Please select a vector layer first, \n" "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
        return
    self.provider = layer.dataProvider()
    if not(self.provider.geometryType() == QGis.WKBPolygon or self.provider.geometryType() == QGis.WKBMultiPolygon or self.provider.geometryType() == QGis.WKBPoint):
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Wrong geometry type, only (multi) polygons and points may be used.\n" "Please select a (multi) polygon or point layer first, \n" "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
        return

    # we need the fields of the active layer to show in the attribute combobox in the gui:
    self.attrFields = []
    fields = self.provider.fields()
    if hasattr(fields, 'iteritems'):
        for (i, field) in fields.iteritems():
            self.attrFields.append(field.name().trimmed())
    else:
        for field in self.provider.fields():
            self.attrFields.append(field.name().strip())
    for i in range(layer.fields().count()):
        if layer.fields().fieldOrigin(i) == QgsFields.OriginExpression:
            self.attrFields.append(layer.fields()[i].name())
    # construct gui (using these fields)
    flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
    # construct gui: if available reuse this one
    if hasattr(self, 'imageMapPlugin') == False:
        self.imageMapPluginGui = ImageMapPluginGui(self.iface.mainWindow(), flags)
    self.imageMapPluginGui.setAttributeFields(self.attrFields)
    self.imageMapPluginGui.setMapCanvasSize(self.iface.mapCanvas().width(), self.iface.mapCanvas().height())
    self.layerAttr = self.attrFields
    self.selectedFeaturesOnly = False # default all features in current Extent
    # catch SIGNAL's
    QObject.connect(self.imageMapPluginGui, SIGNAL("getFilesPath(QString)"), self.setFilesPath)
    QObject.connect(self.imageMapPluginGui, SIGNAL("getLayerName(QString)"), self.setLayerName)
    QObject.connect(self.imageMapPluginGui, SIGNAL("getDimensions(QString)"), self.setDimensions)
    QObject.connect(self.imageMapPluginGui, SIGNAL("getIconFilePath(QString)"), self.setIconFilePath)
    QObject.connect(self.imageMapPluginGui, SIGNAL("onHrefAttributeSet(QString)"), self.onHrefAttributeFieldSet)
    QObject.connect(self.imageMapPluginGui, SIGNAL("onClickAttributeSet(QString)"), self.onClickAttributeFieldSet)
    QObject.connect(self.imageMapPluginGui, SIGNAL("onMouseOverAttributeSet(QString)"), self.onMouseOverAttributeFieldSet)
    QObject.connect(self.imageMapPluginGui, SIGNAL("onMouseOutAttributeSet(QString)"), self.onMouseOutAttributeFieldSet)
    QObject.connect(self.imageMapPluginGui, SIGNAL("getCbkBoxSelectedOnly(bool)"), self.setSelectedOnly)
    QObject.connect(self.imageMapPluginGui, SIGNAL("getSelectedFeatureCount(QString)"), self.setFeatureCount)
    QObject.connect(self.imageMapPluginGui, SIGNAL("go(QString)"), self.go)
    QObject.connect(self.imageMapPluginGui, SIGNAL("setMapCanvasSize(int, int)"), self.setMapCanvasSize)
    # remember old paths in this session:
    self.imageMapPluginGui.setFilesPath(self.filesPath)
    self.imageMapPluginGui.setIconFilePath(self.iconFilePath)
    # Set active layer name and expected image dimensions
    self.imageMapPluginGui.setLayerName(self.iface.activeLayer().name())
    self.imageMapPluginGui.setDimensions("~ " + str(self.iface.mapCanvas().width()) + " x " + str(self.iface.mapCanvas().height()))
    # Set number of selected features
    msg = ""
    featureCount = self.iface.activeLayer().selectedFeatureCount()
    if featureCount > 0:
        msg = " (selected feat. may be outside of extent)"
    self.imageMapPluginGui.setFeatureCount(str(featureCount) + msg)
    self.imageMapPluginGui.show()

  def writeHtml(self):
    iconName = os.path.basename(os.path.normpath(self.iconFilePath))
    src = self.iconFilePath
    dst = os.path.dirname(self.filesPath) + "/" + iconName
    # Copy marker symbol to export directory if it is located elsewhere
    if src <> dst:
        copyfile(src, dst)
    # create a holder for retrieving features from the provider
    feature = QgsFeature();
    temp = unicode(self.filesPath+".png")
    imgfilename = os.path.basename(temp)
    html = [u'<!DOCTYPE HTML><html>']
    isLabelChecked = self.imageMapPluginGui.isOnClickChecked()
    isInfoChecked = self.imageMapPluginGui.isOnMouseOverChecked()
    html.append(u'<head><title>QGIS</title></head><body>')
    if isInfoChecked:
        html.append(u'<div id="info-box" class="hidden"></div>')
    if isLabelChecked:
        html.append(u'<div class="title-box"></div>')
    # Write necessary CSS content:
    html.append(u'<style type="text/css">')
    html.append(u'#map-container { width: auto; height: auto; z-index: 0; position: relative; } .icons { z-index: 10; position: absolute; } body { font-family: Arial, Helvetica, sans-serif; } ')
    if isInfoChecked:
        html.append(u'#info-box { position: absolute; visibility: visible; z-index: 50; background-color: #FFFFFF; width: 250px; height: 114px; padding: 10px; margin: 0; border-radius: 10px; box-shadow: 4px 4px 2px 0 rgba(0, 0, 0, 0.75); font-family: Arial, Helvetica, sans-serif; font-size: 11px; line-height: 130%; color: #5F5F5F; } #info-box:after { content: ""; position: absolute; border-style: solid; border-width: 15px 15px 0; border-color: #FFFFFF transparent; display: block; width: 0; z-index: 1; bottom: -15px; left: 129px; } .hidden { display: none; } .visible { display: block; } ')
    if isLabelChecked:
        html.append(u'.title-box { position: absolute; z-index: 15; font-family: Arial, Helvetica, sans-serif; font-size: 12px; color: black; text-shadow: -1px 0 white, 0 1px white, 1px 0 white, 0 -1px white; white-space: nowrap; }')
    html.append(u'</style>')
    html.append(u'<div id="mousemovemessage"></div><br>')
    html.append(u'<div id="container"></div><img id="map-container" src="'+ imgfilename +'" border="0" ismap="ismap" usemap="#mapmap" alt="html imagemap created with QGIS" >\n')
    html.append(u'<map name="mapmap">\n')

    mapCanvasExtent = self.iface.mapCanvas().extent()
    doCrsTransform = False

    # in case of 'on the fly projection' 
    # AND 
    # different srs's for mapCanvas/project and layer we have to reproject stuff
    if hasattr(self.iface.mapCanvas().mapRenderer(), 'destinationSrs'):
      # QGIS < 2.0
      destinationCrs = self.iface.mapCanvas().mapRenderer().destinationSrs()
      layerCrs = self.iface.activeLayer().srs()
    else:
      destinationCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
      layerCrs = self.iface.activeLayer().crs()
    #print 'destination crs: %s:' % destinationCrs.toProj4()
    #print 'layer crs:       %s:' % layerCrs.toProj4()
    if not destinationCrs == layerCrs:
      # we have to transform the mapCanvasExtent to the data/layer Crs to be able
      # to retrieve the features from the data provider
      # but ONLY if we are working with on the fly projection
      # (because in that case we just 'fly' to the raw coordinates from data)
      if self.iface.mapCanvas().hasCrsTransformEnabled():
        self.crsTransform = QgsCoordinateTransform(destinationCrs, layerCrs)
        mapCanvasExtent = self.crsTransform.transformBoundingBox(mapCanvasExtent)
        # we have to have a transformer to do the transformation of the geometries
        # to the mapcanvas srs ourselves:
        self.crsTransform = QgsCoordinateTransform(layerCrs, destinationCrs)
        doCrsTransform = True
    # now iterate through each feature
    # select features within current extent,
    # set max progress bar to number of features (not very accurate with a lot of huge multipolygons)
    #self.imageMapPluginGui.setProgressBarMax(self.iface.activeLayer().featureCount())
    # or run over all features in current selection, just to determine the number of... (should be simpler ...)
    count = 0
    #   with  ALL attributes, WITHIN extent, WITH geom, AND using Intersect instead of bbox
    if hasattr(self.provider, 'select'):
        self.provider.select(self.provider.attributeIndexes(), mapCanvasExtent, True, True)
        while self.provider.nextFeature(feature):
            count = count + 1
    else:
        request = QgsFeatureRequest().setFilterRect(mapCanvasExtent)
        for feature in self.iface.activeLayer().getFeatures(request):
            count = count + 1
    self.imageMapPluginGui.setProgressBarMax(count)
    progressValue = 0
    # in case of points / lines we need to buffer geometries, calculate bufferdistance here
    bufferDistance = self.iface.mapCanvas().mapUnitsPerPixel()*10 #(plusminus 20pixel areas)

    # get a list of all selected features ids
    selectedFeaturesIds = self.iface.activeLayer().selectedFeaturesIds()
    # it seems that a postgres provider is on the end of file now
    # we do the select again to set the pointer/cursor to 0 again ?
    if hasattr(self.provider, 'select'):
        self.provider.select(self.provider.attributeIndexes(), mapCanvasExtent, True, True)
        while self.provider.nextFeature(feature):
            html.extend( self.handleGeom(feature, selectedFeaturesIds, doCrsTransform, bufferDistance) )
            progressValue = progressValue+1
            self.imageMapPluginGui.setProgressBarValue(progressValue)
    else:   # QGIS >= 2.0
        for feature in self.iface.activeLayer().getFeatures(request):
            html.extend( self.handleGeom(feature, selectedFeaturesIds, doCrsTransform, bufferDistance) )
            progressValue = progressValue+1
            self.imageMapPluginGui.setProgressBarValue(progressValue)
    html.append(u'</map>')
    # Write necessary JavaScript content:
    html.append(u'<script type="text/javascript">\n')
    html.append(u'(function() { "use strict"; var offsetHeight = document.getElementById("map-container").offsetHeight - 10; var areas = document.querySelectorAll("area"); for (var i = 0; i < areas.length; i++) { var img = new Image(); var centroid = getAreaCenter(areas[i].getAttribute("coords")); img.id = i.toString(); img.src = "'+ iconName +'"; img.className = "hidden"; document.getElementById("container").appendChild(img); img.style.left = centroid[0] + "px"; img.style.top = centroid[1] + "px"; img.onload = function() { this.style.left = parseInt(this.style.left, 10) - this.width / 2 + 8 + "px"; this.style.top = parseInt(this.style.top, 10) - this.height / 2 + 25 + "px"; this.className = "icons"; ')
    if isLabelChecked:
        html.append(u'var boundingBox = this.getBoundingClientRect(); this.style.top = parseInt(this.style.top, 10) + offsetHeight + "px"; var centerX = boundingBox.width / 2 + boundingBox.left + document.body.scrollLeft; var centerY = boundingBox.height + boundingBox.top + document.body.scrollTop; displayElementText(centerX, centerY, Number(this.id));')
    html.append(u' } } ')
    if isInfoChecked:
        html.append(u'document.addEventListener("click", function(e) { if (e.target.className === "icons") { var boundingBox = e.target.getBoundingClientRect(); var centerX = boundingBox.width / 2 + boundingBox.left; var centerY = boundingBox.top + boundingBox.height / 2; document.getElementById("info-box").className = "visible"; displayBox(centerX, centerY, Number(e.target.id)); } else { hideBox(); } }); ')
        html.append(u'function displayBox(centerX, centerY, id) { var infoBox = document.getElementById("info-box"); var infoWidthToCenter = infoBox.offsetWidth / 2; var infoHeight = infoBox.offsetHeight; infoBox.innerHTML = infoBoxes[id]; infoBox.style.left = (centerX - infoWidthToCenter - 9) + document.body.scrollLeft + "px"; infoBox.style.top = (centerY - infoHeight - 15) + document.body.scrollTop + "px"; } ')
        html.append(u'function hideBox() { document.getElementById("info-box").className = "hidden"; } ')
    if isLabelChecked:
        html.append(u'function displayElementText(centerX, centerY, id) { var titleBoxContainer = document.getElementsByClassName("title-box")[0]; var titleBox = document.createElement("title-box"); titleBox.className = "title-box"; titleBox.innerHTML = labels[id]; titleBoxContainer.appendChild(titleBox); var titleWidthToCenter = titleBox.offsetWidth / 2; var titleHeightToCenter = titleBox.offsetHeight; titleBox.style.left = (centerX - titleWidthToCenter - 8) + "px"; titleBox.style.top = (centerY - titleHeightToCenter + 5) + "px"; } ')
    html.append(u'function getAreaCenter(coords) { var coordsArray = coords.split(","), center = []; var coord, maxX, maxY, minX = maxX = parseInt(coordsArray[0], 10), minY = maxY = parseInt(coordsArray[1], 10); for (var i = 0; i < coordsArray.length; i++) { coord = parseInt(coordsArray[i], 10); if (i % 2 === 0) { if (coord < minX) { minX = coord; } else if (coord > maxX) { maxX = coord; } } else { if (coord < minY) { minY = coord; } else if (coord > maxY) { maxY = coord; } } } center = [parseInt((minX + maxX) / 2, 10), parseInt((minY + maxY) / 2, 10)]; return center; } ')
    # Dynamically write JavaScript array from field attribute array
    if len(self.labels) > 0:
        labelCounter = 0
        for l in self.labels:
            if len(self.labels) == 1:
                html.append(u'var labels = ["'+ l +'"]; ')
                break
            else:
                if labelCounter == 0:
                    html.append(u'var labels = ["'+ l +'", ')
                elif labelCounter <> len(self.labels) - 1:
                    html.append(u'"'+ l +'", ')
                else:
                    html.append(u'"'+ l +'"]; ')
                    break
                labelCounter = labelCounter + 1
    if len(self.infoBoxes) > 0:
        infoBoxCounter = 0
        for i in self.infoBoxes:
            if len(self.infoBoxes) == 1:
                html.append(u'var infoBoxes = ["'+ i +'"]; ')
                break
            else:
                if infoBoxCounter == 0:
                    html.append(u'var infoBoxes = ["'+ i +'", ')
                elif infoBoxCounter <> len(self.infoBoxes) - 1:
                    html.append(u'"'+ i +'", ')
                else:
                    html.append(u'"'+ i +'"]; ')
                    break
                infoBoxCounter = infoBoxCounter + 1
    # Clean up arrays afterwards
    del self.labels[:]
    del self.infoBoxes[:]
    html.append(u'})();\n')
    html.append(u'</script></body></html>')
    return html

  def handleGeom(self, feature, selectedFeaturesIds, doCrsTransform, bufferDistance):
    html = []
    # if checkbox 'selectedFeaturesOnly' is checked: check if this feature is selected
    if self.selectedFeaturesOnly and feature.id() not in selectedFeaturesIds:
        # print "skipping %s " % feature.id()
        None
    else:
        geom = feature.geometry()
        if hasattr(self.iface.activeLayer(), "srs"):
            # QGIS < 2.0
            layerCrs = self.iface.activeLayer().srs()
        else:
            layerCrs = self.iface.activeLayer().crs()
        if doCrsTransform:
            if hasattr(geom, "transform"):
                geom.transform(self.crsTransform)
            else:
                QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Cannot crs-transform geometry in your QGIS version ...\n" "Only QGIS version 1.5 and above can transform geometries on the fly\n" "As a workaround, you can try to save the layer in the destination crs (eg as shapefile) and reload that layer...\n"), QMessageBox.Ok, QMessageBox.Ok)
                #break
                raise Exception("Cannot crs-transform geometry in your QGIS version ...\n" "Only QGIS version 1.5 and above can transform geometries on the fly\n" "As a workaround, you can try to save the layer in the destination crs (eg as shapefile) and reload that layer...\n")
        projectExtent = self.iface.mapCanvas().extent()
        projectExtentAsPolygon = QgsGeometry()
        projectExtentAsPolygon = QgsGeometry.fromRect(projectExtent)
        #print "GeomType: %s" % geom.wkbType()
        if geom.wkbType() == QGis.WKBPoint: # 1 = WKBPoint
            # we make a copy of the geom, because apparently buffering the orignal will
            # only buffer the source-coordinates 
            geomCopy = QgsGeometry.fromPoint(geom.asPoint())
            polygon = geomCopy.buffer(bufferDistance, 0).asPolygon()
            #print "BufferedPoint: %s" % polygon
            for ring in polygon:
                h = self.ring2area(feature, ring, projectExtent, projectExtentAsPolygon)
                html.append(h)
        if geom.wkbType() == QGis.WKBPolygon: # 3 = WKBTYPE.WKBPolygon:
            polygon = geom.asPolygon()  # returns a list
            for ring in polygon:
                h = self.ring2area(feature, ring, projectExtent, projectExtentAsPolygon)
                html.append(h)
        if geom.wkbType() == QGis.WKBMultiPolygon: # 6 = WKBTYPE.WKBMultiPolygon:
            multipolygon = geom.asMultiPolygon() # returns a list
            for polygon in multipolygon:
                for ring in polygon:
                    h = self.ring2area(feature, ring, projectExtent, projectExtentAsPolygon)
                    html.append(h)
    return html

  def renderTest(self, painter):
    # Get canvas dimensions
    self.canvaswidth = painter.device().width()
    self.canvasheight = painter.device().height()

  def setFilesPath(self, filesPathQString):
    self.filesPath = filesPathQString

  def setIconFilePath(self, iconPathQString):
    self.iconFilePath = iconPathQString
    
  def setLayerName(self, layerNameQString):
    self.layerName = layerNameQString
  
  def setDimensions(self, dimensionsQString):
    self.dimensions = dimensionsQString
    
  def onHrefAttributeFieldSet(self, attributeFieldQstring):
    self.hrefAttributeField = attributeFieldQstring
    self.hrefAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

  def onClickAttributeFieldSet(self, attributeFieldQstring):
    self.onClickAttributeField = attributeFieldQstring
    self.onClickAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

  def onMouseOverAttributeFieldSet(self, attributeFieldQstring):
    self.onMouseOverAttributeField = attributeFieldQstring
    self.onMouseOverAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

  def onMouseOutAttributeFieldSet(self, attributeFieldQstring):
    self.onMouseOutAttributeField = attributeFieldQstring
    self.onMouseOutAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

  def setSelectedOnly(self, selectedOnlyBool):
    #print "selectedFeaturesOnly: %s" % selectedOnlyBool
    self.selectedFeaturesOnly = selectedOnlyBool
  
  def setFeatureCount(self, featureCountQstring):
    self.featureCount = featureCountQstring
    
  def setMapCanvasSize(self, newWidth, newHeight):
    mapCanvas=self.iface.mapCanvas()
    parent=mapCanvas.parentWidget()
    # QGIS 2.4 places another widget between mapcanvas and qmainwindow, so:
    if not parent.parentWidget() == None:
        parent = parent.parentWidget()
    # some QT magic for me, coming from maximized force a minimal layout change first
    if(parent.isMaximized()):
      QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Maximized QGIS window..\n" "QGIS window is maximized, plugin will try to de-maximize the window.\n" "If image size is still not exact what you asked for,\ntry starting plugin with non maximized window."), QMessageBox.Ok, QMessageBox.Ok)
      parent.showNormal()
    # on diffent OS's there seems to be different offsets to be taken into account
    magic=0
    if platform.system() == "Linux":
      magic=0 # mmm, not magic anymore?
    elif platform.system() == "Windows":
      magic=0 # mmm, not magic anymore?
    newWidth=newWidth+magic
    newHeight=newHeight+magic
    diffWidth=mapCanvas.size().width()-newWidth
    diffHeight=mapCanvas.size().height()-newHeight
    mapCanvas.resize(newWidth, newHeight)
    parent.resize(parent.size().width()-diffWidth, parent.size().height()-diffHeight)
    # HACK: there are cases where after maximizing and here demaximizing the size of the parent is not
    # in sync with the actual size, giving a small error in the size setting
    # we do the resizing again, this fixes this small error then ....
    if newWidth <> mapCanvas.size().width() or newHeight <> mapCanvas.size().height():
      diffWidth=mapCanvas.size().width()-newWidth
      diffHeight=mapCanvas.size().height()-newHeight
      mapCanvas.resize(newWidth, newHeight)
      parent.resize(parent.size().width()-diffWidth, parent.size().height()-diffHeight)

  def go(self, foo):
    htmlfilename = unicode(self.filesPath + ".html")
    imgfilename = unicode(self.filesPath + ".png")
    # check if path is writable: ?? TODO
    #if not os.access(htmlfilename, os._OK):
    #  QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("Unable to write file with this name.\n" "Please choose a valid filename and a writable directory."))
    #  return
    # check if file(s) exist:
    if os.path.isfile(htmlfilename) or os.path.isfile(imgfilename):
        if QMessageBox.question(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("There is already a filename with this name.\n" "Continue?"), QMessageBox.Cancel, QMessageBox.Ok) <> QMessageBox.Ok:
            return
    # else: everthing ok: start writing img and html
    try:
        if len(self.filesPath)==0:
            raise IOError
        file = open(htmlfilename, "w")
        html = self.writeHtml()
        for line in html:
          file.write(line.encode('utf-8'))
        file.close()
        self.index = 0
        self.iface.mapCanvas().saveAsImage(imgfilename)
        msg = "Files successfully saved to:\n" + self.filesPath
        QMessageBox.information(self.iface.mainWindow(), self.MSG_BOX_TITLE, ( msg ), QMessageBox.Ok)
        self.imageMapPluginGui.hide()
    except IOError:
        QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, ("No valid path or file name.\n" "Please enter or browse a valid file name."), QMessageBox.Ok, QMessageBox.Ok)


  # NOT WORKING ????
  # pixpoint = m2p.transform(point.x(), point.y())
  # print m2p.transform(point.x(), point.y())
  # so for now: a custom 'world2pixel' method
  def w2p(self, x, y, mupp, minx, maxy):
    pixX = (x - minx)/mupp
    pixY = (y - maxy)/mupp
    return [int(pixX), int(-pixY)]

  # for given ring in feature, IF at least one point in ring is in mapCanvasExtent
  # generate a string like:
  # <area data-info-id=x shape=polygon coords=519,-52,519,..,-52,519,-52 alt=...>
  def ring2area(self, feature, ring, extent, extentAsPoly):
    param = u''
    htm = u'<area data-info-id="'+ str(self.index) +'" shape="poly" '
    self.index = self.index + 1
    if hasattr(feature, 'attributeMap'):
        attrs = feature.attributeMap()
    else:
        # QGIS > 2.0
        attrs = feature
    # escape ' and " because they will collapse as javascript parameter
    if self.imageMapPluginGui.isOnClickChecked():
        # A negative index in this context means the field in question is a virtual one
        if self.onClickAttributeIndex < 0:
            # This is a workaround, since the data provider cannot find the virtual fields
            self.onClickAttributeIndex = self.attrFields.index(str(self.onClickAttributeField))
        param = unicode(attrs[self.onClickAttributeIndex])
        self.labels.append(self.escapeNewLine(param))
    if self.imageMapPluginGui.isOnMouseOverChecked():
        if self.onMouseOverAttributeIndex < 0:
            self.onMouseOverAttributeIndex = self.attrFields.index(str(self.onMouseOverAttributeField))
        param = unicode(attrs[self.onMouseOverAttributeIndex])
        self.infoBoxes.append(self.escapeNewLine(param))
    htm = htm + 'coords="'
    lastPixel=[0,0]
    insideExtent = False
    coordCount = 0
    extentAsPoly = QgsGeometry()
    extentAsPoly = QgsGeometry.fromRect(extent)
    for point in ring:
        if extentAsPoly.contains(point):
            insideExtent = True
        pixpoint =  self.w2p(point.x(), point.y(), 
                self.iface.mapCanvas().mapUnitsPerPixel(),
                extent.xMinimum(), extent.yMaximum())
        if lastPixel <> pixpoint:
            coordCount = coordCount + 1
            htm += (str(pixpoint[0]) + ',' + str(pixpoint[1]) + ',')
            lastPixel = pixpoint
    htm = htm[0:-1]
    # check if there are more than 2 coords: very small polygons on current map can have coordinates
    # which if rounded to pixels all come to the same pixel, resulting in just ONE x,y coordinate
    # we skip these
    if coordCount < 2:
        #print "Ring contains just one pixel coordinate pair: skipping"
        return ''
    # if at least ONE pixel of this ring is in current view extent, return the area-string, otherwise return an empty string
    if not insideExtent:
        #print "RING FULLY OUTSIDE EXTENT: %s " % ring
        return ''
    else:
        # using last param as alt parameter (to be W3 compliant we need one)
        htm += '" alt="' + self.escapeNewLine(param) + '">\n'
        return unicode(htm)
        
  # Prevent new lines inside JavaScript array
  def escapeNewLine(self, str):
    return "".join(str.split("\n"))