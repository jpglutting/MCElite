# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_MCElite.ui'
#
# Created: Thu Sep  9 13:10:50 2010
#      by: PyQt4 UI code generator 4.7.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MCElite(object):
    def setupUi(self, MCElite):
        MCElite.setObjectName(_fromUtf8("MCElite"))
        MCElite.resize(687, 266)
        self.tabWidget = QtGui.QTabWidget(MCElite)
        self.tabWidget.setGeometry(QtCore.QRect(30, 9, 620, 220))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tabBool = QtGui.QWidget()
        self.tabBool.setObjectName(_fromUtf8("tabBool"))
        self.labelConstraintsBool = QtGui.QLabel(self.tabBool)
        self.labelConstraintsBool.setGeometry(QtCore.QRect(10, 10, 151, 22))
        self.labelConstraintsBool.setMargin(1)
        self.labelConstraintsBool.setIndent(0)
        self.labelConstraintsBool.setObjectName(_fromUtf8("labelConstraintsBool"))
        self.labelFactorsBool = QtGui.QLabel(self.tabBool)
        self.labelFactorsBool.setGeometry(QtCore.QRect(245, 10, 121, 22))
        self.labelFactorsBool.setMargin(1)
        self.labelFactorsBool.setIndent(0)
        self.labelFactorsBool.setObjectName(_fromUtf8("labelFactorsBool"))
        self.tabWidget.addTab(self.tabBool, _fromUtf8(""))
        self.tabWLC = QtGui.QWidget()
        self.tabWLC.setObjectName(_fromUtf8("tabWLC"))
        self.labelConstraintsWLC = QtGui.QLabel(self.tabWLC)
        self.labelConstraintsWLC.setGeometry(QtCore.QRect(10, 10, 151, 22))
        self.labelConstraintsWLC.setMargin(1)
        self.labelConstraintsWLC.setIndent(0)
        self.labelConstraintsWLC.setObjectName(_fromUtf8("labelConstraintsWLC"))
        self.labelFactorsWLC = QtGui.QLabel(self.tabWLC)
        self.labelFactorsWLC.setGeometry(QtCore.QRect(245, 10, 121, 22))
        self.labelFactorsWLC.setMargin(1)
        self.labelFactorsWLC.setIndent(0)
        self.labelFactorsWLC.setObjectName(_fromUtf8("labelFactorsWLC"))
        self.labelSensitivityWLC = QtGui.QLabel(self.tabWLC)
        self.labelSensitivityWLC.setGeometry(QtCore.QRect(530, 0, 71, 41))
        self.labelSensitivityWLC.setMargin(1)
        self.labelSensitivityWLC.setIndent(0)
        self.labelSensitivityWLC.setObjectName(_fromUtf8("labelSensitivityWLC"))
        self.labelWeightsWLC = QtGui.QLabel(self.tabWLC)
        self.labelWeightsWLC.setGeometry(QtCore.QRect(460, 0, 51, 41))
        self.labelWeightsWLC.setMargin(1)
        self.labelWeightsWLC.setIndent(0)
        self.labelWeightsWLC.setObjectName(_fromUtf8("labelWeightsWLC"))
        self.tabWidget.addTab(self.tabWLC, _fromUtf8(""))
        self.tabOWA = QtGui.QWidget()
        self.tabOWA.setObjectName(_fromUtf8("tabOWA"))
        self.labelFactorsOWA = QtGui.QLabel(self.tabOWA)
        self.labelFactorsOWA.setGeometry(QtCore.QRect(245, 10, 121, 22))
        self.labelFactorsOWA.setMargin(1)
        self.labelFactorsOWA.setIndent(0)
        self.labelFactorsOWA.setObjectName(_fromUtf8("labelFactorsOWA"))
        self.labelConstraintsOWA = QtGui.QLabel(self.tabOWA)
        self.labelConstraintsOWA.setGeometry(QtCore.QRect(10, 10, 151, 22))
        self.labelConstraintsOWA.setMargin(1)
        self.labelConstraintsOWA.setIndent(0)
        self.labelConstraintsOWA.setObjectName(_fromUtf8("labelConstraintsOWA"))
        self.labelWeightsOWA = QtGui.QLabel(self.tabOWA)
        self.labelWeightsOWA.setGeometry(QtCore.QRect(460, 0, 51, 41))
        self.labelWeightsOWA.setMargin(1)
        self.labelWeightsOWA.setIndent(0)
        self.labelWeightsOWA.setObjectName(_fromUtf8("labelWeightsOWA"))
        self.labelSensitivityOWA = QtGui.QLabel(self.tabOWA)
        self.labelSensitivityOWA.setGeometry(QtCore.QRect(530, 0, 71, 41))
        self.labelSensitivityOWA.setMargin(1)
        self.labelSensitivityOWA.setIndent(0)
        self.labelSensitivityOWA.setObjectName(_fromUtf8("labelSensitivityOWA"))
        self.tabWidget.addTab(self.tabOWA, _fromUtf8(""))

        self.retranslateUi(MCElite)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MCElite)

    def retranslateUi(self, MCElite):
        MCElite.setWindowTitle(QtGui.QApplication.translate("MCElite", "MCElite", None, QtGui.QApplication.UnicodeUTF8))
        self.labelConstraintsBool.setText(QtGui.QApplication.translate("MCElite", "Number of Constraints", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFactorsBool.setText(QtGui.QApplication.translate("MCElite", "Number of Factors", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabBool), QtGui.QApplication.translate("MCElite", "Boolean", None, QtGui.QApplication.UnicodeUTF8))
        self.labelConstraintsWLC.setText(QtGui.QApplication.translate("MCElite", "Number of Constraints", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFactorsWLC.setText(QtGui.QApplication.translate("MCElite", "Number of Factors", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSensitivityWLC.setText(QtGui.QApplication.translate("MCElite", "Sensitivity\n"
"analysis", None, QtGui.QApplication.UnicodeUTF8))
        self.labelWeightsWLC.setText(QtGui.QApplication.translate("MCElite", "Factor\n"
"weights", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabWLC), QtGui.QApplication.translate("MCElite", "WLC", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFactorsOWA.setText(QtGui.QApplication.translate("MCElite", "Number of Factors", None, QtGui.QApplication.UnicodeUTF8))
        self.labelConstraintsOWA.setText(QtGui.QApplication.translate("MCElite", "Number of Constraints", None, QtGui.QApplication.UnicodeUTF8))
        self.labelWeightsOWA.setText(QtGui.QApplication.translate("MCElite", "Factor\n"
"weights", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSensitivityOWA.setText(QtGui.QApplication.translate("MCElite", "Sensitivity\n"
"analysis", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabOWA), QtGui.QApplication.translate("MCElite", "OWA", None, QtGui.QApplication.UnicodeUTF8))

