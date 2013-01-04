"""
***************************************************************************
MCELite
A QGIS plugin
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

 This script initializes the plugin, making it known to QGIS.

"""
def name(): 
    return "MCElite" 

def author():
    return "JP Glutting"

def description():
    return "Multiple Criteria Analysis tool"

def homepage():
    return "www.jpglutting.com"

def respository():
    return "https://github.com/jpglutting/MCElite"

def version(): 
    return "Version 0.1.4" 

def qgisMinimumVersion():
    return "1.8"

def classFactory(iface): 
    # load MCElite class from file MCElite
    from MCElite import MCElite 
    return MCElite(iface)


