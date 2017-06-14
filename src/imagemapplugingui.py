
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os.path

from qgis.core import QgsContextHelp
from qgis.core import QgsApplication

from ui_imagemapplugingui import Ui_ImageMapPluginGui

import imagemapplugin_rc


class ImageMapPluginGui(QDialog, Ui_ImageMapPluginGui):

  PATH_STRING = "Path and file name (no extension)"
  MSG_BOX_TITLE = "QGIS HTML Image Map Creator"

  def __init__(self, parent, fl):
    QDialog.__init__(self, parent, fl)
    self.setupUi(self)


  def on_buttonBox_accepted(self):
    # Make sure at least one checkbox is checked
    if (not self.chkBoxOnClick.isChecked()) and (not self.chkBoxOnMouseOver.isChecked()):
      QMessageBox.warning(self, self.MSG_BOX_TITLE, ("Not a single option checked?\n" "Please choose at least one attribute to use on marker symbols."), QMessageBox.Ok)
      return
    self.emit(SIGNAL("getFilesPath(QString)"), self.txtFileName.text() )
    self.emit(SIGNAL("getIconFilePath(QString)"), self.txtIconFileName.text() )
    self.emit(SIGNAL("onClickAttributeSet(QString)"), self.cmbAttributesOnClick.currentText() )
    self.emit(SIGNAL("onMouseOverAttributeSet(QString)"), self.cmbAttributesOnMouseOver.currentText() )
    # and GO
    self.emit(SIGNAL("go(QString)"), "ok" )
    #self.done(1)   

  def on_buttonBox_rejected(self):
    self.done(0)

  def on_chkBoxSelectedOnly_stateChanged(self):
    self.emit(SIGNAL("getCbkBoxSelectedOnly(bool)"), self.chkBoxSelectedOnly.isChecked() )

  def on_chkBoxOnClick_stateChanged(self):
    self.cmbAttributesOnClick.setEnabled(self.chkBoxOnClick.isChecked())

  def on_chkBoxOnMouseOver_stateChanged(self):
    self.cmbAttributesOnMouseOver.setEnabled(self.chkBoxOnMouseOver.isChecked())
  
  # if the text in this field is stil beginning with: 'full path and name'
  def on_txtFileName_cursorPositionChanged(self, old, new):
    if self.txtFileName.text().startswith(self.PATH_STRING):  # text() returns QString => startsWith instead startswith
        self.txtFileName.setText('')

  # see http://www.riverbankcomputing.com/Docs/PyQt4/pyqt4ref.html#connecting-signals-and-slots
  # without this magic, the on_btnOk_clicked will be called two times: one clicked() and one clicked(bool checked)
  @pyqtSignature("on_btnBrowse_clicked()")
  def on_btnBrowse_clicked(self):
    fileName = QFileDialog.getSaveFileName(self, self.PATH_STRING, "/", "")
    self.txtFileName.setText(fileName)

  @pyqtSignature("on_btnIconFileBrowse_clicked()")  
  def on_btnIconFileBrowse_clicked(self):
    fileName = QFileDialog.getSaveFileName(self, "Marker symbol", QgsApplication.svgPaths()[0], filter="*.svg;*.png;*.jpg", options=QFileDialog.DontConfirmOverwrite)
    self.txtIconFileName.setText(fileName)
    
  def setFilesPath(self, path):
    self.txtFileName.setText(path)

  def setIconFilePath(self, path):
    self.txtIconFileName.setText(path)
    
  def setLayerName(self, name):
    self.txtLayerName.setText(name)
  
  def setDimensions(self, dimensions):
    self.txtDimensions.setText(dimensions)
    
  def setFeatureCount(self, count):
    self.featureCount.setText(count)
  
  def setAttributeFields(self, layerAttr):
    # populate comboboxes with attribute field names of active layer
    self.cmbAttributesOnClick.addItems(layerAttr)
    self.cmbAttributesOnMouseOver.addItems(layerAttr)

  def setProgressBarMax(self, maxInt):
    # minimum default to zero
    self.progressBar.setMinimum(0)
    self.progressBar.setMaximum(maxInt)

  def setMapCanvasSize(self, width, height):
    pass
    # self.spinBoxImageWidth.setValue(width)
    # self.spinBoxImageHeight.setValue(height)
  
  def setProgressBarValue(self, valInt):
    self.progressBar.setValue(valInt)

  def isOnClickChecked(self):
    return self.chkBoxOnClick.isChecked()

  def isOnMouseOverChecked(self):
    return self.chkBoxOnMouseOver.isChecked()