'''
Created on Oct 11, 2010

@author: jpg

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''

import unittest
import os

from osgeo import gdal
import RasterServices

class CheckRasterServices(unittest.TestCase):
    
    def test(self):
        unittest.main(__name__)
    
    def setUp(self):
        self.test_raster_file = os.path.abspath('../examples/data/developfuzz.rst')
    
    def tearDown(self):
        pass
    
    def testrastercreation(self):
        rp = RasterServices.RasterProvider()
        r1 = rp.readFromFile(self.test_raster_file)
        pass