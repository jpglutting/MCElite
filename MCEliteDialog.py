# -*- coding: utf-8 -*-

"""
***************************************************************************
MCElite
Multiple Criteria Analysis tool
-------------------
begin                : 2010-08-27 
copyright            : (C) 2010 by JP Glutting
email                : jpglutting@gmail.com 
***************************************************************************

***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

"""
import os
import string
from sys import exc_info

from PyQt4 import QtCore, QtGui 
from qgis.core import QgsRasterLayer, QgsContrastEnhancement, QgsMapLayerRegistry
from Ui_MCElite import Ui_MCElite
from lib.QueryManager import QgisQueryManager
from lib.MCErrorClasses import MCEliteError

# create the dialog for zoom to point
class MCEliteDialog(QtGui.QDialog):
    def __init__(self): 
        QtGui.QDialog.__init__(self) 
        # Set up the user interface from Designer, and embed it in the MCEliteDialog object for easy access. 
        # Ui_MCElite creates the main window, the tabs and fixed items.
        # Everything else is created here.
        self.ui = Ui_MCElite()
        self.ui.setupUi(self) 
        # Create and embed a QueryManager (QGIS, in this case) for easy access
        # The QueryManager will handle all query parameters and the creation of QueryObjects, RasterObjects, results files, etc.
        self.qm = QgisQueryManager()
        # Set basic parameters for Window
        self.MCEType = None # ['Bool', 'WLC' 'OWA']
        self.maxRows = 10
        self.rows = range(self.maxRows)
        self.gdal_output_formats = self.qm.gdal_output_formats
        self.output_format = None
        # Saves references to the visible range of elements
        self.dmaxvisible = {'rows':0, 'constraints':0, 'factors':0} 
        self.lastdirused = ''
        self.configurationFile = None
        self.winW = 700
        self.winH = 360
        self.resize(self.winW, self.winH)
        self.tabW = self.winW - 20
        self.tabH = self.winH - 20
        self.okW = 160
        self.okH = 32
        self.okOffsetW = 180
        self.okOffsetH = 60
        self.yBase = 50
        self.yMod = 30
        # User Interface Dictionary
        self.uid = {}
        self.moveableWidgets = []
        self.suffixD = {1:'st', 2:'nd', 3:'rd'}
        self.tabD = {'Bool':{'parent':self.ui.tabBool, 
                             'criteria':{'constraints':['filepath', 'button'],
                                       'factors':['filepath', 'button']
                                         },
                             'sum':[], 
                             'tabid':0, },
                    'WLC':{'parent':self.ui.tabWLC, 
                           'criteria':{'constraints':['filepath', 'button'], 
                                       'factors':['filepath', 'button', 'weights', 'checkbox']
                                       }, 
                             'sum':['weights',],
                             'tabid':1,},
                    'OWA':{'parent':self.ui.tabOWA,
                           'criteria':{'constraints':['filepath', 'button'], 
                                       'factors':['filepath', 'button', 'weights', 'oweights', 'checkbox']
                                       }, 
                             'sum':['weights','oweights'],
                             'tabid':2,},
                                }
        self.widgetd = {'filepath': {'gen':QtGui.QLineEdit, 'width': 120, 'height':22, 'yBase':self.yBase+2,
                                                         'xdict':{'constraints':10, 'factors':240}, 'slot':None, 'signal':None},
                        'button': {'gen':QtGui.QPushButton, 'width': 80, 'height':32, 'yBase':self.yBase,
                                                         'xdict':{'constraints':130, 'factors':360}, 'slot':self.slotOpenRasterFile, 'signal':'clicked()'},
                        'weights': {'gen':QtGui.QLineEdit, 'width':50, 'height':22, 'yBase':self.yBase+2, 'xdict':{'factors':460}, 'slot':None, 'signal':None},
                        'oweights': {'gen':QtGui.QLineEdit, 'width':40, 'height':22, 'xbase':10, 'xmod':50, 'slot':None, 'signal':None},
                        'checkbox': {'gen':QtGui.QCheckBox, 'width':80, 'height':22, 'yBase':self.yBase+2, 'xdict':{'factors':530}, 'slot':None, 'signal':None},
                         }
        
        # SET USER INTERFACE (UI) PARAMETERS
        # Set tab geometry
        self.ui.tabWidget.setGeometry(QtCore.QRect(10, 9, self.tabW, self.tabH))
        self.ui.tabWidget.setCurrentIndex(0)

        # Combo Boxes
        # Bool
        self.ui.comboNumberConstraintsBool = QtGui.QComboBox(self.ui.tabBool)
        self.ui.comboNumberConstraintsBool.setGeometry(QtCore.QRect(170, 10, 55, 26))
        self.ui.comboNumberConstraintsBool.setObjectName("comboNumberConstraintsBool")
        self.ui.comboNumberFactorsBool = QtGui.QComboBox(self.ui.tabBool)
        self.ui.comboNumberFactorsBool.setGeometry(QtCore.QRect(370, 10, 55, 26))
        self.ui.comboNumberFactorsBool.setObjectName("comboNumberFactorsBool")
        # WLC
        self.ui.comboNumberConstraintsWLC = QtGui.QComboBox(self.ui.tabWLC)
        self.ui.comboNumberConstraintsWLC.setGeometry(QtCore.QRect(170, 10, 55, 26))
        self.ui.comboNumberConstraintsWLC.setObjectName("comboNumberConstraintsWLC")
        self.ui.comboNumberFactorsWLC = QtGui.QComboBox(self.ui.tabWLC)
        self.ui.comboNumberFactorsWLC.setGeometry(QtCore.QRect(370, 10, 55, 26))
        self.ui.comboNumberFactorsWLC.setObjectName("comboNumberFactorsWLC")
        # OWA
        self.ui.comboNumberConstraintsOWA = QtGui.QComboBox(self.ui.tabOWA)
        self.ui.comboNumberConstraintsOWA.setGeometry(QtCore.QRect(170, 10, 55, 26))
        self.ui.comboNumberConstraintsOWA.setObjectName("comboNumberConstraintsOWA")
        self.ui.comboNumberFactorsOWA = QtGui.QComboBox(self.ui.tabOWA)
        self.ui.comboNumberFactorsOWA.setGeometry(QtCore.QRect(370, 10, 55, 26))
        self.ui.comboNumberFactorsOWA.setObjectName("comboNumberFactorsOWA")
        for ix in range(self.maxRows):
            ixstr = str(ix+1)
            self.ui.comboNumberConstraintsBool.addItem("")
            self.ui.comboNumberFactorsBool.addItem("")
            self.ui.comboNumberConstraintsWLC.addItem("")
            self.ui.comboNumberFactorsWLC.addItem("")
            self.ui.comboNumberConstraintsOWA.addItem("")
            self.ui.comboNumberFactorsOWA.addItem("")
            self.ui.comboNumberConstraintsBool.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))
            self.ui.comboNumberFactorsBool.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))
            self.ui.comboNumberConstraintsWLC.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))
            self.ui.comboNumberFactorsWLC.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))
            self.ui.comboNumberConstraintsOWA.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))
            self.ui.comboNumberFactorsOWA.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))

        # Sensitivity input
        # WLC
