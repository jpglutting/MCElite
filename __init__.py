"""
/***************************************************************************
MCELite
A QGIS plugin
Multiple Criteria Analysis tool
                             -------------------
begin                : 2010-08-27 
copyright            : (C) 2010 by JP Glutting
email                : jpglutting@gmail.com 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
def name(): 
    return "MCE Lite" 
def description():
    return "Multiple Criteria Analysis tool"
def version(): 
    return "Version 0.1.2" 
def qgisMinimumVersion():
    return "1.0"
def classFactory(iface): 
    # load MCELite class from file MCELite
    from MCELite import MCELite 
    return MCELite(iface)


