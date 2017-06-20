
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os.path

from qgis.core import QgsContextHelp
from qgis.core import QgsApplication

from ui_imagemapplugingui import Ui_ImageMapPluginGui

import imagemapplugin_rc


class ImageMapPluginGui(QDialog, Ui_ImageMapPluginGui):

  PATH_STRING = "Path and filename (no extension)"
  MSG_BOX_TITLE = "QGIS HTML Image Map Creator"

  def __init__(self, parent, fl):
    QDialog.__init__(self, parent, fl)
    self.setupUi(self)
    self.currentFileName = ""
    self.currentIconName = ""


  def on_buttonBox_accepted(self):
    # Make sure at least one checkbox is checked
    if (not self.chkBoxLabel.isChecked()) and (not self.chkBoxInfoBox.isChecked()):
      QMessageBox.warning(self, self.MSG_BOX_TITLE, ("Not a single option checked?\n" "Please choose at least one attribute to use on marker symbols."), QMessageBox.Ok)
      return
    self.emit(SIGNAL("getFilesPath(QString)"), self.txtFileName.text() )
    self.emit(SIGNAL("getIconFilePath(QString)"), self.txtIconFileName.text() )
    self.emit(SIGNAL("labelAttributeSet(QString)"), self.cmbLabelAttributes.currentText() )
    self.emit(SIGNAL("infoBoxAttributeSet(QString)"), self.cmbInfoBoxAttributes.currentText() )
    # and GO
    self.emit(SIGNAL("go(QString)"), "ok" )
    #self.done(1)   

  def on_buttonBox_rejected(self):
    self.done(0)

  def on_chkBoxSelectedOnly_stateChanged(self):
    self.emit(SIGNAL("getCbkBoxSelectedOnly(bool)"), self.chkBoxSelectedOnly.isChecked() )

  def on_chkBoxLabel_stateChanged(self):
    self.cmbLabelAttributes.setEnabled(self.chkBoxLabel.isChecked())
    
  def on_chkBoxInfoBox_stateChanged(self):
    self.cmbInfoBoxAttributes.setEnabled(self.chkBoxInfoBox.isChecked())
  
  # If the text in this field still begins with: 'full path and name'
  def on_txtFileName_cursorPositionChanged(self, old, new):
    if self.txtFileName.text().startswith(self.PATH_STRING):  # text() returns QString => startsWith instead startswith
        self.txtFileName.setText('')

  # see http://www.riverbankcomputing.com/Docs/PyQt4/pyqt4ref.html#connecting-signals-and-slots
  # without this magic, the on_btnOk_clicked will be called two times: one clicked() and one clicked(bool checked)
  @pyqtSignature("on_btnBrowse_clicked()")
  def on_btnBrowse_clicked(self):
    # Remember previously browsed directories
    if self.txtFileName.text() <> "":
        self.currentFileName = self.txtFileName.text()
    empty = self.currentFileName == ""
    # Set current default export directory to the recently browsed file directory
    saveFileName = QFileDialog.getSaveFileName(self, self.PATH_STRING, os.path.dirname(self.currentFileName) if not empty else "/", "")
    # If user clicks 'cancel' or enters empty string, the current file name is not overwritten
    if saveFileName <> "":
        self.currentFileName = saveFileName
    # If current file name is not empty, it is written into the line edit field
    if self.currentFileName <> "":
        self.txtFileName.setText(self.currentFileName)

  @pyqtSignature("on_btnIconFileBrowse_clicked()")  
  def on_btnIconFileBrowse_clicked(self):
    # Remember previously browsed directories
    if self.txtIconFileName.text() <> "":
        self.currentIconName = self.txtIconFileName.text()
    empty = self.currentIconName == ""
    svgPath = "/"
    # If there is a svg path at the index 0, use that as the initial default directory
    if QgsApplication.svgPaths()[0]:
        svgPath = QgsApplication.svgPaths()[0]
    # After this, set current default icon directory to the recently browsed icon directory
    saveIconName = QFileDialog.getSaveFileName(self, "Marker symbol", os.path.dirname(self.currentIconName) if not empty else svgPath, filter="*.svg;*.png;*.jpg", options=QFileDialog.DontConfirmOverwrite)
    # If user clicks 'cancel' or enters empty string, the current icon directory is not overwritten
    if saveIconName <> "":
        self.currentIconName = saveIconName
    # If current icon name is not empty, it is written into the line edit field
    if self.currentIconName <> "":
        self.txtIconFileName.setText(self.currentIconName)
    
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
    self.cmbLabelAttributes.addItems(layerAttr)
    self.cmbInfoBoxAttributes.addItems(layerAttr)

  def setProgressBarMax(self, maxInt):
    # minimum default to zero
    self.progressBar.setMinimum(0)
    self.progressBar.setMaximum(maxInt)
  
  def setProgressBarValue(self, valInt):
    self.progressBar.setValue(valInt)

  def isLabelChecked(self):
    return self.chkBoxLabel.isChecked()

  def isInfoBoxChecked(self):
    return self.chkBoxInfoBox.isChecked()