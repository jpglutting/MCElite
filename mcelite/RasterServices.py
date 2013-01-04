# -*- coding: utf-8 -*-

'''
Created on Aug 21, 2010

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
__author__ = '''JP Glutting'''
__credits__ = '''Copyright (c) JP Glutting'''

import os
import copy

from numpy import add, subtract, multiply, divide, issubdtype, ma
from MCErrorClasses import MCEliteError

# This potentially saves problems when GDAL is not installed
try:
    try:
        from osgeo import gdal 
    except ImportError:
        import gdal
except ImportError:
    print('''GDAL is unavailable. \nPlease install or configure GDAL.''')
    raise ImportError


# Causes GDAL to raise errors rather than print error info to sys.stdout
gdal.UseExceptions()
gdal.AllRegister()

class RasterObject(object):
    '''
    Provides a Python Object to hold information about a raster file:
    - Filename
    - Projection
    - Dimensions
    - Data
    '''

    def __init__(self, filepath=None, env='standalone', gdal_output_format=None, bands=None):
        '''
        Constructor to show what information a RasterObject instance will hold
        
        Arguments:
        
        filepath
            full path of the file source of the raster data
        env
            register the environment used, as a standalone library (default) or with QGIS/IDRISI/ArcGIS
        gdal_output_format
            optional type of format to output results
        bands
            optional number of bands in raster object
            
        Additional object properties:
         
         projection
             spatial projection [provided by GDAL]
        geotransform
            geotransform [provided by GDAL]
        origin
            origin [provided by GDAL]
        
        '''
        self.filepath = filepath
        self.path = None
        self.filename = None        
        self.env = env
        self.bands = bands
        self.projection = None
        self.geotransform = None
        self.origin = None
        self.pixelsize = None
        self.shape = None
        self.width = None
        self.height = None
        self.driver = None
        self.gdt = None
        self.gdtd = {} # GDAL data type
        self.npdt = {} # Numpy data type
        self.geotrans = None
        self.datad = {} # A dictionary that will hold raster information by band
                        #    as 2-dimensional numpy arrays
        self.nodatad = {}
        self.weight = 1.0 
                
    def __add__(self, other):
        # Matrix addition
        # rores = Raster Object Result
        rores = self.yieldCopy()
        rores.filepath = rores.filename = None
        rores.bands = len(rores.datad)
        #rores, other = self.adjustDataTypes(rores, other)
        #
        if isinstance(other, RasterObject):
            if self.width != other.width or self.height != other.height:
                raise ValueError('Rasters have incompatible dimensions')
            else:
                return self.add_ro_ro(rores, other)
        elif isinstance(other, bool):
            raise TypeError
        elif isinstance(other, (int, long, float)):
            return self.add_ro_num(rores, float(other))
        else:
            return NotImplemented

    __radd__ = __add__
            
    def add_ro_ro(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = add(rores.datad[i], other.datad[i])
        rores.bands = len(rores.datad)
        return rores
        
    def add_ro_num(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = add(rores.datad[i], other)
        rores.bands = len(rores.datad)
        return rores
        
    def __sub__(self, other):
        # Matrix subtraction
        rores = self.yieldCopy()
        rores.filepath = rores.filename = None
        rores.bands = len(rores.datad)
#        rores, other = self.adjustDataTypes(rores, other)
        if isinstance(other, RasterObject):
            if self.width != other.width or self.height != other.height:
                raise ValueError('Rasters have incompatible dimensions')
            else:
                return self.add_ro_ro(rores, other)
        elif isinstance(other, bool):
            raise TypeError
        elif isinstance(other, (int, long, float)):
            return self.add_ro_num(rores, float(other))
        else:
            return NotImplemented

    __rsub__ = __sub__
            
    def sub_ro_ro(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = subtract(rores.datad[i], other.datad[i])
        return rores
        
    def sub_ro_num(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = subtract(rores.datad[i], other)
        return rores        
        
    def __mul__(self, other):
        # Matrix multiplication
        rores = self.yieldCopy()
        rores.filepath = rores.filename = None
        rores.bands = len(rores.datad)
#        rores, other = self.adjustDataTypes(rores, other)
        if isinstance(other, RasterObject):
            if self.width != other.width or self.height != other.height:
                raise ValueError('Rasters have incompatible dimensions')
            else:
                return self.mul_ro_ro(rores, other)
        elif isinstance(other, bool):
            raise TypeError
        elif isinstance(other, (int, long, float)):
            return self.mul_ro_num(rores, float(other))
        else:
            return NotImplemented

    __rmul__ = __mul__

    def mul_ro_ro(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = multiply(rores.datad[i], other.datad[i])
        return rores

    def mul_ro_num(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = multiply(rores.datad[i], other)
        return rores

    def __div__(self, other):
        # Matrix division
        rores = self.yieldCopy()
        rores.filepath = rores.filename = None
        rores.bands = len(rores.datad)
#        rores, other = self.adjustDataTypes(rores, other)
        if isinstance(other, RasterObject):
            if self.width != other.width or self.height != other.height:
                raise ValueError('Rasters have incompatible dimensions')
            else:
                return self.div_ro_ro(rores, other)
        elif isinstance(other, bool):
            raise TypeError
        elif isinstance(other, (int, long, float)):
            return self.div_ro_num(rores, float(other))
        else:
            return NotImplemented

    __rdiv__ = __div__

    def div_ro_ro(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = divide(rores.datad[i], other.datad[i])
        return rores

    def div_ro_num(self, rores, other):
        for i in range(1, self.bands+1):
            rores.datad[i] = divide(rores.datad[i], other)
        return rores

    def adjustDataTypes(self, rores, other):
        if rores.gdt != other.gdt:
            print('{0} and {1} have different data types'.format(rores.filename, other.filename))
            return rores, other
        else:
            return rores, other
            
    def adjustWeight(self):
        for i in range(1, self.bands+1):
            # This will change the values of the datad array to float
            saveDtype = self.datad[i].dtype
            self.datad[i] = self.weight * self.datad[i]
            if issubdtype(saveDtype, int):
                self.datad[i] = self.datad[i].round()
        
    def setFilepath(self, filepath):    
        self.path, self.filename = os.path.split(filepath)
        
    def setData(self, indata, band=1):
        self.datad[band] = indata
    
    def setNoData(self, nodataval, band=1):
        self.nodatad[band] = nodataval
            
    def setDims(self):
        self.shape = self.datad[1].shape
        
    def setGDT(self, new_gdt):
        self.gdt = new_gdt
        
    def setMask(self, maskVal=None, band='All'):
        if band != 'All':
            self.unsetMask(band)
            self.setNoData(maskVal, band)
            if self.nodatad[band] is not None:
                self.datad[band] = ma.masked_equal(self.datad[band], self.nodatad[band])
        else:
            self.unsetMask()
            for band in range(1, self.bands+1):
                self.setMask(maskVal, band)
        
    def unsetMask(self, band='All'):
        # Remove any existing mask
        if band != 'All':
            if hasattr(self.datad[band], 'mask'):
                self.datad[band].mask = ma.nomask
        else:
            for band in range(1, self.bands+1):
                self.unsetMask(band)
        
    def getData(self):
        return self.datad[1]
    
    def getDataType(self):
        return self.npdt[1] # Return numpy data type
    
    def yieldCopy(self):
        cp = copy.deepcopy(self)
        cp.filename = cp.filepath = cp.path = None
        cp.weight = 1.0
        return cp
    
    def yieldZRaster(self):
        from scipy import stats   
        zraster = self.yieldCopy()
        zraster.setGDT('Float32')
        zraster.datad[1] = stats.zscore(self.getData())
        return zraster
            
    def adjustDataFormat(self):
        # This is not needed yet, as gdal handles rounding and data conversion of byte data
        # However, it might be needed later for other functions, such as comparing raster layers
        if self.gdt in ['Byte', 'UInt16', 'Int16', 'UInt32', 'Int32']:
            for i in range(1, self.bands+1):
                self.datad[i] = self.datad[i].round()
                self.datad[i].astype(self.gdt.lower())
        elif self.gdt in [ 'Float32', 'Float64']:
            for i in range(1, self.bands+1):
                self.datad[i].astype(self.gdt.lower())
        else:
            return NotImplementedError

    def rescaleData(self, inmin=None, inmax=None):
        '''Rescale the resulting floating point data to the appropriate scale\n
            Byte (8bit) integers assumed in test case
            UNUSED: This seems to be implemented properly, but does not produce the same
                scaling as the IDRISI OWA function, so there is something missing. Revisit with fuzzy logic.
            '''
        dScale = {'Byte':{'min':0.0, 'max':255.0},
                  'Int16':{'min':-32768.0, 'max':32767.0},
                  'UInt16':{'min':0.0, 'max':65535.0},
                  'Int32':{'min':-2147483648.0, 'max':2147483647.0},
                  'UInt32':{'min':0.0, 'max':4294967295.0},
                  }
        target0 = dScale[self.gdt]['min']
        targetN = dScale[self.gdt]['max']
        for adata in self.datad.values():
            source0 = adata.min()
            sourceN = adata.max()
            scale = (sourceN-source0)/(targetN-target0)
            lenX, lenY = adata.shape
            for ix in range(lenX):
                for iy in range(lenY):
                    adata[ix,iy] = target0+(adata[ix,iy]-source0)/scale
#                    ESRI formula
#                    adata[ix,iy] = (adata[ix,iy]-source0) * targetN / (sourceN - source0) + target0


class RasterProvider(object):
    '''
    The purpose of this class is to manage raster input and conversion to NumPy arrays. Only GDAL is implemented.
    '''

    def __init__(self, env="standalone"):
        '''
        Constructor
        Code here to determine the GIS environment, if possible
        '''
        self.env = env
        self.dmap_data_formats = {'Byte':['Byte','UInt16','Int16','UInt32','Int32'],
                            'UInt16':['UInt16','UInt32','Int32'],
                            'Int16':['Int16','Int32'],
                            'UInt32':['UInt32','Int32'],
                            'Int32':['Int32'],
                            'Float32':['Float32','Float64'],
                            'Float64':['Float64'],
                            }
            
    def readFromFile(self, filepath, gdal_output_format=None, bands=None, maskVal=None):
        if not filepath:
            raise IOError('Could not open raster %s' %(filepath))
        filepath = os.path.abspath(str(filepath))
        rasterOb = RasterObject() # Create new empty RasterObject from class
        # This function won't take a Unicode string, it needs to be converted.
        rasterOb.setFilepath(filepath)
        ds = gdal.Open(filepath)
        if ds is None:
            print("File could not be opened.")
            raise MCEliteError('Raster file %s could not be opened' %(filepath))
        # Temp RasterObject
        rasterOb.env = self.env
        rasterOb.projection = ds.GetProjection()
        rasterOb.geotransform = ds.GetGeoTransform()
        if not rasterOb.geotransform is None:
            rasterOb.origin = (rasterOb.geotransform[0],rasterOb.geotransform[3])
            rasterOb.pixelSize = (rasterOb.geotransform[1],rasterOb.geotransform[5])
        # ===
        rasterOb.driver = repr(ds.GetDriver())
        # ===
        rasterOb.width = ds.RasterXSize
        rasterOb.height = ds.RasterYSize
        # Use only band 1 for MCE - the rest can wait
        # bands can be passed as "all" or integer
        if bands == 'All':
            rasterOb.bands = ds.RasterCount
        elif not bands:
            rasterOb.bands = 1
        # If there are multiple bands, we are only going to use band 1, but this is unexpected and will use more memory
        # Bands > 1 disabled
        # For now, we will only use one band
        if rasterOb.bands > 1: 
            print('Multiple Bands [{0}] in raster {1} in directory {2}'.format(rasterOb.bands, rasterOb.filename, rasterOb.path))
        # Reads all bands - this should not be needed, but the RasterObject could have other uses for this later. 
        for iband in range(1, rasterOb.bands+1):
            band_data = ds.GetRasterBand(iband)
            rasterOb.gdtd[iband] = gdal.GetDataTypeName(band_data.DataType)
            rasterOb.datad[iband] = band_data.ReadAsArray()
            rasterOb.npdt[iband] = rasterOb.datad[iband].dtype
        rasterOb.setMask(maskVal)
        rasterOb.gdt = copy.copy(rasterOb.gdtd[1])
        # Make masked array to exclude NoDataValue from calculations
        # Clean up ds to recover memory
        ds = None
        rasterOb.setDims()
        return rasterOb
        
    def writeToFile(self, rasterOb, filepath, gdal_output_format='GTiff'):
        ro = rasterOb
        filepath = os.path.splitext(filepath)[0]
        # Need to create a RasterBAnd object and write to that
        driver = gdal.GetDriverByName(gdal_output_format)
        metadata = driver.GetMetadata()
        suffix = metadata.get(gdal.DMD_EXTENSION, '')
        create_data_types = metadata[gdal.DMD_CREATIONDATATYPES].split()
        if suffix:
            outfilepath = filepath + '.' + suffix
        else:
            outfilepath = filepath
        # Create(<filename>, <xsize>, <ysize>, [<bands>], [<GDALDataType>])
        output_gdt = None
        if ro.gdt in create_data_types:
            output_gdt = ro.gdt
        else:
            for dfmt in self.dmap_data_formats[ro.gdt]:
                if dfmt in create_data_types:
                    output_gdt = dfmt
                    break
        try:
            ds_out = driver.Create(outfilepath, ro.width, ro.height, 1, gdal.GetDataTypeByName(output_gdt))
        except RuntimeError:
#            print('\tOUTPUT DATA_FORMAT:', output_gdt)
#            print('\tro.width:', ro.width)
#            print('\tro.height:', ro.height)
#            print('\toutfilepath:', outfilepath)
            raise MCEliteError("Results file %s cannot be written. \
            \nMake sure that it is not opened or write-protected, and that the format is supported." %(outfilepath))
        ds_out.SetGeoTransform(ro.geotransform)
        ds_out.SetProjection(ro.projection)
        # Writes as many bands as we have
        for band_id in ro.datad:
            ds_out.GetRasterBand(band_id).WriteArray(rasterOb.datad[band_id])
            ds_out.GetRasterBand(band_id).SetNoDataValue(0.0)
        return outfilepath
            
    def importFromArc(self):
        ''' This can be implemented for ArcGIS 10, using gp.RasterToNumPyArray (recover results with NumPyArrayToRaster)
        '''
        pass
    
    def exportToArc(self):
        ''' This can be implemented for ArcGIS 10, using gp.NumPyArrayToRaster
        '''
        pass
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()
