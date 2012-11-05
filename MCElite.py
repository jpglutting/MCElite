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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
#from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from MCEliteDialog import MCEliteDialog

class MCElite: 

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

    def initGui(self):    
        # Create action that will start plugin configuration
        self.action = QAction(QIcon(":/plugins/mcelite/mcelite.png"), \
                "MCElite", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.slotRun) 
        self.helpaction = QAction(QIcon(":/mcehelp.png"), "Help", self.iface.mainWindow())
        self.helpaction.setWhatsThis("MCElite Help")
        self.action.setStatusTip("MCElite")
        QObject.connect(self.helpaction, SIGNAL("activated()"), self.helprun)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&MCElite", self.action)

        self.uiitems = {} 
        self.uiitems['mcetype'] = 'bool' #['bool', 'wcl', 'owa']
        self.uiitems['constraintcount'] = 1 # 1-10
        self.uiitems['factorcount'] = 1 # 1-10
        self.uiitems['constraints'] = {} 
        self.uiitems['constraintweights'] = {} 
        self.uiitems['factors'] = {} 
        self.uiitems['factorweights'] = {} 

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu("&MCElite",self.action)
        self.iface.removeToolBarIcon(self.action)

    def helprun(self):
        infoString = QString("MCElite - A Multi-Criteria Evaluaton Tool")
        infoString = infoString.append("Version 0.1.3")
        infoString = infoString.append("Coded by JP Glutting\njpglutting@gmail.com\n")
        infoString = infoString.append("Source: http://spatialserver.net/pyqgis_1.0/contributed/mcelite.zip")
        QMessageBox.information(self.iface.mainWindow(), "Raster File Info Plugin About",infoString)


    # run method that performs all the real work
    def slotRun(self): 
        # create and show the dialog 
        dlg = MCEliteDialog() 
        # show the dialog
        dlg.show()
        result = dlg.exec_() 
        # See if OK was pressed
        if result == 1: 
            # Establish an MCEvaluation item (class)
            # run evaluation
            # Return results
            pass 