#        self.ui.sensRadioWLC = QtGui.QButtonGroup(self.ui.tabWLC)
        #
        self.ui.buttonSensitivityAllWLC = QtGui.QPushButton(self.ui.tabWLC)
        self.ui.buttonSensitivityAllWLC.setGeometry(QtCore.QRect(530, self.yBase+(1*self.yMod), 95, 32))
        self.ui.buttonSensitivityAllWLC.setObjectName('WLC_all_factor_button')
        self.ui.buttonSensitivityAllWLC.setText(QtGui.QApplication.translate('MCElite', 'All Factors', None, QtGui.QApplication.UnicodeUTF8))
#        self.ui.sensRadioWLC.addButton(self.ui.buttonSensitivityAllWLC, 999)
        self.moveableWidgets.append(self.ui.buttonSensitivityAllWLC)
        self.ui.buttonSensitivityClearWLC = QtGui.QPushButton(self.ui.tabWLC)
        self.ui.buttonSensitivityClearWLC.setGeometry(QtCore.QRect(530, self.yBase+(2*self.yMod), 125, 32))
        self.ui.buttonSensitivityClearWLC.setObjectName('WLC_none_factor_button')
        self.ui.buttonSensitivityClearWLC.setText(QtGui.QApplication.translate('MCElite', 'Clear Factors', None, QtGui.QApplication.UnicodeUTF8))
        self.ui.buttonSensitivityClearWLC.setChecked(True)
