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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from imagemapplugingui import ImageMapPluginGui

# Initialize Qt resources from file
import imagemapplugin_rc
import codecs

from shutil import copyfile

VALID_GEOMETRY_TYPES = {
    QGis.WKBPolygon,
    QGis.WKBMultiPolygon,
    QGis.WKBPoint
}

class ImageMapPlugin:

    MSG_BOX_TITLE = "QGIS HTML Image Map Creator "

    def __init__(self, iface):
        # Save reference to the QGIS interface and initialize instance variables
        self.iface = iface
        self.files_path = ""
        self.attr_fields = []
        self.layer_name = ""
        self.dimensions = ""
        self.icon_file_path = ""
        self.labels = []
        self.info_boxes = []
        self.index = 0
        self.feature_count = 0

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/imagemapicon.xpm"), "create...", self.iface.mainWindow())
        self.action.setWhatsThis("Configuration for Image Map Creator")
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        if hasattr(self.iface, "addPluginToWebMenu"):
            self.iface.addPluginToWebMenu("&HTML Image Map Creator", self.action)
        else:
            self.iface.addPluginToMenu("&HTML Image Map Creator", self.action)
        # Connect to signal renderComplete which is emitted when canvas rendering is done
        QObject.connect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)

    def unload(self):
        # Remove the plugin menu item and icon
        if hasattr(self.iface, "addPluginToWebMenu"):
            self.iface.removePluginWebMenu("&HTML Image Map Creator", self.action)
        else:
            self.iface.removePluginMenu("&HTML Image Map Creator", self.action)
        self.iface.removeToolBarIcon(self.action)
        # Disconnect from canvas signal
        QObject.disconnect(self.iface.mapCanvas(), SIGNAL("renderComplete(QPainter *)"), self.renderTest)

    def run(self):
        # Check if active layer is a polygon layer:
        layer = self.iface.activeLayer()
        if layer is None:
            QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
              "No active layer found\n"
              "Please select a (multi) polygon or point layer first, \n"
              "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
            return
        # Don't know if this is possible / needed
        if not layer.isValid():
            QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
              "No VALID layer found\n"
              "Please select a valid (multi) polygon or point layer first, \n"
              "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
            return
        if (layer.type() > 0):  # 0 = vector, 1 = raster
            QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
              "Wrong layer type, only vector layers may be used...\n"
              "Please select a vector layer first, \n"
              "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
            return
        self.provider = layer.dataProvider()
        if self.provider.geometryType() not in VALID_GEOMETRY_TYPES:
            QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
              "Wrong geometry type, only (multi) polygons and points may be used.\n"
              "Please select a (multi) polygon or point layer first, \n"
              "by selecting it in the legend"), QMessageBox.Ok, QMessageBox.Ok)
            return

        # We need the fields of the active layer to show in the attribute combobox in the gui:
        self.attr_fields = []
        fields = self.provider.fields()
        if hasattr(fields, 'iteritems'):
            for (i, field) in fields.iteritems():
                self.attr_fields.append(field.name().trimmed())
        else:
            for field in self.provider.fields():
                self.attr_fields.append(field.name().strip())
        # Append virtual fields
        for i in range(layer.fields().count()):
            if layer.fields().fieldOrigin(i) == QgsFields.OriginExpression:
                self.attr_fields.append(layer.fields()[i].name())
        # Construct gui (using these fields)
        flags = Qt.WindowTitleHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint  # QgisGui.ModalDialogFlags
        # Construct gui: if available reuse this one
        if hasattr(self, 'imageMapPlugin') is False:
            self.imageMapPluginGui = ImageMapPluginGui(self.iface.mainWindow(), flags)
        self.imageMapPluginGui.setAttributeFields(self.attr_fields)
        self.layerAttr = self.attr_fields
        self.selectedFeaturesOnly = False  # default all features in current extent
        # Catch SIGNAL's
        signals = [
            ("getFilesPath(QString)", self.setFilesPath),
            ("getLayerName(QString)", self.setLayerName),
            ("getDimensions(QString)", self.setDimensions),
            ("getIconFilePath(QString)", self.setIconFilePath),
            ("labelAttributeSet(QString)", self.labelAttributeFieldSet),
            ("infoBoxAttributeSet(QString)", self.infoBoxAttributeFieldSet),
            ("getCbkBoxSelectedOnly(bool)", self.setSelectedOnly),
            ("getSelectedFeatureCount(QString)", self.setFeatureCount),
            ("go(QString)", self.go),
            ("setMapCanvasSize(int, int)", self.setMapCanvasSize),
        ]
        for code, func in signals:
            QObject.connect(self.imageMapPluginGui, SIGNAL(code), func)
        self.imageMapPluginGui.setFilesPath(self.files_path)
        self.imageMapPluginGui.setIconFilePath(self.icon_file_path)
        # Set active layer name and expected image dimensions
        self.imageMapPluginGui.setLayerName(self.iface.activeLayer().name())
        canvas_width = self.iface.mapCanvas().width()
        canvas_height = self.iface.mapCanvas().height()
        dimensions = "~ Width: <b>{}</b> pixels | Height: <b>{}</b> pixels".format(canvas_width, canvas_height)
        self.imageMapPluginGui.setDimensions(dimensions)
        # Set number of selected features
        msg = ""
        feature_count = self.iface.activeLayer().selectedFeatureCount()
        if feature_count > 0:
            msg = "(feature(s) may be outside of view)"
        else:
            self.imageMapPluginGui.chkBoxSelectedOnly.setEnabled(False)
        self.imageMapPluginGui.setFeatureCount("{} {}".format(feature_count, msg))
        self.imageMapPluginGui.show()

    def writeHtml(self):
        iconName = os.path.basename(os.path.normpath(self.icon_file_path))
        src = self.icon_file_path
        dst = os.path.dirname(self.files_path) + "/" + iconName
        # Copy marker symbol to export directory if it is located elsewhere
        if src != dst:
            copyfile(src, dst)
        plugin_path = os.path.dirname(__file__)
        # Template directories
        full_template_dir = "{}/templates/full".format(plugin_path)
        label_template_dir = "{}/templates/label".format(plugin_path)
        info_template_dir = "{}/templates/info_box".format(plugin_path)
        # Create a holder for retrieving features from the provider
        feature = QgsFeature()
        temp = unicode(self.files_path+".png")
        imgfilename = os.path.basename(temp)
        html = [u'<!DOCTYPE HTML><html>']
        isLabelChecked = self.imageMapPluginGui.isLabelChecked()
        isInfoChecked = self.imageMapPluginGui.isInfoBoxChecked()
        onlyLabel = isLabelChecked and not isInfoChecked
        onlyInfo = isInfoChecked and not isLabelChecked
        html.append(u'<head><title>' + self.iface.activeLayer().name() +
          '</title><meta charset="UTF-8"></head><body>')
        html.append(u'\n<!-- BEGIN EXTRACTABLE CONTENT -->')
        if isInfoChecked:
            html.append(u'\n<div id="info-box" class="hidden"></div>')
        if isLabelChecked:
            html.append(u'\n<div class="title-box"></div>')
        # Write necessary CSS content for corresponding features, namely "label" and "infoBox":
        html.append(u'<style type="text/css">\n')
        filename = "css.txt"
        if onlyLabel:
            html.append(self.writeContent(label_template_dir, filename))
        elif onlyInfo:
            html.append(self.writeContent(info_template_dir, filename))
        else:
            html.append(self.writeContent(full_template_dir, filename))
        html.append(u'<br>')
        html.append(u'<div id="container"></div><img id="map-container" src="' + imgfilename + '" ')
        html.append(u'border="0" ismap="ismap" usemap="#mapmap" alt="html imagemap created with QGIS" >\n')
        html.append(u'<map name="mapmap">\n')

        mapCanvasExtent = self.iface.mapCanvas().extent()
        doCrsTransform = False
        # In case of 'on the fly projection'.
        # Different srs's for mapCanvas/project and layer we have to reproject stuff
        if hasattr(self.iface.mapCanvas().mapRenderer(), 'destinationSrs'):
            # QGIS < 2.0
            destinationCrs = self.iface.mapCanvas().mapRenderer().destinationSrs()
            layerCrs = self.iface.activeLayer().srs()
        else:
            destinationCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
            layerCrs = self.iface.activeLayer().crs()
        if not destinationCrs == layerCrs:
            # We have to transform the mapCanvasExtent to the data/layer Crs to be able
            # to retrieve the features from the data provider,
            # but ONLY if we are working with on the fly projection.
            # (because in that case we just 'fly' to the raw coordinates from data)
            if self.iface.mapCanvas().hasCrsTransformEnabled():
                self.crsTransform = QgsCoordinateTransform(destinationCrs, layerCrs)
                mapCanvasExtent = self.crsTransform.transformBoundingBox(mapCanvasExtent)
                # We have to have a transformer to do the transformation of the geometries
                # to the mapcanvas srs ourselves:
                self.crsTransform = QgsCoordinateTransform(layerCrs, destinationCrs)
                doCrsTransform = True
        # Now iterate through each feature,
        # select features within current extent,
        # set max progress bar to number of features (not very accurate with a lot of huge multipolygons)
        # or run over all features in current selection, just to determine the number of... (should be simpler ...)
        count = 0
        # With  ALL attributes, WITHIN extent, WITH geom, AND using Intersect instead of bbox
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
        # In case of points / lines we need to buffer geometries, calculate bufferdistance here
        bufferDistance = self.iface.mapCanvas().mapUnitsPerPixel() * 10  # (plusminus 20pixel areas)
        # Get a list of all selected features ids.
        selectedFeaturesIds = self.iface.activeLayer().selectedFeaturesIds()
        # It seems that a postgres provider is on the end of file now
        if hasattr(self.provider, 'select'):
            self.provider.select(self.provider.attributeIndexes(), mapCanvasExtent, True, True)
            while self.provider.nextFeature(feature):
                html.extend(self.handleGeom(feature, selectedFeaturesIds, doCrsTransform, bufferDistance))
                progressValue = progressValue+1
                self.imageMapPluginGui.setProgressBarValue(progressValue)
        else:   # QGIS >= 2.0
            for feature in self.iface.activeLayer().getFeatures(request):
                html.extend(self.handleGeom(feature, selectedFeaturesIds, doCrsTransform, bufferDistance))
                progressValue = progressValue + 1
                self.imageMapPluginGui.setProgressBarValue(progressValue)
        html.append(u'</map>')
        # Write necessary JavaScript content:
        # If only one checkbox is checked, the required code for that feature (label/info box) alone is written
        html.append(u'<script type="text/javascript">\n')
        filename = "js.txt"
        if onlyLabel:
            html.append(self.writeContent(label_template_dir, filename).replace("{}", repr(str(iconName))))
        elif onlyInfo:
            html.append(self.writeContent(info_template_dir, filename).replace("{}", repr(str(iconName))))
        else:
            html.append(self.writeContent(full_template_dir, filename).replace("{}", repr(str(iconName))))
        # Dynamically write JavaScript array from field attribute arrays
        if self.labels:
            html.append(u'\nvar labels = ["' + '", "'.join(self.labels) + '"]; ')
        if self.info_boxes:
            html.append(u'\nvar infoBoxes = ["' + '", "'.join(self.info_boxes) + '"]; ')
        # Clean up arrays afterwards
        del self.labels[:]
        del self.info_boxes[:]
        html.append(u'})();\n')
        html.append(u'</script>')
        html.append(u'\n<!-- END EXTRACTABLE CONTENT -->')
        html.append(u'\n</body></html>')
        return html

    # Returns a string representing the individual template's content
    def writeContent(self, dir, filename):
        content = []
        f = codecs.open("{}/{}".format(dir, filename), "r")
        for line in f:
            content.append(line)
        f.close()
        return "".join(content)

    def handleGeom(self, feature, selectedFeaturesIds, doCrsTransform, bufferDistance):
        html = []
        # If checkbox 'selectedFeaturesOnly' is checked: check if this feature is selected
        if self.selectedFeaturesOnly and feature.id() not in selectedFeaturesIds:
            return html
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
                QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
                  "Cannot crs-transform geometry in your QGIS version ...\n"
                  "Only QGIS version 1.5 and above can transform geometries on the fly\n"
                  "As a workaround, you can try to save the layer in the destination crs\n"
                  "(eg as shapefile) and reload that layer...\n"), QMessageBox.Ok, QMessageBox.Ok)
                raise Exception("Cannot crs-transform geometry in your QGIS version ...\n"
                  "Only QGIS version 1.5 and above can transform geometries on the fly\n"
                  "As a workaround, you can try to save the layer in the destination crs\n"
                  "(e.g. as Shapefile) and reload that layer...\n")
        projectExtent = self.iface.mapCanvas().extent()
        projectExtentAsPolygon = QgsGeometry()
        projectExtentAsPolygon = QgsGeometry.fromRect(projectExtent)
        ringTuple = (
            feature,
            projectExtent,
            projectExtentAsPolygon
        )
        if geom.wkbType() == QGis.WKBPoint:  # 1 = WKBPoint
            # We make a copy of the geom, because apparently buffering the original will
            # only buffer the source-coordinates
            geomCopy = QgsGeometry.fromPoint(geom.asPoint())
            polygon = geomCopy.buffer(bufferDistance, 0).asPolygon()
            html.append(self.polygon2html(ringTuple, polygon))
        if geom.wkbType() == QGis.WKBPolygon:  # 3 = WKBTYPE.WKBPolygon:
            polygon = geom.asPolygon()  # returns a list
            html.append(self.polygon2html(ringTuple, polygon))
        if geom.wkbType() == QGis.WKBMultiPolygon:  # 6 = WKBTYPE.WKBMultiPolygon:
            multipolygon = geom.asMultiPolygon()  # returns a list
            for polygon in multipolygon:
                html.append(self.polygon2html(ringTuple, polygon))
        return html

    def polygon2html(self, ringTuple, polygon):
        feature = ringTuple[0]
        projectExtent = ringTuple[1]
        projectExtentAsPolygon = ringTuple[2]
        area_strings = [self.ring2html(feature, ring, projectExtent, projectExtentAsPolygon) for ring in polygon]
        return "".join(area_strings)

    def renderTest(self, painter):
        # Get canvas dimensions
        self.canvas_width = painter.device().width()
        self.canvas_height = painter.device().height()

    def setFilesPath(self, filesPathQString):
        self.files_path = filesPathQString

    def setIconFilePath(self, iconPathQString):
        self.icon_file_path = iconPathQString

    def setLayerName(self, layerNameQString):
        self.layer_name = layerNameQString

    def setDimensions(self, dimensionsQString):
        self.dimensions = dimensionsQString

    def labelAttributeFieldSet(self, attributeFieldQstring):
        self.labelAttributeField = attributeFieldQstring
        self.labelAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

    def infoBoxAttributeFieldSet(self, attributeFieldQstring):
        self.infoBoxAttributeField = attributeFieldQstring
        self.infoBoxAttributeIndex = self.provider.fieldNameIndex(attributeFieldQstring)

    def setSelectedOnly(self, selectedOnlyBool):
        self.selectedFeaturesOnly = selectedOnlyBool

    def setFeatureCount(self, featureCountQstring):
        self.feature_count = featureCountQstring

    def setMapCanvasSize(self, newWidth, newHeight):
        mapCanvas = self.iface.mapCanvas()
        parent = mapCanvas.parentWidget()
        # QGIS 2.4 places another widget between mapcanvas and qmainwindow, so:
        if not parent.parentWidget() is None:
            parent = parent.parentWidget()
        # Some QT magic for me, coming from maximized, force a minimal layout change first
        if(parent.isMaximized()):
            QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
              "Maximized QGIS window..\n"
              "QGIS window is maximized, plugin will try to de-maximize the window.\n"
              "If image size is still not exact what you asked for,\n"
              "try starting plugin with non maximized window."), QMessageBox.Ok, QMessageBox.Ok)
            parent.showNormal()
        diffWidth = mapCanvas.size().width() - newWidth
        diffHeight = mapCanvas.size().height() - newHeight
        mapCanvas.resize(newWidth, newHeight)
        parent.resize(parent.size().width() - diffWidth, parent.size().height() - diffHeight)
        # HACK: There are cases where after maximizing and here demaximizing the size of the parent is not
        # in sync with the actual size, giving a small error in the size setting.
        # We do the resizing again, which fixes this small error
        if newWidth != mapCanvas.size().width() or newHeight != mapCanvas.size().height():
            diffWidth = mapCanvas.size().width() - newWidth
            diffHeight = mapCanvas.size().height() - newHeight
            mapCanvas.resize(newWidth, newHeight)
            parent.resize(parent.size().width() - diffWidth, parent.size().height() - diffHeight)

    def go(self, foo):
        htmlfilename = unicode(self.files_path + ".html")
        imgfilename = unicode(self.files_path + ".png")
        if os.path.isfile(htmlfilename) or os.path.isfile(imgfilename):
            if QMessageBox.question(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
              "There is already a filename with this name.\n" "Continue?"), 
              QMessageBox.Cancel, QMessageBox.Ok) != QMessageBox.Ok:
                return
        # Else: everthing ok: start writing img and html
        try:
            if len(self.files_path) == 0:
                raise IOError
            file = open(htmlfilename, "w")
            html = self.writeHtml()
            for line in html:
                file.write(line.encode('utf-8'))
            file.close()
            self.index = 0
            self.iface.mapCanvas().saveAsImage(imgfilename)
            msg = "Files successfully saved to:\n" + self.files_path
            QMessageBox.information(self.iface.mainWindow(), self.MSG_BOX_TITLE, (msg), QMessageBox.Ok)
            self.imageMapPluginGui.hide()
        except IOError:
            QMessageBox.warning(self.iface.mainWindow(), self.MSG_BOX_TITLE, (
              "No valid path or filename.\n"
              "Please enter or browse a valid file name."), QMessageBox.Ok, QMessageBox.Ok)

    def world2pixel(self, x, y, mupp, minx, maxy):
        pixX = (x - minx)/mupp
        pixY = (y - maxy)/mupp
        return [int(pixX), int(-pixY)]

    # For given ring in feature, IF at least one point in ring is in 'mapCanvasExtent',
    # generate a string like:
    # <area data-info-id=x shape=polygon coords=519,-52,519,..,-52,519,-52 alt=...>
    def ring2html(self, feature, ring, extent, extentAsPoly):
        param = u''
        htm = u'<area data-info-id="' + str(self.index) + '" shape="poly" '
        self.index = self.index + 1
        if hasattr(feature, 'attributeMap'):
            attrs = feature.attributeMap()
        else:
            # QGIS > 2.0
            attrs = feature
        # Escape ' and " because they will collapse as JavaScript parameter
        if self.imageMapPluginGui.isLabelChecked():
            # A negative index in this context means the field in question is a virtual one
            if self.labelAttributeIndex < 0:
                # This is a workaround, since the data provider cannot find the virtual fields
                self.labelAttributeIndex = self.attr_fields.index(str(self.labelAttributeField))
            param = unicode(attrs[self.labelAttributeIndex])
            self.labels.append(self.removeNewLine(param))
        if self.imageMapPluginGui.isInfoBoxChecked():
            if self.infoBoxAttributeIndex < 0:
                self.infoBoxAttributeIndex = self.attr_fields.index(str(self.infoBoxAttributeField))
            param = unicode(attrs[self.infoBoxAttributeIndex])
            self.info_boxes.append(self.removeNewLine(param))
        htm = htm + 'coords="'
        lastPixel = [0, 0]
        insideExtent = False
        coordCount = 0
        extentAsPoly = QgsGeometry()
        extentAsPoly = QgsGeometry.fromRect(extent)
        for point in ring:
            if extentAsPoly.contains(point):
                insideExtent = True
            pixpoint = self.world2pixel(point.x(), point.y(),
                           self.iface.mapCanvas().mapUnitsPerPixel(),
                           extent.xMinimum(), extent.yMaximum())
            if lastPixel != pixpoint:
                coordCount = coordCount + 1
                htm += (str(pixpoint[0]) + ',' + str(pixpoint[1]) + ',')
                lastPixel = pixpoint
        htm = htm[0:-1]
        # Check if there are more than 2 coords: very small polygons on current map can have coordinates,
        # which if rounded to pixels all come to the same pixel, resulting in just ONE x,y coordinate.
        # We skip these:
        if coordCount < 2:
            return ''
        # If at least ONE pixel of this ring is in current view extent,
        # return the area-string, otherwise return an empty string
        if not insideExtent:
            return ''
        else:
            # Using last param as alt parameter (to be W3 compliant we need one)
            htm += '" alt="' + self.removeNewLine(param) + '">\n'
            return unicode(htm)

    # Prevent new lines inside JavaScript array
    def removeNewLine(self, str):
        return "".join(str.split("\n"))
