# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'html_image_map_creator_dialog_base.ui'
#
# Created: Tue Jun 20 09:17:59 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ImageMapPluginGui(object):
    def setupUi(self, ImageMapPluginGui):
        ImageMapPluginGui.setObjectName(_fromUtf8("ImageMapPluginGui"))
        ImageMapPluginGui.resize(900, 513)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ImageMapPluginGui.setWindowIcon(icon)
        self.gridLayout = QtGui.QGridLayout(ImageMapPluginGui)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(ImageMapPluginGui)
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8(":/imagemap.png")))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 3, 1)
        self.line1 = QtGui.QFrame(ImageMapPluginGui)
        self.line1.setMaximumSize(QtCore.QSize(2, 32767))
        self.line1.setFrameShape(QtGui.QFrame.VLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setFrameShape(QtGui.QFrame.VLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setObjectName(_fromUtf8("line1"))
        self.gridLayout.addWidget(self.line1, 0, 1, 3, 1)
        self.txtHeading = QtGui.QLabel(ImageMapPluginGui)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtHeading.sizePolicy().hasHeightForWidth())
        self.txtHeading.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Sans Serif"))
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setStrikeOut(False)
        self.txtHeading.setFont(font)
        self.txtHeading.setAlignment(QtCore.Qt.AlignCenter)
        self.txtHeading.setObjectName(_fromUtf8("txtHeading"))
        self.gridLayout.addWidget(self.txtHeading, 0, 2, 1, 1)
        self.textEdit = QtGui.QTextEdit(ImageMapPluginGui)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout.addWidget(self.textEdit, 1, 2, 1, 1)
        self.progressBar = QtGui.QProgressBar(ImageMapPluginGui)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.gridLayout.addWidget(self.progressBar, 3, 0, 1, 3)
        self.buttonBox = QtGui.QDialogButtonBox(ImageMapPluginGui)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.gridLayout_3 = QtGui.QGridLayout()
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.lblDimensions = QtGui.QLabel(ImageMapPluginGui)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblDimensions.sizePolicy().hasHeightForWidth())
        self.lblDimensions.setSizePolicy(sizePolicy)
        self.lblDimensions.setObjectName(_fromUtf8("lblDimensions"))
        self.gridLayout_3.addWidget(self.lblDimensions, 1, 0, 1, 1)
        self.lblActiveLayer = QtGui.QLabel(ImageMapPluginGui)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblActiveLayer.sizePolicy().hasHeightForWidth())
        self.lblActiveLayer.setSizePolicy(sizePolicy)
        self.lblActiveLayer.setObjectName(_fromUtf8("lblActiveLayer"))
        self.gridLayout_3.addWidget(self.lblActiveLayer, 2, 0, 1, 1)
        self.lblFilename = QtGui.QLabel(ImageMapPluginGui)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFilename.sizePolicy().hasHeightForWidth())
        self.lblFilename.setSizePolicy(sizePolicy)
        self.lblFilename.setObjectName(_fromUtf8("lblFilename"))
        self.gridLayout_3.addWidget(self.lblFilename, 3, 0, 1, 1)
        self.btnBrowse = QtGui.QPushButton(ImageMapPluginGui)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.gridLayout_3.addWidget(self.btnBrowse, 3, 3, 1, 1)
        self.lblIconFileName = QtGui.QLabel(ImageMapPluginGui)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblIconFileName.sizePolicy().hasHeightForWidth())
        self.lblIconFileName.setSizePolicy(sizePolicy)
        self.lblIconFileName.setObjectName(_fromUtf8("lblIconFileName"))
        self.gridLayout_3.addWidget(self.lblIconFileName, 4, 0, 1, 1)
        self.btnIconFileBrowse = QtGui.QPushButton(ImageMapPluginGui)
        self.btnIconFileBrowse.setObjectName(_fromUtf8("btnIconFileBrowse"))
        self.gridLayout_3.addWidget(self.btnIconFileBrowse, 4, 3, 1, 1)
        self.txtIconFileName = QtGui.QLineEdit(ImageMapPluginGui)
        self.txtIconFileName.setObjectName(_fromUtf8("txtIconFileName"))
        self.gridLayout_3.addWidget(self.txtIconFileName, 4, 1, 1, 2)
        self.chkBoxOnClick = QtGui.QCheckBox(ImageMapPluginGui)
        self.chkBoxOnClick.setObjectName(_fromUtf8("chkBoxOnClick"))
        self.gridLayout_3.addWidget(self.chkBoxOnClick, 5, 0, 1, 1)
        self.cmbAttributesOnClick = QtGui.QComboBox(ImageMapPluginGui)
        self.cmbAttributesOnClick.setEnabled(False)
        self.cmbAttributesOnClick.setObjectName(_fromUtf8("cmbAttributesOnClick"))
        self.gridLayout_3.addWidget(self.cmbAttributesOnClick, 5, 1, 1, 3)
        self.chkBoxOnMouseOver = QtGui.QCheckBox(ImageMapPluginGui)
        self.chkBoxOnMouseOver.setObjectName(_fromUtf8("chkBoxOnMouseOver"))
        self.gridLayout_3.addWidget(self.chkBoxOnMouseOver, 6, 0, 1, 1)
        self.cmbAttributesOnMouseOver = QtGui.QComboBox(ImageMapPluginGui)
        self.cmbAttributesOnMouseOver.setEnabled(False)
        self.cmbAttributesOnMouseOver.setObjectName(_fromUtf8("cmbAttributesOnMouseOver"))
        self.gridLayout_3.addWidget(self.cmbAttributesOnMouseOver, 6, 1, 1, 3)
        self.txtFileName = QtGui.QLineEdit(ImageMapPluginGui)
        self.txtFileName.setObjectName(_fromUtf8("txtFileName"))
        self.gridLayout_3.addWidget(self.txtFileName, 3, 1, 1, 2)
        self.txtDimensions = QtGui.QLabel(ImageMapPluginGui)
        self.txtDimensions.setObjectName(_fromUtf8("txtDimensions"))
        self.gridLayout_3.addWidget(self.txtDimensions, 1, 1, 1, 1)
        self.txtLayerName = QtGui.QLineEdit(ImageMapPluginGui)
        self.txtLayerName.setEnabled(False)
        self.txtLayerName.setObjectName(_fromUtf8("txtLayerName"))
        self.gridLayout_3.addWidget(self.txtLayerName, 2, 1, 1, 2)
        self.chkBoxSelectedOnly = QtGui.QCheckBox(ImageMapPluginGui)
        self.chkBoxSelectedOnly.setObjectName(_fromUtf8("chkBoxSelectedOnly"))
        self.gridLayout_3.addWidget(self.chkBoxSelectedOnly, 9, 0, 1, 2)
        self.featureCount = QtGui.QLabel(ImageMapPluginGui)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.featureCount.sizePolicy().hasHeightForWidth())
        self.featureCount.setSizePolicy(sizePolicy)
        self.featureCount.setText(_fromUtf8(""))
        self.featureCount.setObjectName(_fromUtf8("featureCount"))
        self.gridLayout_3.addWidget(self.featureCount, 9, 1, 1, 3)
        self.gridLayout.addLayout(self.gridLayout_3, 2, 2, 1, 1)

        self.retranslateUi(ImageMapPluginGui)
        QtCore.QMetaObject.connectSlotsByName(ImageMapPluginGui)

    def retranslateUi(self, ImageMapPluginGui):
        ImageMapPluginGui.setWindowTitle(_translate("ImageMapPluginGui", "HTML Image Map Creator", None))
        self.textEdit.setHtml(_translate("ImageMapPluginGui", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">This plugin will create an HTML file along with a corresponding PNG file taken from the current map view. </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\'; font-size:6pt;\"> </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">- It can be used on any active point or (multi-)polygon vector layer (Geopackage, Shapefile etc.).</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">- The marker symbol of your choosing will be copied over to the export directory.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Sans Serif\';\">- The marker label and the body of the infobox will use the individual field attribute as their text and look like as shown in the picture on the left.</span></p></body></html>", None))
        self.lblDimensions.setText(_translate("ImageMapPluginGui", "Image dimensions", None))
        self.lblActiveLayer.setText(_translate("ImageMapPluginGui", "Active layer", None))
        self.lblFilename.setText(_translate("ImageMapPluginGui", "Export path and filename", None))
        self.btnBrowse.setText(_translate("ImageMapPluginGui", "Browse", None))
        self.lblIconFileName.setText(_translate("ImageMapPluginGui", "Marker symbol", None))
        self.btnIconFileBrowse.setText(_translate("ImageMapPluginGui", "Browse", None))
        self.chkBoxOnClick.setText(_translate("ImageMapPluginGui", "Marker label", None))
        self.chkBoxOnMouseOver.setText(_translate("ImageMapPluginGui", "Body of infobox", None))
        self.txtFileName.setText(_translate("ImageMapPluginGui", "Path and name without extension", None))
        self.chkBoxSelectedOnly.setText(_translate("ImageMapPluginGui", "Selected features only", None))

import resources_rc