#        self.ui.sensRadioWLC.addButton(self.ui.buttonSensitivityClearWLC, -999)
        self.moveableWidgets.append(self.ui.buttonSensitivityClearWLC)
        self.ui.sensMinWLC = QtGui.QLineEdit(self.ui.tabWLC)
        self.ui.sensMinWLC.setGeometry(QtCore.QRect(200, self.yBase+(4*self.yMod), 40, 22))
        self.ui.sensMinWLC.setObjectName('sensMinWLC')
        self.ui.sensMinWLC.setText(QtGui.QApplication.translate("MCElite", "-0.2", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensMinWLC)
        self.ui.sensMaxWLC = QtGui.QLineEdit(self.ui.tabWLC)
        self.ui.sensMaxWLC.setGeometry(QtCore.QRect(300, self.yBase+(4*self.yMod), 40, 22))
        self.ui.sensMaxWLC.setObjectName('sensMaxWLC')
        self.ui.sensMaxWLC.setText(QtGui.QApplication.translate("MCElite", "0.2", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensMaxWLC)
        self.ui.sensStepWLC = QtGui.QLineEdit(self.ui.tabWLC)
        self.ui.sensStepWLC.setGeometry(QtCore.QRect(400, self.yBase+(4*self.yMod), 40, 22))
        self.ui.sensStepWLC.setObjectName('sensStepWLC')
        self.ui.sensStepWLC.setText(QtGui.QApplication.translate("MCElite", "0.05", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensStepWLC)
        self.ui.sensThresholdWLC = QtGui.QLineEdit(self.ui.tabWLC)
        self.ui.sensThresholdWLC.setGeometry(QtCore.QRect(500, self.yBase+(4*self.yMod), 50, 22))
        self.ui.sensThresholdWLC.setObjectName('sensThresholdWLC')
        self.ui.sensThresholdWLC.setText(QtGui.QApplication.translate("MCElite", "175", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensThresholdWLC)
        # WLC sensitivity labels
        self.ui.labelSensitivityRangeWLC = QtGui.QLabel(self.ui.tabWLC)
        self.ui.labelSensitivityRangeWLC.setGeometry(QtCore.QRect(330, self.yBase+(3*self.yMod), 200, 22))
        self.ui.labelSensitivityRangeWLC.setMargin(1)
        self.ui.labelSensitivityRangeWLC.setIndent(0)
        self.ui.labelSensitivityRangeWLC.setObjectName("labelSensitivityRangeWLC")
        self.ui.labelSensitivityRangeWLC.setText(QtGui.QApplication.translate("MCElite", "<b>Sensitivity Analysis Range</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeWLC)
        self.ui.labelSensitivityRangeMinWLC = QtGui.QLabel(self.ui.tabWLC)
        self.ui.labelSensitivityRangeMinWLC.setGeometry(QtCore.QRect(250, self.yBase+(4*self.yMod), 30, 22))
        self.ui.labelSensitivityRangeMinWLC.setMargin(1)
        self.ui.labelSensitivityRangeMinWLC.setIndent(0)
        self.ui.labelSensitivityRangeMinWLC.setObjectName("labelSensitivityRangeMinWLC")
        self.ui.labelSensitivityRangeMinWLC.setText(QtGui.QApplication.translate("MCElite", "Min", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeMinWLC)
        self.ui.labelSensitivityRangeMaxWLC = QtGui.QLabel(self.ui.tabWLC)
        self.ui.labelSensitivityRangeMaxWLC.setGeometry(QtCore.QRect(350, self.yBase+(4*self.yMod), 30, 22))
        self.ui.labelSensitivityRangeMaxWLC.setMargin(1)
        self.ui.labelSensitivityRangeMaxWLC.setIndent(0)
        self.ui.labelSensitivityRangeMaxWLC.setObjectName("labelSensitivityRangeMaxWLC")
        self.ui.labelSensitivityRangeMaxWLC.setText(QtGui.QApplication.translate("MCElite", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeMaxWLC)
        self.ui.labelSensitivityRangeStepWLC = QtGui.QLabel(self.ui.tabWLC)
        self.ui.labelSensitivityRangeStepWLC.setGeometry(QtCore.QRect(450, self.yBase+(4*self.yMod), 30, 22))
        self.ui.labelSensitivityRangeStepWLC.setMargin(1)
        self.ui.labelSensitivityRangeStepWLC.setIndent(0)
        self.ui.labelSensitivityRangeStepWLC.setObjectName("labelSensitivityRangeStepWLC")
        self.ui.labelSensitivityRangeStepWLC.setText(QtGui.QApplication.translate("MCElite", "Step", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeStepWLC)
        self.ui.labelSensitivityRangeThresholdWLC = QtGui.QLabel(self.ui.tabWLC)
        self.ui.labelSensitivityRangeThresholdWLC.setGeometry(QtCore.QRect(555, self.yBase+(4*self.yMod), 80, 22))
        self.ui.labelSensitivityRangeThresholdWLC.setMargin(1)
        self.ui.labelSensitivityRangeThresholdWLC.setIndent(0)
        self.ui.labelSensitivityRangeThresholdWLC.setObjectName("labelSensitivityRangeThresholdWLC")
        self.ui.labelSensitivityRangeThresholdWLC.setText(QtGui.QApplication.translate("MCElite", "Threshold", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeThresholdWLC)
        # OWA
        #
        self.ui.buttonSensitivityAllOWA = QtGui.QPushButton(self.ui.tabOWA)
        self.ui.buttonSensitivityAllOWA.setGeometry(QtCore.QRect(530, self.yBase+(1*self.yMod), 95, 32))
        self.ui.buttonSensitivityAllOWA.setObjectName('OWA_all_factor_button')
        self.ui.buttonSensitivityAllOWA.setText(QtGui.QApplication.translate('MCElite', 'All Factors', None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.buttonSensitivityAllOWA)
        #
        self.ui.buttonSensitivityClearOWA = QtGui.QPushButton(self.ui.tabOWA)
        self.ui.buttonSensitivityClearOWA.setGeometry(QtCore.QRect(530, self.yBase+(2*self.yMod), 125, 32))
        self.ui.buttonSensitivityClearOWA.setObjectName('OWA_none_factor_button')
        self.ui.buttonSensitivityClearOWA.setText(QtGui.QApplication.translate('MCElite', 'Clear Factors', None, QtGui.QApplication.UnicodeUTF8))
        self.ui.buttonSensitivityClearOWA.setChecked(True)
        self.moveableWidgets.append(self.ui.buttonSensitivityClearOWA)
        #
        self.ui.sensMinOWA = QtGui.QLineEdit(self.ui.tabOWA)
        self.ui.sensMinOWA.setGeometry(QtCore.QRect(200, self.yBase+(4*self.yMod), 40, 22))
        self.ui.sensMinOWA.setObjectName('sensMinOWA')
        self.ui.sensMinOWA.setText(QtGui.QApplication.translate("MCElite", "-0.2", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensMinOWA)
        #
        self.ui.sensMaxOWA = QtGui.QLineEdit(self.ui.tabOWA)
        self.ui.sensMaxOWA.setGeometry(QtCore.QRect(300, self.yBase+(4*self.yMod), 40, 22))
        self.ui.sensMaxOWA.setObjectName('sensMaxOWA')
        self.ui.sensMaxOWA.setText(QtGui.QApplication.translate("MCElite", "0.2", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensMaxOWA)
        #
        self.ui.sensStepOWA = QtGui.QLineEdit(self.ui.tabOWA)
        self.ui.sensStepOWA.setGeometry(QtCore.QRect(400, self.yBase+(4*self.yMod), 40, 22))
        self.ui.sensStepOWA.setObjectName('sensStepOWA')
        self.ui.sensStepOWA.setText(QtGui.QApplication.translate("MCElite", "0.05", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensStepOWA)
        #
        self.ui.sensThresholdOWA = QtGui.QLineEdit(self.ui.tabOWA)
        self.ui.sensThresholdOWA.setGeometry(QtCore.QRect(500, self.yBase+(4*self.yMod), 50, 22))
        self.ui.sensThresholdOWA.setObjectName('sensThresholdOWA')
        self.ui.sensThresholdOWA.setText(QtGui.QApplication.translate("MCElite", "175", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.sensThresholdOWA)
        # OWA sensitivity labels
        self.ui.labelSensitivityRangeOWA = QtGui.QLabel(self.ui.tabOWA)
        self.ui.labelSensitivityRangeOWA.setGeometry(QtCore.QRect(330, self.yBase+(3*self.yMod), 200, 22))
        self.ui.labelSensitivityRangeOWA.setMargin(1)
        self.ui.labelSensitivityRangeOWA.setIndent(0)
        self.ui.labelSensitivityRangeOWA.setObjectName("labelSensitivityRangeOWA")
        self.ui.labelSensitivityRangeOWA.setText(QtGui.QApplication.translate("MCElite", "<b>Sensitivity Analysis Range</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeOWA)
        self.ui.labelSensitivityRangeMinOWA = QtGui.QLabel(self.ui.tabOWA)
        self.ui.labelSensitivityRangeMinOWA.setGeometry(QtCore.QRect(250, self.yBase+(4*self.yMod), 30, 22))
        self.ui.labelSensitivityRangeMinOWA.setMargin(1)
        self.ui.labelSensitivityRangeMinOWA.setIndent(0)
        self.ui.labelSensitivityRangeMinOWA.setObjectName("labelSensitivityRangeMinOWA")
        self.ui.labelSensitivityRangeMinOWA.setText(QtGui.QApplication.translate("MCElite", "Min", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeMinOWA)
        self.ui.labelSensitivityRangeMaxOWA = QtGui.QLabel(self.ui.tabOWA)
        self.ui.labelSensitivityRangeMaxOWA.setGeometry(QtCore.QRect(350, self.yBase+(4*self.yMod), 30, 22))
        self.ui.labelSensitivityRangeMaxOWA.setMargin(1)
        self.ui.labelSensitivityRangeMaxOWA.setIndent(0)
        self.ui.labelSensitivityRangeMaxOWA.setObjectName("labelSensitivityRangeMaxOWA")
        self.ui.labelSensitivityRangeMaxOWA.setText(QtGui.QApplication.translate("MCElite", "Max", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeMaxOWA)
        self.ui.labelSensitivityRangeStepOWA = QtGui.QLabel(self.ui.tabOWA)
        self.ui.labelSensitivityRangeStepOWA.setGeometry(QtCore.QRect(450, self.yBase+(4*self.yMod), 30, 22))
        self.ui.labelSensitivityRangeStepOWA.setMargin(1)
        self.ui.labelSensitivityRangeStepOWA.setIndent(0)
        self.ui.labelSensitivityRangeStepOWA.setObjectName("labelSensitivityRangeStepOWA")
        self.ui.labelSensitivityRangeStepOWA.setText(QtGui.QApplication.translate("MCElite", "Step", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeStepOWA)
        self.ui.labelSensitivityRangeThresholdOWA = QtGui.QLabel(self.ui.tabOWA)
        self.ui.labelSensitivityRangeThresholdOWA.setGeometry(QtCore.QRect(550, self.yBase+(4*self.yMod), 80, 22))
        self.ui.labelSensitivityRangeThresholdOWA.setMargin(1)
        self.ui.labelSensitivityRangeThresholdOWA.setIndent(0)
        self.ui.labelSensitivityRangeThresholdOWA.setObjectName("labelSensitivityRangeThresholdOWA")
        self.ui.labelSensitivityRangeThresholdOWA.setText(QtGui.QApplication.translate("MCElite", "Threshold", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelSensitivityRangeThresholdOWA)

        # Introductory text (Bool only)
        self.ui.introText = QtGui.QLabel(self.ui.tabBool)
        self.ui.introText.setGeometry(QtCore.QRect(260, self.yBase+(1.5*self.yMod), 300, 250))
        self.ui.introText.setMargin(1)
        self.ui.introText.setAlignment(QtCore.Qt.AlignTop)
        self.ui.introText.setObjectName('introText')
        self.ui.introText.setText(QtGui.QApplication.translate("MCElite", 
        '''<b>Multi-Criteria Evaluation</b> <p><b>Boolean</b>: Product of constraints & factors</p>
        <p><b>WLC</b>: Weighted Linear Combination</p><p><b>OWA</b>: Ordered Weighted Averaging</p>''', 
                                    None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.introText)

        # Buttons for loading configuration files
        self.ui.browseConfigBool = QtGui.QPushButton(self.ui.tabBool)
        self.ui.browseConfigBool.setGeometry(QtCore.QRect(320, self.tabH - (4 * self.yMod)-10, 200, 32))
        self.ui.browseConfigBool.setObjectName('browseConfigBool')
        self.ui.browseConfigBool.setText(QtGui.QApplication.translate("MCElite", "Load Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.browseConfigBool)
        self.ui.browseConfigWLC = QtGui.QPushButton(self.ui.tabWLC)
        self.ui.browseConfigWLC.setGeometry(QtCore.QRect(320, self.tabH - (4 * self.yMod)-10, 200, 32))
        self.ui.browseConfigWLC.setObjectName('browseConfigWLC')
        self.ui.browseConfigWLC.setText(QtGui.QApplication.translate("MCElite", "Load Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.browseConfigWLC)
        self.ui.browseConfigOWA = QtGui.QPushButton(self.ui.tabOWA)
        self.ui.browseConfigOWA.setGeometry(QtCore.QRect(320, self.tabH - (4 * self.yMod)-10, 200, 32))
        self.ui.browseConfigOWA.setObjectName('browseConfigOWA')
        self.ui.browseConfigOWA.setText(QtGui.QApplication.translate("MCElite", "Load Configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.browseConfigOWA)
        
        # OWA Order Weights
        self.ui.labelOrderWeights = QtGui.QLabel(self.ui.tabOWA)
        self.ui.labelOrderWeights.setGeometry(QtCore.QRect(10, self.tabH - (4 * self.yMod), 230, 22))
        self.ui.labelOrderWeights.setText(QtGui.QApplication.translate("MCElite", "<b>Order Weights</b> (ranked ascending):", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelOrderWeights)

        # Results file dialogs
        self.ui.results_file_Bool = QtGui.QLineEdit(self.ui.tabBool)
        self.ui.results_file_Bool.setGeometry(QtCore.QRect(10, self.tabH - (2 * self.yMod)+2, 180, 22))
        self.ui.results_file_Bool.setObjectName('results_file_Bool')
        self.ui.results_file_Bool.setText(QtGui.QApplication.translate("MCElite", "Results raster file", None, QtGui.QApplication.UnicodeUTF8))
        # Add results to tabD dictionary for easy access and to avoid cluttering uid dictionary
        self.tabD['Bool']['results'] = self.ui.results_file_Bool
        self.moveableWidgets.append(self.ui.results_file_Bool)
        self.ui.results_browsebutton_Bool = QtGui.QPushButton(self.ui.tabBool)
        self.ui.results_browsebutton_Bool.setGeometry(QtCore.QRect(200, self.tabH - (2 * self.yMod), 80, 32))
        self.ui.results_browsebutton_Bool.setObjectName('results_browsebutton_Bool')
        self.ui.results_browsebutton_Bool.setText(QtGui.QApplication.translate("MCElite", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.results_browsebutton_Bool)
        #
        self.ui.results_file_WLC = QtGui.QLineEdit(self.ui.tabWLC)
        self.ui.results_file_WLC.setGeometry(QtCore.QRect(10, self.tabH - (2 * self.yMod)+2, 180, 22))
        self.ui.results_file_WLC.setObjectName('results_file_WLC')
        self.ui.results_file_WLC.setText(QtGui.QApplication.translate("MCElite", "Results raster file", None, QtGui.QApplication.UnicodeUTF8))
        # Add results to tabD dictionary for easy access and to avoid cluttering uid dictionary
        self.tabD['WLC']['results'] = self.ui.results_file_WLC
        self.moveableWidgets.append(self.ui.results_file_WLC)
        self.ui.results_browsebutton_WLC = QtGui.QPushButton(self.ui.tabWLC)
        self.ui.results_browsebutton_WLC.setGeometry(QtCore.QRect(200, self.tabH - (2 * self.yMod), 80, 32))
        self.ui.results_browsebutton_WLC.setObjectName('results_browsebutton_WLC')
        self.ui.results_browsebutton_WLC.setText(QtGui.QApplication.translate("MCElite", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.results_browsebutton_WLC)
        # Results file field
        self.ui.results_file_OWA = QtGui.QLineEdit(self.ui.tabOWA)
        self.ui.results_file_OWA.setGeometry(QtCore.QRect(10, self.tabH - (2 * self.yMod)+2, 180, 22))
        self.ui.results_file_OWA.setObjectName('results_file_OWA')
        self.ui.results_file_OWA.setText(QtGui.QApplication.translate("MCElite", "Results raster file", None, QtGui.QApplication.UnicodeUTF8))
        # Add results to tabD dictionary for easy access and to avoid cluttering uid dictionary
        self.tabD['OWA']['results'] = self.ui.results_file_OWA
        self.moveableWidgets.append(self.ui.results_file_OWA)
        self.ui.results_browsebutton_OWA = QtGui.QPushButton(self.ui.tabOWA)
        self.ui.results_browsebutton_OWA.setGeometry(QtCore.QRect(200, self.tabH - (2 * self.yMod), 80, 32))
        self.ui.results_browsebutton_OWA.setObjectName('results_browsebutton_OWA')
        self.ui.results_browsebutton_OWA.setText(QtGui.QApplication.translate("MCElite", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.results_browsebutton_OWA)

        # Raster Format Combo Boxes and Labels
        # Labels
        # Bool
        self.ui.labelOutputRasterFormatsBool = QtGui.QLabel(self.ui.tabBool)
        self.ui.labelOutputRasterFormatsBool.setGeometry(QtCore.QRect(282, self.tabH-(2*self.yMod)+2, 100, 26))
        self.ui.labelOutputRasterFormatsBool.setMargin(1)
        self.ui.labelOutputRasterFormatsBool.setAlignment(QtCore.Qt.AlignTop)
        self.ui.labelOutputRasterFormatsBool.setObjectName('labelOutputRasterFormatsBool')
        self.ui.labelOutputRasterFormatsBool.setText(QtGui.QApplication.translate("MCElite", '<b>Output format:</b>', 
                                    None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelOutputRasterFormatsBool)
        # WLC
        self.ui.labelOutputRasterFormatsWLC = QtGui.QLabel(self.ui.tabWLC)
        self.ui.labelOutputRasterFormatsWLC.setGeometry(QtCore.QRect(282, self.tabH-(2*self.yMod)+2, 100, 26))
        self.ui.labelOutputRasterFormatsWLC.setMargin(1)
        self.ui.labelOutputRasterFormatsWLC.setAlignment(QtCore.Qt.AlignTop)
        self.ui.labelOutputRasterFormatsWLC.setObjectName('labelOutputRasterFormatsWLC')
        self.ui.labelOutputRasterFormatsWLC.setText(QtGui.QApplication.translate("MCElite", '<b>Output format:</b>', 
                                    None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelOutputRasterFormatsWLC)
        # OWA
        self.ui.labelOutputRasterFormatsOWA = QtGui.QLabel(self.ui.tabOWA)
        self.ui.labelOutputRasterFormatsOWA.setGeometry(QtCore.QRect(282, self.tabH-(2*self.yMod)+2, 100, 26))
        self.ui.labelOutputRasterFormatsOWA.setMargin(1)
        self.ui.labelOutputRasterFormatsOWA.setAlignment(QtCore.Qt.AlignTop)
        self.ui.labelOutputRasterFormatsOWA.setObjectName('labelOutputRasterFormatsOWA')
        self.ui.labelOutputRasterFormatsOWA.setText(QtGui.QApplication.translate("MCElite", '<b>Output format:</b>', 
                                    None, QtGui.QApplication.UnicodeUTF8))
        self.moveableWidgets.append(self.ui.labelOutputRasterFormatsOWA)

#        # Combo Boxes
#        # Bool
        self.ui.comboOutputRasterFormatsBool = QtGui.QComboBox(self.ui.tabBool)
        self.ui.comboOutputRasterFormatsBool.setGeometry(QtCore.QRect(380, self.tabH - (2 * self.yMod), 100, 26))
        self.ui.comboOutputRasterFormatsBool.setObjectName("comboOutputRasterFormatsBool")
        self.moveableWidgets.append(self.ui.comboOutputRasterFormatsBool)
#        # WLC
        self.ui.comboOutputRasterFormatsWLC = QtGui.QComboBox(self.ui.tabWLC)
        self.ui.comboOutputRasterFormatsWLC.setGeometry(QtCore.QRect(380, self.tabH - (2 * self.yMod), 100, 26))
        self.ui.comboOutputRasterFormatsWLC.setObjectName("comboOutputRasterFormatsWLC")
        self.moveableWidgets.append(self.ui.comboOutputRasterFormatsWLC)
#        # OWA
        self.ui.comboOutputRasterFormatsOWA = QtGui.QComboBox(self.ui.tabOWA)
        self.ui.comboOutputRasterFormatsOWA.setGeometry(QtCore.QRect(380, self.tabH - (2 * self.yMod), 100, 26))
        self.ui.comboOutputRasterFormatsOWA.setObjectName("comboOutputRasterFormatsOWA")
        self.moveableWidgets.append(self.ui.comboOutputRasterFormatsOWA)
        for ix, ixstr in enumerate(self.gdal_output_formats):
            self.ui.comboOutputRasterFormatsBool.addItem("")
            self.ui.comboOutputRasterFormatsWLC.addItem("")
            self.ui.comboOutputRasterFormatsOWA.addItem("")
            self.ui.comboOutputRasterFormatsBool.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))
            self.ui.comboOutputRasterFormatsWLC.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))
            self.ui.comboOutputRasterFormatsOWA.setItemText(ix, QtGui.QApplication.translate("MCElite", ixstr, None, QtGui.QApplication.UnicodeUTF8))

        # Set OK/Cancel button boxes on the three tabs
        # Boolean overlay
        self.ui.buttonBoxOkCancelBool = QtGui.QDialogButtonBox(self.ui.tabBool)
        self.ui.buttonBoxOkCancelBool.setGeometry(QtCore.QRect(self.tabW - self.okOffsetW, self.tabH - (2 * self.yMod), self.okW, self.okH))
        #self.ui.buttonBoxOkCancelBool.setGeometry(QtCore.QRect(460, 150, self.okW, self.okH))
        self.ui.buttonBoxOkCancelBool.setOrientation(QtCore.Qt.Horizontal)
        self.ui.buttonBoxOkCancelBool.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.ui.buttonBoxOkCancelBool.setObjectName("buttonbox_Bool")
        self.moveableWidgets.append(self.ui.buttonBoxOkCancelBool)
        # Weighted Linear Combination
        self.ui.buttonBoxOkCancelWLC = QtGui.QDialogButtonBox(self.ui.tabWLC)
        self.ui.buttonBoxOkCancelWLC.setGeometry(QtCore.QRect(self.tabW - self.okOffsetW, self.tabH - (2 * self.yMod), self.okW, self.okH))
        self.ui.buttonBoxOkCancelWLC.setOrientation(QtCore.Qt.Horizontal)
        self.ui.buttonBoxOkCancelWLC.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.ui.buttonBoxOkCancelWLC.setObjectName("buttonbox_WLC")
        self.moveableWidgets.append(self.ui.buttonBoxOkCancelWLC)
        # Ordered Weighted Averaging
        self.ui.buttonBoxOkCancelOWA = QtGui.QDialogButtonBox(self.ui.tabOWA)
        self.ui.buttonBoxOkCancelOWA.setGeometry(QtCore.QRect(self.tabW - self.okOffsetW, self.tabH - (2 * self.yMod), self.okW, self.okH))
        self.ui.buttonBoxOkCancelOWA.setOrientation(QtCore.Qt.Horizontal)
        self.ui.buttonBoxOkCancelOWA.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.ui.buttonBoxOkCancelOWA.setObjectName("buttonbox_OWA")
        self.moveableWidgets.append(self.ui.buttonBoxOkCancelOWA)

        # Miscellaneous goodies

        # Signals & Slots: Connect object signals to execution slots
        # Button Boxes
        QtCore.QObject.connect(self.ui.buttonBoxOkCancelBool, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.ui.buttonBoxOkCancelBool, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.ui.buttonBoxOkCancelWLC, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.ui.buttonBoxOkCancelWLC, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.ui.buttonBoxOkCancelOWA, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.ui.buttonBoxOkCancelOWA, QtCore.SIGNAL("rejected()"), self.reject)
        # Results file browsers
        QtCore.QObject.connect(self.ui.results_browsebutton_Bool, QtCore.SIGNAL("clicked()"), self.slotSaveRasterFile)
        QtCore.QObject.connect(self.ui.results_browsebutton_WLC, QtCore.SIGNAL("clicked()"), self.slotSaveRasterFile)
        QtCore.QObject.connect(self.ui.results_browsebutton_OWA, QtCore.SIGNAL("clicked()"), self.slotSaveRasterFile)
        QtCore.QObject.connect(self.ui.comboNumberConstraintsBool, QtCore.SIGNAL("activated(int)"), self.setNumberConstraints)
        QtCore.QObject.connect(self.ui.comboNumberFactorsBool, QtCore.SIGNAL("activated(int)"), self.setNumberFactors)
        QtCore.QObject.connect(self.ui.comboNumberConstraintsWLC, QtCore.SIGNAL("activated(int)"), self.setNumberConstraints)
        QtCore.QObject.connect(self.ui.comboNumberFactorsWLC, QtCore.SIGNAL("activated(int)"), self.setNumberFactors)
        QtCore.QObject.connect(self.ui.comboNumberConstraintsOWA, QtCore.SIGNAL("activated(int)"), self.setNumberConstraints)
        QtCore.QObject.connect(self.ui.comboNumberFactorsOWA, QtCore.SIGNAL("activated(int)"), self.setNumberFactors)
        # Configuration file browsers
        QtCore.QObject.connect(self.ui.browseConfigBool, QtCore.SIGNAL("clicked()"), self.slotOpenConfigFile)
        QtCore.QObject.connect(self.ui.browseConfigWLC, QtCore.SIGNAL("clicked()"), self.slotOpenConfigFile)
        QtCore.QObject.connect(self.ui.browseConfigOWA, QtCore.SIGNAL("clicked()"), self.slotOpenConfigFile)
        # Sensitivity
        QtCore.QObject.connect(self.ui.buttonSensitivityAllWLC, QtCore.SIGNAL("clicked()"), self.slotSelectAllSensCheckboxes)
        QtCore.QObject.connect(self.ui.buttonSensitivityClearWLC, QtCore.SIGNAL("clicked()"), self.slotClearAllSensCheckboxes)
        QtCore.QObject.connect(self.ui.buttonSensitivityAllOWA, QtCore.SIGNAL("clicked()"), self.slotSelectAllSensCheckboxes)
        QtCore.QObject.connect(self.ui.buttonSensitivityClearOWA, QtCore.SIGNAL("clicked()"), self.slotClearAllSensCheckboxes)
        # Gdal Output Formats
        QtCore.QObject.connect(self.ui.comboOutputRasterFormatsBool, QtCore.SIGNAL("activated(QString)"), self.slotSetGdalOutputFormat)
        # Finish
        QtCore.QMetaObject.connectSlotsByName(self)
        
        # Browse buttons, raster filenames and weights will be organized by number in a dictionary, 
        #     in order to copy the correct filenames to the right fields, and apply the correct weights
        # Create User Interface Dictionary
        self.createUID()
        self.setVisibility()
        self.resizeTabs()
        
    def createUID(self):
        fd = self.uid
        # local tab dictionary for each MCEType
        for tab, lTabD in self.tabD.items():
            fd.setdefault(tab, {})
            for row in self.rows:
                # Create empty row dictionary if it does not exist
                fd[tab].setdefault(row, {})
                # Loop through dictionary of Tab elements (for ltabD - specific to the Tab being created 
                for crit in lTabD['criteria']:
                    # Create empty criteria dictionary if it does not exist
                    fd[tab][row].setdefault(crit, {})
                    # Get name of widget to be created
                    for widget_name in lTabD['criteria'][crit]:
                        # local_widgetd = specific reference to sub-dict in widgetd with paramaters for this widget
                        local_widgetd = self.widgetd[widget_name]
                        # Call the widget_name, in the UID or create it out of the Tab dictionary
                        widget = fd[tab][row][crit].setdefault(widget_name, local_widgetd['gen'](lTabD['parent']))
                        try:
                            # Set widget geometry based on parameters references by local_widgetd OR 
                            widget.setGeometry(QtCore.QRect(local_widgetd['xdict'][crit], local_widgetd['yBase'] + (row * self.yMod), local_widgetd['width'], local_widgetd['height']))
                        except KeyError:
                            widget.setGeometry(QtCore.QRect(local_widgetd['xbase'] + (row * local_widgetd['xmod']), self.tabH - (3 * self.yMod), local_widgetd['width'], local_widgetd['height']))
                            self.moveableWidgets.append(widget)
                        # Set name of widget based on TAB + ROW + CRITERIA + WIDGET_NAME (type)
                        widget.setObjectName(string.join([tab, str(row), crit, widget_name], '_'))
                        if crit in ['constraints', 'factors']:
                            if widget_name == 'filepath':
                                widget.setText(QtGui.QApplication.translate('MCElite', '%s %s' % (crit.title(), row + 1), None, QtGui.QApplication.UnicodeUTF8))
                            elif widget_name == 'button':
                                widget.setText(QtGui.QApplication.translate('MCElite', 'Browse', None, QtGui.QApplication.UnicodeUTF8))
                            elif widget_name == 'weights':
                                widget.setText(QtGui.QApplication.translate('MCElite', 'Wt %s' % (row + 1), None, QtGui.QApplication.UnicodeUTF8))
                            elif widget_name == 'oweights':
                                widget.setText(QtGui.QApplication.translate('MCElite', '%s%s' % (row + 1, self.suffixD.get(row + 1, 'th')), None, QtGui.QApplication.UnicodeUTF8))
                            elif widget_name == 'checkbox':
                                widget.setText(QtGui.QApplication.translate('MCElite', 'Factor %s' % (row + 1), None, QtGui.QApplication.UnicodeUTF8))
#                                radioGroup = 'sensRadio'+tab
#                                getattr(self.ui, radioGroup).addButton(widget, row)
                        if local_widgetd['slot'] is not None:
                            QtCore.QObject.connect(widget, QtCore.SIGNAL(local_widgetd['signal']), local_widgetd['slot'])
             
        
    def setNumberConstraints(self, numconstraints):
        self.dmaxvisible['constraints'] = numconstraints
        # Visibility first! Qt won't leave a visible widget outside the parent window (which is a good thing).
        self.setVisibility()
        self.resizeTabs()
        self.reindexCombos()

    def setNumberFactors(self, numfactors):
        self.dmaxvisible['factors'] = numfactors
        # Visibility first! Qt won't leave a visible widget outside the parent window (which is a good thing).
        self.setVisibility()
        self.resizeTabs()
        self.reindexCombos()
        
    def resizeTabs(self):
        oldWinH = self.height()
        self.dmaxvisible['rows'] = max(self.dmaxvisible['constraints'], self.dmaxvisible['factors'])
        maxR = self.dmaxvisible['rows']
        newWinH = self.winH + (30 * (maxR))
        newTabH = self.tabH + (30 * (maxR)) 
        diffY = newWinH - oldWinH
        self.resize(self.winW, newWinH)
        self.ui.tabWidget.setGeometry(QtCore.QRect(10, 9, self.tabW, newTabH))
        # Adjust moveable widgets vertically
        for qObj in self.moveableWidgets:
            ogeo = qObj.geometry()
            ogeo.translate(0, diffY)
            qObj.setGeometry(ogeo)
        # Clear unseen fields if the UI is smaler (less constraints/factors)
        if diffY < 0:
            self.clearConfig(visible=False)

    def reindexCombos(self):
        self.ui.comboNumberConstraintsBool.setCurrentIndex(self.dmaxvisible['constraints'])
        self.ui.comboNumberFactorsBool.setCurrentIndex(self.dmaxvisible['factors'])
        self.ui.comboNumberConstraintsWLC.setCurrentIndex(self.dmaxvisible['constraints'])
        self.ui.comboNumberFactorsWLC.setCurrentIndex(self.dmaxvisible['factors'])
        self.ui.comboNumberConstraintsOWA.setCurrentIndex(self.dmaxvisible['constraints'])
        self.ui.comboNumberFactorsOWA.setCurrentIndex(self.dmaxvisible['factors'])

    def setVisibility(self):
            # Can we make this recursive without making a mess?
            td = self.uid
            for tab in td: # Bool, WLC, OWA
                for row in td[tab]: # index 0-9
                    for col in td[tab][row]: # factors, constraints 
                        for obj in td[tab][row][col].values(): # Button, etc.
                            if obj is None: continue
                            if col == 'factors':
                                if row <= self.dmaxvisible['factors']:
                                    obj.show()
                                else: 
                                    obj.hide()
                            elif col == 'constraints':
                                if row <= self.dmaxvisible['constraints']:
                                    obj.show()
                                else: 
                                    obj.hide()

    def slotSetGdalOutputFormat(self, gformat):
        if not gformat in self.gdal_output_formats:
            return
        self.output_format = str(gformat)

    def slotSelectAllSensCheckboxes(self):
        snd = self.sender()
        sndName = snd.objectName()
        mce = [str(x) for x in sndName.split('_')][0]
        # Clear all boxes in case there are non-visible boxes checked
        self.slotClearAllSensCheckboxes(mce)
        for ix in range(self.dmaxvisible['rows']+1):
            self.uid[mce][ix]['factors']['checkbox'].setChecked(True)        
    
    def slotClearAllSensCheckboxes(self, mce=None):
        snd = self.sender()
        sndName = snd.objectName()
        if not mce:
            mce = [str(x) for x in sndName.split('_')][0]
        for ix in range(self.maxRows):
            self.uid[mce][ix]['factors']['checkbox'].setChecked(False)

    def slotOpenRasterFile(self):
        snd = self.sender()
        sndName = snd.objectName()
        spl = [str(x) for x in sndName.split('_')]
        filename = QtGui.QFileDialog.getOpenFileName(self, self.tr("Raster"), self.lastdirused, "Raster (*.rst *.RST *.tif *tiff *.TIF *.TIFF)")
        self.lastdirused = os.path.split(str(filename))[0]
        #QtGui.QMessageBox.information(self, "OpenRaster", "Oinfo: %s" %(spl))
        self.uid[spl[0]][int(spl[1])][spl[2]]['filepath'].setText(filename)

    def slotSaveRasterFile(self):
        snd = self.sender()
        sndName = snd.objectName()
        spl = [str(x) for x in sndName.split('_')]
        filename = QtGui.QFileDialog.getSaveFileName(self, self.tr("Raster"), self.lastdirused, "Raster (*.rst *.RST *.tif *tiff *.TIF *.TIFF)")
        self.lastdirused = os.path.split(str(filename))[0]
        #QtGui.QMessageBox.information(self, "SaveRaster", "Oinfo: %s" %(spl))
        getattr(self.ui, 'results_file_'+spl[-1]).setText(filename)

    def slotOpenConfigFile(self):
#        snd = self.sender()
#        sndName = snd.objectName()
#        tab = str(sndName[-3:]).lower()
        filename = QtGui.QFileDialog.getOpenFileName(self, self.tr("Config"), self.lastdirused, "Text (*.txt *.TXT)")
        self.lastdirused = os.path.split(str(filename))[0]
        if filename:
            try:
                self.loadConfig(filename)
            except MCEliteError:
                errmsg = exc_info()[1]
                QtGui.QMessageBox.critical(self, self.tr("Error"), self.tr("%s" %(errmsg)))
                return
                        
    def clearConfig(self, visible=True):
        for MCEType in self.tabD:
            td = self.uid[MCEType]
            for row in range(self.maxRows):
                for crit, critd in td[row].items():
                    if not visible and row < self.dmaxvisible[crit]+1: continue
                    for widget_name, widget in critd.items():
                        if widget_name == 'button': continue
                        elif widget_name == 'filepath': 
                            widget.setText(QtGui.QApplication.translate('MCElite', '%s %s' % (crit.title(), row + 1), None, QtGui.QApplication.UnicodeUTF8))
                        elif widget_name == 'weights':
                            widget.setText(QtGui.QApplication.translate('MCElite', 'Wt %s' % (row + 1), None, QtGui.QApplication.UnicodeUTF8))
                        elif widget_name == 'oweights':
                            widget.setText(QtGui.QApplication.translate('MCElite', '%s%s' % (row + 1, self.suffixD.get(row + 1, 'th')), None, QtGui.QApplication.UnicodeUTF8))
                        elif widget_name == 'checkbox':
                            widget.setChecked(False)

            
    def loadConfig(self, filename=None):
        self.clearConfig()
        if filename:
            self.configurationFile = filename
        dread = {}
        csect = self.qm.config_sections
        dcsect = self.qm.dconfig_sections
        # conf is a list of lines now
        conf = open(self.configurationFile, 'rU').readlines()
#        conf = conf.split(nl)
        # Clean up lines in conf
        conf = [x.strip() for x in conf]
#        QtGui.QMessageBox.information(self, "Configuration", "%s" %(conf))
        for sect in csect:
            dread[sect] = {'index':None,
                             'val':[],
                             }
            # Find index value for start of each section in config file
            dread[sect]['index'] = conf.index(sect)
        for ix, sect in enumerate(csect):
            if sect == 'end':
                continue
            # Set start index for section to line after section name
            val_start = dread[sect]['index']+1
            # Set end of section to index of next section
            val_end = dread[csect[ix+1]]['index']
            # Grab lines in defined section
            dread[sect]['val'] = conf[val_start:val_end]
        mce = dread['mcetype']['val'][0]
        # Set output format to value from config file
        self.slotSetGdalOutputFormat(dread['output_format']['val'])
        self.ui.tabWidget.setCurrentIndex(self.tabD[mce]['tabid'])
        # Reset constraints drop-down menu and number of visible constraints rows
        self.setNumberConstraints(len(dread['constraints']['val'])-1)
        # Reset factors drop-down menu and number of visible factors rows
        self.setNumberFactors(len(dread['factors']['val'])-1)
        for ix, constraint in enumerate(dread['constraints']['val']):
            self.uid[mce][ix]['constraints']['filepath'].setText(constraint)
        for ix, factor in enumerate(dread['factors']['val']):
            try:
                # Set file path in textbox
                self.uid[mce][ix]['factors']['filepath'].setText(factor)
                # Set weight in text box (will be converted to numeric when read)
                self.uid[mce][ix]['factors']['weights'].setText(dread['weights']['val'][ix])
            except IndexError:
                raise MCEliteError("There must be one factor weight per factor. Please check configuration file.")
            except KeyError:
                pass
            try:
                self.uid[mce][ix]['factors']['oweights'].setText(dread['oweights']['val'][ix])
            except IndexError:
                raise MCEliteError("There must be one order weight per factor. Please check configuration file.")                
            except KeyError:
                pass
        resultsFilePath = dread['results']['val'][0]
        getattr(self.ui, 'results_file_'+mce).setText(resultsFilePath)
        # Sensitivity parameters - Boolean doesn't use them, so skip the rest
        if mce == 'Bool': return
        getattr(self.ui, 'sensMin'+mce).setText(dread['min']['val'][0])
        getattr(self.ui, 'sensMax'+mce).setText(dread['max']['val'][0])
        getattr(self.ui, 'sensStep'+mce).setText(dread['step']['val'][0])
        getattr(self.ui, 'sensThreshold'+mce).setText(dread['threshold']['val'][0])
        try:
            if dread['sensitivity']['val'][0] == '999':
                # Turn this range call into a list - for Python 3000
                dread['sensitivity']['val'] = list(range(len(dread['factors']['val'])))
        except IndexError:
            pass
        for ix in dread['sensitivity']['val']:
            self.uid[mce][int(ix)]['factors']['checkbox'].setChecked(True)
            
    def makeProgress(self):
        pMax = 4
        if self.qm.getSensitivity():
            self.qm.calSensitivityMods()
            wtCount = len(self.qm.getSensitivityMods())
            factorCount = len(self.qm.getSensitivityIndexes())
            pMax += (wtCount*factorCount)
#            QtGui.QMessageBox.information(self, self.tr("Progress"), self.tr("wtCount: %s\nfactorCount: %s\npMax: %s" 
#                                                                             %(wtCount, factorCount, pMax)))
        self.progress = QtGui.QProgressDialog("Please Wait", "Cancel", 0, pMax)
        self.progress.setValue(1)
#        QtGui.QMessageBox.information(self, self.tr("Progress"), self.tr("Progress: %s\nMin: %s\nMax: %s" %(self.progress.value(), self.progress.minimum(), self.progress.maximum())))
        
    def incrementProgress(self):
        newVal = self.progress.value() + 1
#        QtGui.QMessageBox.information(self, self.tr("Progress"), self.tr("Progress: %s\nSetting to %s." %(self.progress.value(), newVal)))
        self.progress.setValue(newVal)
            
    def accept(self):
        # Check weight sums for factors [WLC, OWA]
        # Check order weight sums for OWA 
        snd = self.sender()
        sndName = snd.objectName()
        spl = [str(x) for x in sndName.split('_')]
        self.MCEType = spl[-1]
        snd.setEnabled(False)
        # Check all constraint files to make sure that they exist
        for row in range(self.dmaxvisible['constraints']):
            tfpath = self.uid[self.MCEType][row]['constraints']['filepath'].text()
            if not os.path.exists(tfpath):
                QtGui.QMessageBox.warning(self, self.tr("Error"), self.tr("Constraint file %s (#%s) does not exist. Please check." 
                                                                          %(tfpath, row+1)))
                snd.setEnabled(True)
                return
        # Check all factor files to make sure that they exist
        for row in range(self.dmaxvisible['factors']):
            tfpath = self.uid[self.MCEType][row]['factors']['filepath'].text()
            if not os.path.exists(tfpath):
                QtGui.QMessageBox.warning(self, self.tr("Error"), self.tr("Factor file %s (#%s) does not exist. Please check." 
                                                                          %(tfpath, row+1)))
                snd.setEnabled(True)
                return            
        # Check to make sure that weights and order weights sum to one
        for wtype in self.tabD[self.MCEType]['sum']:
#            QtGui.QMessageBox.information(self, self.tr("Checking %s" %(self.MCEType)), self.tr("Running sumcheck on %s" %(wtype)))
            sumcheck = self.checkWeightSums(self.MCEType, wtype=wtype)
            if sumcheck != 'OK':
                QtGui.QMessageBox.warning(self, self.tr("Error"), self.tr(sumcheck))
                snd.setEnabled(True)
                return
        # Check to make sure a results file was selected
        resultsFilePath = str(self.tabD[self.MCEType]['results'].text())
        if not resultsFilePath or resultsFilePath == 'Results raster file':
            QtGui.QMessageBox.warning(self, self.tr("Error"), self.tr("Please specify output raster"))
            snd.setEnabled(True)
            return
        # Check to make sure that results directory exists
        elif not os.path.exists(os.path.dirname(resultsFilePath)):
            QtGui.QMessageBox.warning(self, self.tr("Error"), self.tr("Output directory does not exist.\nPlease check results file path."))
            snd.setEnabled(True)
            return            
        else:
            self.qm.setResultsFilePath(resultsFilePath)
        # Basic sanity checks passed - Export data to Query
        self.qm.exportDataToQueryObject(self)
        self.makeProgress()
        try:
            self.runAnalysis(snd)
        except MCEliteError:
            self.progress.cancel()
            errmsg = exc_info()[1]
            QtGui.QMessageBox.critical(self, self.tr("Error"), self.tr("%s" %(errmsg)))
            snd.setEnabled(True)
            return
        except:
            self.progress.cancel()
            snd.setEnabled(True)
            raise
        self.incrementProgress()
        if self.qm.getSensitivity():
            self.progress.cancel()
            QtGui.QMessageBox.information(self, self.tr("Completed"), 
                                          self.tr('Analysis Complete.\nSensitivity results in "%s"' 
                                                  %(self.qm.getSensitivityFileName())))
        else:
            self.progress.cancel()
            QtGui.QMessageBox.information(self, self.tr("Completed"), self.tr("Analysis Complete."))
        snd.setEnabled(True)
    
    def runAnalysis(self, snd):
        # Run the analysis
        try:
            self.qm.runQuery(self.progress)
        except ValueError, e:
            QtGui.QMessageBox.critical(self, self.tr("Error"), self.tr("%s" %(e)))
            snd.setEnabled(True)
            return
        self.incrementProgress()
        resultsLayer = QgsRasterLayer(self.qm.getResultsFilePath(), QtCore.QFileInfo(self.qm.getResultsFilePath()).baseName())
        # Set min/max automatically and stretch
        band = resultsLayer.bandNumber(resultsLayer.grayBandName()) #Should be 1
        # Stretches grayscale to minmax
        resultsLayer.setContrastEnhancementAlgorithm(QgsContrastEnhancement.StretchToMinimumMaximum)
        # End stretch
        QgsMapLayerRegistry.instance().addMapLayer(resultsLayer)
        resultsLayer.setCacheImage(None)
        resultsLayer.triggerRepaint()

    def returnWeightList(self, wname, attr=None, tabname=None, tdict=None):
        localist = list()
        # A typical call would be returnWeightList('weights', 'text', 'WLC')
#        QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("wname=%s\nattr=%s\ntabname=%s\ntdict=%s\nlocalist=%s" 
#                                                                            %(wname, attr, tabname, tdict, localist)))
        if tabname is not None:
            tdict = self.uid[tabname]
        for key, val in tdict.items():
#            QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("key=%s\nval=%s" %(key, val))) 
            if isinstance(val, dict):
#                QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("Going down one level")) 
                localist += self.returnWeightList(wname, attr, tdict=val)
#                QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("Returned with localist=%s" %(localist))) 
            elif key == wname:
                # This is a bit cryptic, but we are calling the "attr" method of "val" (using the "()")
                # if val == 'qobj' and attr == 'string', this is "qobj.string()"
#                QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("Adding %s to localist" %(getattr(val, attr)())))
                # Test to make sure value is a float
                try:
                    localist.append(float(getattr(val, attr)()))
                except ValueError:
                    pass 
#                QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("localist=%s" %(localist))) 
#        QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("returning localist=%s" %(localist))) 
        return localist
        
    def checkWeightSums(self, tabname, wtype='weights'):
        if wtype == 'weights': otype = 'Factor weights'
        else: otype = 'Order weights'
#        QtGui.QMessageBox.information(self, self.tr("Information"), self.tr("We are about to call a returnWeightList"))
        weightList = [x for x in self.returnWeightList(wname=wtype, attr='text', tabname=tabname)]
        if len(weightList) <= self.dmaxvisible['factors']:
            return "There must be a %s for each factor." %(otype)
        sumWeight = sum(weightList)
#        QtGui.QMessageBox.warning(self, self.tr("checkWeightSums"), self.tr("sumWeight for %s == %s" %(wtype, sumWeight)))
        if sumWeight == 0: return 'OK'
        elif sumWeight < 1.0: return '%s must sum to 1.0.\nCurrent sum is %s.\nPlease check.' % (otype, sumWeight)
        elif sumWeight > 1.0: return '%s must sum to 1.0.\nCurrent sum is %s.\nPlease check.' % (otype, sumWeight)
        elif sumWeight == 1.0: return 'OK'
        else: raise IOError
