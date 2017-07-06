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

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

from imagemapplugingui import ImageMapPluginGui

# Initialize Qt resources from file
import imagemapplugin_rc
import codecs

VALID_GEOMETRY_TYPES = {
    QGis.WKBPolygon,
    QGis.WKBMultiPolygon,
    QGis.WKBPoint
}
PLUGIN_PATH = os.path.dirname(__file__)
# Template directories
FULL_TEMPLATE_DIR = "{}/templates/full".format(PLUGIN_PATH)
LABEL_TEMPLATE_DIR = "{}/templates/label".format(PLUGIN_PATH)
INFO_TEMPLATE_DIR = "{}/templates/info_box".format(PLUGIN_PATH)


class ImageMapPlugin:

    MSG_BOX_TITLE = "QGIS HTML Image Map Creator "

    def __init__(self, iface):
        # Save reference to the QGIS interface and initialize instance variables
        self.iface = iface
        self.files_path = ""
        self.label_field_index = 0
        self.info_field_index = 0
        self.attr_fields = []
        self.feature_total = ""
        self.layer_name = ""
        self.dimensions = ""
        self.labels = []
        self.label_offset = 0
        self.label_checked = False
        self.info_boxes = []
        self.info_offset = 0
        self.info_checked = False
        self.index = 0
        self.feature_count = 0

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/imagemapicon.xpm"), "Create map...", self.iface.mainWindow())
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
        self.selectedFeaturesOnly = False  # default: all features in current extent
        # Catch SIGNAL's
        signals = [
            ("getFilesPath(QString)", self.setFilesPath),
            ("getLayerName(QString)", self.setLayerName),
            ("getFeatureTotal(QString)", self.setFeatureTotal),
            ("getDimensions(QString)", self.setDimensions),
            ("labelAttributeSet(QString)", self.labelAttributeFieldSet),
            ("spinLabelSet(int)", self.setLabelOffset),
            ("getCbkBoxLabel(bool)", self.setLabelChecked),
            ("infoBoxAttributeSet(QString)", self.infoBoxAttributeFieldSet),
            ("spinInfoSet(int)", self.setInfoOffset),
            ("getCbkBoxInfo(bool)", self.setInfoChecked),
            ("getCbkBoxSelectedOnly(bool)", self.setSelectedOnly),
            ("getSelectedFeatureCount(QString)", self.setFeatureCount),
            ("go(QString)", self.go),
            ("setMapCanvasSize(int, int)", self.setMapCanvasSize),
        ]
        for code, func in signals:
            QObject.connect(self.imageMapPluginGui, SIGNAL(code), func)

        self.reloadGuiStates()
        # Set active layer name and expected image dimensions
        self.imageMapPluginGui.setLayerName(self.iface.activeLayer().name())
        self.imageMapPluginGui.setFeatureTotal("<b>{}</b> features total".format(self.iface.activeLayer().featureCount()))
        canvas_width = self.iface.mapCanvas().width()
        canvas_height = self.iface.mapCanvas().height()
        dimensions = "~ width: <b>{}</b> pixels, height: <b>{}</b> pixels"
        self.imageMapPluginGui.setDimensions(dimensions.format(canvas_width, canvas_height))
        # Set number of selected features
        selected_features = self.iface.activeLayer().selectedFeatureCount()
        selected_features_in_extent = self.nofSelectedFeaturesInExtent()
        if selected_features == 0 or selected_features_in_extent == 0:
            self.imageMapPluginGui.chkBoxSelectedOnly.setEnabled(False)
        select_msg = "<b>{}</b> selected, of which <b>{}</b> from map view will be exported"
        self.imageMapPluginGui.setFeatureCount(select_msg.format(selected_features, selected_features_in_extent))
        self.imageMapPluginGui.show()

    def reloadGuiStates(self):
        self.imageMapPluginGui.setFilesPath(self.files_path)
        # Only reload states if the plugin is used on the same layer as before:
        if self.layer_name == self.iface.activeLayer().name():
            # Reload selected features in combo-boxes:
            if self.label_field_index < len(self.attr_fields):
                index = self.handleFieldIndexes(self.label_field_index, self.labelAttributeField)
                self.imageMapPluginGui.cmbLabelAttributes.setCurrentIndex(index)
            if self.info_field_index < len(self.attr_fields):
                index = self.handleFieldIndexes(self.info_field_index, self.infoBoxAttributeField)
                self.imageMapPluginGui.cmbInfoBoxAttributes.setCurrentIndex(index)
            # Reload spin-box values:
            self.imageMapPluginGui.spinBoxLabel.setValue(self.label_offset)
            self.imageMapPluginGui.spinBoxInfo.setValue(self.info_offset)
            # Reload check-box states:
            label_state = Qt.Checked if self.label_checked else Qt.Unchecked
            info_state = Qt.Checked if self.info_checked else Qt.Unchecked
            self.imageMapPluginGui.chkBoxLabel.setCheckState(label_state)
            self.imageMapPluginGui.chkBoxInfoBox.setCheckState(info_state)

    def writeHtml(self):
        # Create a holder for retrieving features from the provider
        feature = QgsFeature()
        temp = unicode(self.files_path+".png")
        imgfilename = os.path.basename(temp)
        html = [u'<!DOCTYPE HTML>\n<html>']
        isLabelChecked = self.imageMapPluginGui.isLabelChecked()
        isInfoChecked = self.imageMapPluginGui.isInfoBoxChecked()
        onlyLabel = isLabelChecked and not isInfoChecked
        onlyInfo = isInfoChecked and not isLabelChecked
        html.append(u'\n<head>\n<title>' + self.iface.activeLayer().name() +
                    '</title>\n<meta charset="UTF-8">\n</head>\n<body>')
        html.append(u'\n<!-- BEGIN EXTRACTABLE CONTENT -->')
        if isInfoChecked:
            html.append(u'\n<div id="himc-info-box" class="himc-hidden"></div>')
        if isLabelChecked:
            html.append(u'\n<div class="himc-title-box"></div>')
        # Write necessary CSS content for corresponding features, namely "label" and "infoBox":
        html.append(u'\n<style type="text/css">\n')
        filename = "css.txt"
        # Empty list as replacement parameter, because there are no replacements to be made in
        # CSS templates
        if onlyLabel:
            html.append(self.writeContent(LABEL_TEMPLATE_DIR, filename, []))
        elif onlyInfo:
            html.append(self.writeContent(INFO_TEMPLATE_DIR, filename, []))
        else:
            html.append(self.writeContent(FULL_TEMPLATE_DIR, filename, []))
        html.append(u'\n<br>')
        html.append(u'\n<img id="himc-map-container" src="' + imgfilename + '" ')
        html.append(u'border="0" ismap="ismap" usemap="#mapmap" alt="html imagemap created with QGIS" >')
        html.append(u'\n<map name="mapmap">\n')

        mapCanvasExtent = self.getTransformedMapCanvas()
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
                # In case of points / lines we need to buffer geometries (plus/minus 20px areas)
                html.extend(self.handleGeom(feature, selectedFeaturesIds, self.doCrsTransform, bufferDistance))
                progressValue = progressValue + 1
                self.imageMapPluginGui.setProgressBarValue(progressValue)
        else:   # QGIS >= 2.0
            for feature in self.iface.activeLayer().getFeatures(request):
                html.extend(self.handleGeom(feature, selectedFeaturesIds, self.doCrsTransform, bufferDistance))
                progressValue = progressValue + 1
                self.imageMapPluginGui.setProgressBarValue(progressValue)
        html.append(u'</map>')
        # Write necessary JavaScript content:
        # If only one checkbox is checked, the required code for that feature (label/info box) alone is written
        html.append(u'\n<script type="text/javascript">\n')
        filename = "js.txt"
        if onlyLabel:
            html.append(self.writeContent(LABEL_TEMPLATE_DIR, filename, [self.label_offset]))
        elif onlyInfo:
            html.append(self.writeContent(INFO_TEMPLATE_DIR, filename, [self.info_offset]))
        else:
            html.append(self.writeContent(FULL_TEMPLATE_DIR, filename, [self.label_offset, self.info_offset]))
        # Dynamically write JavaScript array from field attribute list
        if self.labels:
            html.append(u'\nvar labels = ["' + '", "'.join(self.labels) + '"]; ')
        if self.info_boxes:
            html.append(u'\nvar infoBoxes = ["' + '", "'.join(self.info_boxes) + '"]; ')
        # Clean up list afterwards
        del self.labels[:]
        del self.info_boxes[:]
        html.append(u'})();')
        html.append(u'\n</script>')
        html.append(u'\n<!-- END EXTRACTABLE CONTENT -->')
        html.append(u'\n</body>\n</html>')
        return html

    # Returns a string representing the individual template's content and
    # replaces offset-placeholders in the "js.txt" templates
    def writeContent(self, dir, filename, offsets):
        content = ""
        f = codecs.open("{}/{}".format(dir, filename), "r")
        for line in f:
            content += line
        f.close()
        for i, replacement in enumerate("{}".format(i) for i in offsets):
            content = content.replace("{%s}" % i, replacement)
        return content

    def handleGeom(self, feature, selectedFeaturesIds, doCrsTransform, bufferDistance):
        html = []
        # If checkbox 'selectedFeaturesOnly' is checked: check if this feature is selected
        if self.selectedFeaturesOnly and feature.id() not in selectedFeaturesIds:
            return html
        geom = feature.geometry()
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
        if geom.wkbType() == QGis.WKBPoint:  # 1 = WKBPoint
            # We make a copy of the geom, because apparently buffering the original will
            # only buffer the source-coordinates
            geomCopy = QgsGeometry.fromPoint(geom.asPoint())
            polygon = geomCopy.buffer(bufferDistance, 0).asPolygon()
            html.append(self.polygon2html(feature, projectExtent, projectExtentAsPolygon, polygon))
        if geom.wkbType() == QGis.WKBPolygon:  # 3 = WKBTYPE.WKBPolygon:
            polygon = geom.asPolygon()  # returns a list
            html.append(self.polygon2html(feature, projectExtent, projectExtentAsPolygon, polygon))
        if geom.wkbType() == QGis.WKBMultiPolygon:  # 6 = WKBTYPE.WKBMultiPolygon:
            multipolygon = geom.asMultiPolygon()  # returns a list
            for polygon in multipolygon:
                html.append(self.polygon2html(feature, projectExtent, projectExtentAsPolygon, polygon))
        return html

    def polygon2html(self, feature, projectExtent, projectExtentAsPolygon, polygon):
        area_strings = [self.ring2html(feature, ring, projectExtent, projectExtentAsPolygon) for ring in polygon]
        return "".join(area_strings)

    def renderTest(self, painter):
        # Get canvas dimensions
        self.canvas_width = painter.device().width()
        self.canvas_height = painter.device().height()

    def setFilesPath(self, filesPathQString):
        self.files_path = filesPathQString

    def setLayerName(self, layerNameQString):
        self.layer_name = layerNameQString

    def setFeatureTotal(self, totalQString):
        self.feature_total = totalQString

    def setDimensions(self, dimensionsQString):
        self.dimensions = dimensionsQString

    def labelAttributeFieldSet(self, attributeFieldQstring):
        self.labelAttributeField = attributeFieldQstring
        self.label_field_index = self.provider.fieldNameIndex(attributeFieldQstring)

    def setLabelOffset(self, offset):
        self.label_offset = offset

    def setLabelChecked(self, isChecked):
        self.label_checked = isChecked

    def infoBoxAttributeFieldSet(self, attributeFieldQstring):
        self.infoBoxAttributeField = attributeFieldQstring
        self.info_field_index = self.provider.fieldNameIndex(attributeFieldQstring)

    def setInfoOffset(self, offset):
        self.info_offset = offset

    def setInfoChecked(self, isChecked):
        self.info_checked = isChecked

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
              "Invalid path.\n"
              "Path does either not exist or is not writable."), QMessageBox.Ok, QMessageBox.Ok)

    def world2pixel(self, x, y, mupp, minx, maxy):
        pixX = (x - minx)/mupp
        pixY = (y - maxy)/mupp
        return [int(pixX), int(-pixY)]

    # For given ring in feature, IF at least one point in ring is in 'mapCanvasExtent',
    # generate a string like:
    # <area data-info-id=x shape=polygon coords=519,-52,519,..,-52,519,-52 alt=...>
    def ring2html(self, feature, ring, extent, extentAsPoly):
        param = u''
        htm = u'<area data-info-id="{}" shape="poly" '.format(self.index)
        self.index = self.index + 1
        if hasattr(feature, 'attributeMap'):
            attrs = feature.attributeMap()
        else:
            # QGIS > 2.0
            attrs = feature
        # Escape ' and " because they will collapse as JavaScript parameter
        if self.imageMapPluginGui.isInfoBoxChecked():
            index = self.handleFieldIndexes(self.info_field_index, self.infoBoxAttributeField)
            param = unicode(attrs[index])
            self.info_boxes.append(self.removeNewLine(param))
        if self.imageMapPluginGui.isLabelChecked():
            index = self.handleFieldIndexes(self.label_field_index, self.labelAttributeField)
            param = unicode(attrs[index])
            self.labels.append(self.removeNewLine(param))
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
            alt = self.removeNewLine(param) if self.imageMapPluginGui.isLabelChecked() else "{}".format(self.index)
            htm += '" alt="' + u''.join(alt) + '">\n'
            return unicode(htm)

    # Returns the right index for virtual and non-virtual fields
    def handleFieldIndexes(self, index, field):
        # A negative index in this context means the field in question is a virtual one
        if index < 0:
            # This is a workaround, since the data provider cannot find virtual fields
            index = self.attr_fields.index("{}".format(field))
        return index

    # Transforms the coordinates of the current map canvas extent, so that it can then be used
    # for geometrical checks and as a filter
    def getTransformedMapCanvas(self):
        mapCanvasExtent = self.iface.mapCanvas().extent()
        self.doCrsTransform = False
        # In case of 'on the fly projection'.
        # Different srs's for mapCanvas/project and layer we have to reproject stuff
        if hasattr(self.iface.mapCanvas().mapSettings(), 'destinationSrs'):
            # QGIS < 2.0
            destinationCrs = self.iface.mapCanvas().mapSettings().destinationSrs()
            layerCrs = self.iface.activeLayer().srs()
        else:
            destinationCrs = self.iface.mapCanvas().mapSettings().destinationCrs()
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
                self.doCrsTransform = True
        return mapCanvasExtent

    # Returns a list of boundingBoxes representing the original geometry
    def geom2rect(self, geom):
        if geom.wkbType() == QGis.WKBPoint:  # 1 = WKBPoint
            return [geom.boundingBox()]
        if geom.wkbType() == QGis.WKBPolygon:  # 3 = WKBPolygon:
            return [geom.boundingBox()]
        if geom.wkbType() == QGis.WKBMultiPolygon:  # 6 = WKBMultiPolygon:
            multipolygon = geom.asMultiPolygon()
            return [geom.boundingBox() for polygon in multipolygon]

    # Returns the number of *selected* features (points/polygons/multi-polygons) within
    # the current map view
    def nofSelectedFeaturesInExtent(self):
        count = 0
        mapCanvasExtent = self.getTransformedMapCanvas()
        iter = self.iface.activeLayer().selectedFeatures()
        for feature in iter:
            geom = feature.geometry()
            if not geom is None:
                for rect in self.geom2rect(geom):
                    if mapCanvasExtent.intersects(rect):
                        count = count + 1
        return count

    # Prevent new lines inside JavaScript array
    def removeNewLine(self, str):
        return "".join(str.split("\n"))
