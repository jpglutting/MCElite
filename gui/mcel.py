#!/usr/bin/env python
'''
Created on Sep 23, 2010

@author: jpg

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/

Command line program for using MCElite library.

'''
import os
import sys
import optparse

import QueryManager

denv = {'standalone':QueryManager.BaseQueryManager,
        'ESRI':QueryManager.ArcQueryManager,
        'IDRISI':QueryManager.IdrisiQueryManager,
        'QGIS':QueryManager.QgisQueryManager
        }

def main():
    
    p = optparse.OptionParser()

    # Add options and arguments:
    p.add_option('-c', action="store", dest="config")
    p.add_option('--config', action="store", dest='config')

    p.add_option('-f', action='store', dest='format')
    p.add_option('--format', action='store', dest='format')

    p.add_option('-e', action='store', dest='env')
    p.add_option('--environment', action='store', dest='env')

    p.set_defaults(env='standalone')
    p.set_defaults(format='GTiff')

    opts, args = p.parse_args()
    
    env = opts.env
    format = opts.format
    config_file = os.path.abspath(opts.config)

    # Call constructor out of dictionary
    qm = denv[env]()
    qm.setConfigurationFile(config_file)
    qm.readMCEConfig(config_file)
    qm.runQuery()
    print 'Results written to', qm.getResultsFilePath()

if __name__ == "__main__":
    main()
