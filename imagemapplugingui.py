from PyQt4.QtCore import *
from PyQt4.QtGui import *

import os.path
from os.path import expanduser

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
        self.label_components = [self.cmbLabelAttributes, self.lblLabelOffset, self.spinBoxLabel, self.lblLabelPixel]
        self.info_components = [self.cmbInfoBoxAttributes, self.lblInfoOffset, self.spinBoxInfo, self.lblInfoPixel]

    def on_buttonBox_accepted(self):
        self.emit(SIGNAL("getFilesPath(QString)"), self.txtFileName.text())
        self.emit(SIGNAL("labelAttributeSet(QString)"), self.cmbLabelAttributes.currentText())
        self.emit(SIGNAL("spinLabelSet(int)"), self.spinBoxLabel.value())
        self.emit(SIGNAL("getCbkBoxLabel(bool)"), self.chkBoxLabel.isChecked())
        self.emit(SIGNAL("infoBoxAttributeSet(QString)"), self.cmbInfoBoxAttributes.currentText())
        self.emit(SIGNAL("spinInfoSet(int)"), self.spinBoxInfo.value())
        self.emit(SIGNAL("getCbkBoxInfo(bool)"), self.chkBoxInfoBox.isChecked())
        self.emit(SIGNAL("getLayerName(QString)"), self.txtLayerName.text())
        # and GO
        self.emit(SIGNAL("go(QString)"), "ok")

    def on_buttonBox_rejected(self):
        self.done(0)

    def on_chkBoxSelectedOnly_stateChanged(self):
        self.emit(SIGNAL("getCbkBoxSelectedOnly(bool)"), self.chkBoxSelectedOnly.isChecked())

    def on_chkBoxLabel_stateChanged(self):
        for label_comp in self.label_components:
            label_comp.setEnabled(self.chkBoxLabel.isChecked())
        self.emit(SIGNAL("getCurrentLabelState(bool)"), self.chkBoxLabel.isChecked())

    def on_chkBoxInfoBox_stateChanged(self):
        for info_comp in self.info_components:
            info_comp.setEnabled(self.chkBoxInfoBox.isChecked())
        self.emit(SIGNAL("getCurrentInfoState(bool)"), self.chkBoxInfoBox.isChecked())

    # If the text in this field still begins with: 'full path and name'
    def on_txtFileName_cursorPositionChanged(self, old, new):
        if self.txtFileName.text().startswith(self.PATH_STRING):
            self.txtFileName.setText('')

    # See http://www.riverbankcomputing.com/Docs/PyQt4/pyqt4ref.html#connecting-signals-and-slots
    # Without this magic, the on_btnOk_clicked will be called two times: one clicked() and one clicked(bool checked)
    @pyqtSignature("on_btnBrowse_clicked()")
    def on_btnBrowse_clicked(self):
        current_file_name = ""
        # Remember previously browsed directories
        if self.txtFileName.text():
            current_file_name = self.txtFileName.text()
        # Set current default export directory to the recently browsed file directory,
        # if it is empty or it does not exist, fall back to user home directory
        current_path = os.path.dirname(current_file_name)
        exists = os.path.exists(current_path)
        default_path = current_path if exists else expanduser("~")
        save_filename = QFileDialog.getSaveFileName(self, self.PATH_STRING, default_path, "")
        # If user clicks 'cancel' the current file name is not overwritten
        if save_filename:
            dir = os.path.dirname(save_filename)
            filename = os.path.basename(save_filename).rsplit(".", 1)[0]
            self.txtFileName.setText(u'{}/{}'.format(dir, filename))

    # SIGNAL slots:
    def setFilesPath(self, path):
        self.txtFileName.setText(path)

    def setLayerName(self, name):
        self.txtLayerName.setText(name)

    def setFeatureTotal(self, total):
        self.featureTotal.setText(total)

    def setDimensions(self, dimensions):
        self.txtDimensions.setText(dimensions)

    def setFeatureCount(self, count):
        self.featureCount.setText(count)

    def setAttributeFields(self, layerAttr):
        # Populate comboboxes with attribute field names of active layer
        self.cmbLabelAttributes.addItems(layerAttr)
        self.cmbInfoBoxAttributes.addItems(layerAttr)

    def setProgressBarMax(self, maxInt):
        # Minimum default to zero
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(maxInt)

    def setProgressBarValue(self, valInt):
        self.progressBar.setValue(valInt)

    def setOkButtonState(self, state):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(state)

    def isLabelChecked(self):
        return self.chkBoxLabel.isChecked()

    def isInfoBoxChecked(self):
        return self.chkBoxInfoBox.isChecked()
