# -*- coding: utf-8 -*-

'''
Created on Aug 23, 2010

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
import operator
import os
import copy

from numpy import arange, array
from RasterServices import RasterProvider
from MCErrorClasses import MCEliteError

class QueryObject(object):
    '''
    This class holds the data extracted from the UI and passes it to 
    the analytical functions (QueryObjects). 
    '''
    def __init__(self):
        self.mceType = None
        self.rp = RasterProvider()
        self.resultsRaster = None
        self.sensitivityThreshold = None
        self.mceData = {'constraints': [],
                              'factors':[],
                              'factornames':[],
                              'weights':[],
                              'oweights':[],
                              }
        self.analyzeMCE = {'Bool':self.analyzeBool,
                          'WLC':self.analyzeWLC,
                          'OWA':self.analyzeOWA,
                          }
        
    def setMCEType(self, mtype):
        self.mceType = mtype

    def setConstraints(self, constraints):
        self.mceData['constraints'] = constraints

    def setFactors(self, factors):
        self.mceData['factors'] = factors

    def setFactorWeights(self, weights):
        self.mceData['weights'] = weights

    def setOrderWeights(self, oweights):
        self.mceData['oweights'] = oweights

    def setSensitivityThreshold(self, threshold):
        self.sensitivityThreshold = threshold 

    def appendToMCEData(self, intype, invalue):
        self.mceData[intype].append(invalue)
    
    def getMCEType(self):
        return self.mceType

    def getConstraints(self):
        return self.mceData['constraints']

    def getFactors(self):
        return self.mceData['factors']

    def getFactorByIndex(self, ix):
        return self.mceData['factors'][ix]

    def getFactorNames(self):
        return self.mceData['factornames']

    def getFactorNameByIndex(self, ix):
        return self.mceData['factornames'][ix]

    def getFactorWeights(self):
        return self.mceData['weights']

    def getFactorWeightByIndex(self, ix):
        return self.mceData['weights'][ix]

    def getOrderWeights(self):
        return self.mceData['oweights']

    def getResults(self):
        return self.resultsRaster
    
    def runQuery(self):
        if self.mceType == None:
            raise MCEliteError('No analysis type declared.')
        elif not (self.mceData['constraints'] or self.mceData['factors']):
            raise MCEliteError('No raster files to analyze.')
        self.analyzeMCE[self.mceType]()

    def analyzeBool(self):
        if not self.mceData['factors']:
            raise MCEliteError('At least one factor file needed.')
        elif not self.mceData['constraints']:
            self.resultsRaster = self.calReduceRasters('factors')
        else:
            self.resultsRaster = self.calReduceRasters('constraints') * self.calReduceRasters('factors')
    
    def analyzeWLC(self):
        if not self.mceData['factors']:
            raise MCEliteError('At least one factor file needed.')
        elif not self.mceData['constraints']:
            self.resultsRaster = sum(self.calFactorWeights())
        else:
            constraint_results = self.calReduceRasters('constraints')
            factor_results = sum(self.calFactorWeights())
            self.resultsRaster = constraint_results * factor_results
    
    def analyzeOWA(self):
        if not self.mceData['factors']:
            raise MCEliteError('At least one factor file needed.')
        oweights = array(self.mceData['oweights'])
        factor_rasters = self.calFactorWeights()
        self.resultsRaster = factor_rasters[0].yieldCopy()
        aList = [x.datad[1] for x in factor_rasters]
        factor_rasters = None
        aShapes = [x.shape for x in aList]
        refShape = aShapes[0]
        w,l = refShape
        if len(oweights) != len(aList):
            raise IndexError('There must be exactly one order weight per layer.')
        if [x for x in aShapes if x != refShape]:
            raise IndexError('Not all layers have the same dimensions.')
        a3D = array(aList)
        aList = None
        # Extract columns for each (x,y) coordinate point in raster, as a list
        cols = [a3D[:,x,y] for x in range(w) for y in range(l)]
        # Sort columns (smallest to largest)
        [x.sort() for x in cols]
        # Apply oder weights to all columns, and then sum, 
        # leaving a single value per coordinate point
        # Converted to an array and reshaped to the dimensions of the original raster
        newArray = array([sum(x*oweights) for x in cols]).reshape(refShape)
        # Store results raster data in the results raster data dictionary
        self.resultsRaster.datad[1] = newArray
        constraint_results = self.calReduceRasters('constraints')
        if self.mceData['constraints']:
            self.resultsRaster *= constraint_results
#        self.resultsRaster.rescaleData()

    def calReduceRasters(self, dataID):
        # This potentially uses a lot of memory - a loop that cleared references for garbage collection might be better
        # Also, blocking, GDAL's virtual raster format (vrt) and RasterLite (raster in SQLite databases)
        # could all potentially be useful for very large rasters.
        rasternames = self.mceData[dataID]
        rasters = [self.rp.readFromFile(fpath) for fpath in rasternames]
        return reduce(operator.mul, rasters)
    
    def calFactorWeights(self):
        factor_files = self.mceData['factors']
        factor_weights = self.mceData['weights']
        factor_rasters = [self.rp.readFromFile(fpath) for fpath in factor_files]
        for ix, fr in enumerate(factor_rasters):
            fr.weight = factor_weights[ix]
            fr.adjustWeight()
        return factor_rasters    
    
    def yieldCopy(self):
        """
        Create newQueryObject by doing a deepcopy of the 'self' QueryObject
        Copy the data to a new queryObject if this fails.
        """
        try:
            nQO = copy.deepcopy(self)
            nQO.resultsRaster = None
            nQO.resultsPath = None
            nQO.resultsFileRoot = None
            nQO.resultsFilePath = None
        # Sometimes deepcopy fails to copy this object with a TypeError
        except TypeError:
            nQO = QueryObject()
            nQO.setMCEType(self.getMCEType())
            nQO.mceData = copy.deepcopy(self.mceData)
        return nQO

    def countSensitivityThresholdValues(self, threshold=None):
        if not threshold:
            if not self.sensitivityThreshold: 
                raise MCEliteError('No threshold value declared.')
            threshold = self.sensitivityThreshold
        return (self.resultsRaster.datad[1] >= threshold).sum()

    def retypeMCEData(self):
        for dtype in ['weights', 'oweights']:
            self.mceData[dtype] = [float(x) for x in self.mceData[dtype]]
        for dtype in ['constraints', 'factors']:
            self.mceData[dtype] = [str(x) for x in self.mceData[dtype]]

    def extractFactorNames(self):
        return [os.path.splitext(os.path.split(factor)[1])[0] for factor in self.mceData['factors']]        


class BaseQueryManager(object):
    '''
    Base class for managing QueryObjects (which execute queries).\n
    Contains format data, configuration file parser, results file generator
    and read and write functions for variables. 
    Code for sensitivity analysis resides here. The BaseQueryManager makes copies of itself
    with modified parameters to test the sensitivity of results to changes.  
    '''
    
    def __init__(self):
        try:
            from osgeo import gdal
        except ImportError:
            print('GDAL is not available.')
            raise ImportError 
        # Causes GDAL to raise errors rather than print error info to sys.stdout
        gdal.UseExceptions()
        # ------------------
        self.env = 'standalone'
        self.baseQuery = QueryObject()
        self.rp = RasterProvider()
        self.mceType = None
        self.gdal_output_format = None
        self.resultsFilePath = None
        self.resultsPath = None
        self.resultsFileRoot = None
        self.sensitivity = False
        self.sensitivityIndexes = []
        self.sensitivityThreshold = None
        self.sensitivityMin = None
        self.sensitivityMax = None
        self.sensitivityStep = None
        self.sensitivityWeights = []
        self.sensitivityMods = []
        self.sensitivityResults = {}
        self.sensitivityFileName = None
        self.sensitivityFilePath = None
        self.configurationFile = None
        self.config_sections = ['mcetype', 'output_format', 'results',
                    'constraints', 'factors', 'weights','oweights',
                    'sensitivity','min','max','step','threshold',
                    'end']
        self.dconfig_sections = {
                    'mcetype':{'type':str, 'source':self.getMCEType,
                                'target':self.setMCEType,},
                    'output_format':{'type':str, 'source':self.getGdalFormat,
                                'target':self.setGdalFormat,},
                     'results':{'type':str, 'source':self.getResultsFilePath, 
                                 'target':self.setResultsFilePath,},
                     'constraints':{'type':str, 'source':self.baseQuery.getConstraints,
                                    'target':self.baseQuery.setConstraints,},
                     'factors':{'type':str, 'source':self.baseQuery.getFactors,
                                'target':self.baseQuery.setFactors,},
                     'weights':{'type':float, 'source':self.baseQuery.getFactorWeights,
                                'target':self.baseQuery.setFactorWeights,},
                     'oweights':{'type':float, 'source':self.baseQuery.getOrderWeights,
                                 'target':self.baseQuery.setOrderWeights,},
                     'sensitivity':{'type':int, 'source':self.getSensitivityIndexes,
                                         'target':self.setSensitivityIndex,},
                     'min':{'type':float, 'source':self.getSensitivityMin,
                            'target':self.setSensitivityMin,},
                     'max':{'type':float, 'source':self.getSensitivityMax,
                            'target':self.setSensitivityMax,},
                     'step':{'type':float, 'source':self.getSensitivityStep,
                             'target':self.setSensitivityStep,},
                     'threshold':{'type':float, 'source':self.getSensitivityThreshold,
                                  'target':self.setSensitivityThreshold},
                    # This entry prevents a KeyError when writing the configuration file
                     'end':{'type':str, 'source':str,
                                  'target':str,},
                     }
        self.dEnv = {'standalone':'GTiff',
                     'ESRI':'GTiff',
                     'IDRISI':'RST',
                     'QGIS':'GTiff'
                     }
        self.gdal_output_formats = ['GTiff', 'ENVI', 'EHdr', 'RST']
        self.setEnv()
        
    def undo_list(self, inx):
        if isinstance(inx, list):
            if len(inx) == 0:
                return None
            else:
                return inx[0]
        else:
            return inx
    
    def setConfigurationFile(self, filepath):
        if not os.path.isfile(filepath):
            print("File not available")
            raise IOError
        self.configurationFile = filepath
        
    def setGdalFormat(self, fmt=None):
        fmt = self.undo_list(fmt)
        if fmt:
            self.gdal_output_format = fmt
        else:
            self.gdal_output_format = self.dEnv[self.env]
        
    def setEnv(self, inEnv=None):
        inEnv = self.undo_list(inEnv)
        if inEnv:
            self.env = inEnv
        else:
            self.env = 'standalone'
        self.setGdalFormat()
       
    def setMCEType(self, mtype):
        mtype = self.undo_list(mtype)
        self.mceType = mtype
        self.baseQuery.setMCEType(mtype)

    def setResultsFilePath(self, filepath):
        if isinstance(filepath, list):
            filepath = filepath[0]
        path, filename = os.path.split(filepath)
        fileroot = os.path.splitext(filename)[0]
        self.resultsPath = path
        self.resultsFilePath = filepath
        self.resultsFileRoot = fileroot
        self.resultsFileName = filename
        
    def setSensitivity(self, sensitivity):
        sensitivity = self.undo_list(sensitivity)
        self.sensitivity = sensitivity
        
    def setSensitivityIndex(self, sindexes):
        self.sensitivityIndexes = sindexes
        
    def appendSensitivityIndex(self, sindex):
        self.sensitivityIndexes.append(sindex)

    def clearSensitivityIndex(self):
        self.sensitivityIndexes = []
        
    def setSensitivityMin(self, min):
        min = self.undo_list(min)
        self.sensitivityMin = min
        
    def setSensitivityMax(self, max):
        max = self.undo_list(max)
        self.sensitivityMax = max
        
    def setSensitivityStep(self, step):
        step = self.undo_list(step)
        self.sensitivityStep = step
        
    def setSensitivityThreshold(self, threshold):
        threshold = self.undo_list(threshold)
        self.sensitivityThreshold = threshold 
        
    def getMCEType(self):
        return self.mceType
        
    def getGdalFormat(self):
        return self.gdal_output_format
        
    def getResultsFilePath(self):
        return self.resultsFilePath

    def getResultsPath(self):
        return self.resultsPath

    def getResultsFileName(self):
        return self.resultsFileName

    def getResultsFileRoot(self):
        return self.resultsFileRoot
        
    def getSensitivity(self):
        return self.sensitivity

    def getSensitivityIndexes(self):
        return self.sensitivityIndexes
    
    def getSensitivityMods(self):
        return self.sensitivityMods
    
    def getSensitivityMin(self):
        return self.sensitivityMin
    
    def getSensitivityMax(self):
        return self.sensitivityMax
        
    def getSensitivityStep(self):
        return self.sensitivityStep
        
    def getSensitivityThreshold(self):
        return self.sensitivityThreshold
        
    def getSensitivityFileName(self):
        return self.sensitivityFileName
    
    def calSensitivityMods(self):
        start = self.sensitivityMin
        stop = self.sensitivityMax + 0.00001
        step = self.sensitivityStep
        self.sensitivityMods = arange(start, stop, step)
        
    def runSensitivityAnalysis(self):
        if self.sensitivity is not True or self.mceType == 'Bool': 
            return
        # Calculate value modifications (weights) to be applied to test factors.
        self.calSensitivityMods()
        refIndex = self.sensitivityIndexes
        refWeights = array(self.baseQuery.getFactorWeights())
        lenNewWts = len(refWeights)-1
        self.baseQuery.setSensitivityThreshold(self.sensitivityThreshold)
        self.sensitivityResults['base'] = self.baseQuery.countSensitivityThresholdValues()
        sensQuery = self.baseQuery.yieldCopy()
        factor_names = self.baseQuery.extractFactorNames()
        # Loop through indexes / names of factors to be tested
        for ix, resName in enumerate(factor_names):
            if (refIndex.count(999) + refIndex.count(ix)) == 0:
                continue
            resDict = self.sensitivityResults.setdefault(resName, {})
            # Loop through weights that will be applied to selected factors
            for wtVar in self.sensitivityMods:
                # Adjust selected factor by percentage modification
                wtAdjust = refWeights[ix] * wtVar
                # Create list of length lenNewWts-1 (for factors, minus the one being tested)
                # with the amount the selected weight is adjusted divided among the 
                # remaining factors, with the sign reversed
                newWts = lenNewWts * [-wtAdjust/lenNewWts]
                newWts.insert(ix, wtAdjust)
                newWts = array(newWts)
                # Make newWts equal to the adjusted values of original weights (refWeights)
                newWts += refWeights
                resID = '%s_%spct' %(resName, int(round(wtVar*100, 0)))
                # Reuse the same object, just set new weights and recalculate
                # Hopefully this will prevent the creation of a memory-eating monster
                sensQuery.setFactorWeights(newWts)
                sensQuery.runQuery()
                sensQuery.setSensitivityThreshold(self.sensitivityThreshold)
                # Extract the count of cells above sensitivity threshold
                # and move on to next modification
                resDict[wtVar] = sensQuery.countSensitivityThresholdValues()
                # This increments the index.value() of the QProgressDialog
                if hasattr(self, 'pd'): 
                    self.incrementPD()
                    self.pd.setVisible(True)
        self.writeSensitivityResults()
    
    def writeSensitivityResults(self):
        refFileRoot = self.getResultsFileRoot()
        refFileName = self.getResultsFilePath()
        refFilePath = self.getResultsPath()
        refRes = self.sensitivityResults
        step = self.sensitivityStep
        self.sensitivityFileName = '%s_sensitivity_results.html' %(refFileRoot)
        self.sensitivityFilePath = os.path.join(refFilePath, self.sensitivityFileName)
        ltabint = []
        ltable1 = []
        ltable2 = []
        lhead1 = ['<tr style="background: darkgray;"><th>% Var</th>']
        lhead2 = ['<tr style="background: darkgray;"><th>% Var</th>']
        wtkeys = list(self.sensitivityMods)
        wtkeys.reverse()
        refkeys = refRes.keys()
        refkeys.sort()
        [lhead1.append('<td>%s</td>'%(x.title())) for x in refkeys if x != 'base']
        [lhead2.append('<td>%s</td>'%(x.title())) for x in refkeys if x != 'base']
        lhead1.append('</tr>')
        lhead2.append('</tr>')
        for ix, wkey in enumerate(wtkeys):
            ltabint.append([])
            ltable1.append([])
            ltabint[ix] = [refRes[x][wkey] for x in refkeys if x != 'base']
            ltable1[ix] = [0.0 for x in ltabint[ix]]
            ltable2 = copy.deepcopy(ltable1)
        tlen = len(ltabint)-1
        # Step through the results table
        for y, row in enumerate(ltabint):
            refwt = int(round(wtkeys[y]*100))
            for x, cell in enumerate(row):
                # Don't try to compare to previous results if we are at the first(bottom) row
                if y == tlen:
                    diff = 0.0
                    format = ''
                else:
                    # Value from "previous" iteration (y+1)
                    baseline = ltabint[y+1][x]
                    try:
                        diff = (cell - baseline)/float(baseline)
                    except ZeroDivisionError:
                        diff = 1.0
                    if abs(diff) > (3*step):
                        format = ' style="color: crimson;"'
                    elif abs(diff) > (2*step):
                        format = ' style="color: darkorange;"'
                    elif abs(diff) > step:
                        format = ' style="color: royalblue;"'
                    else:
                        format = ''
                ltable1[y][x] = '<td%s>%s</td>' %(format, cell)
                ltable2[y][x] = '<td%s>%s%%</td>' %(format, round(diff*100, 2))
            ltable1[y].insert(0, '<td>%s%%</td>' %(refwt))
            ltable2[y].insert(0, '<td>%s%%</td>' %(refwt))
        ofile = open(self.sensitivityFilePath, 'w')
        ofile.write('<html>\n')
        ofile.write('<h2>Sensitivity Results for %s</h2>\n' %(refFileName))
        ofile.write('<h4>Threshold: %s <br>Range:<br>Min: %s%% to Max: %s%%<br>Step Value: %s%% </h4>\n'%(self.sensitivityThreshold,  
                                                                               int(round(self.sensitivityMin*100)), int(round(self.sensitivityMax*100)), 
                                                                               int(round(step*100))))
        ofile.write('<h3>Count of pixels above the sensitivity threshold, per layer, by percentage variation in initial weight.\n')
        ofile.write('<br>Base pixel count: %s</h3>\n'%(refRes['base']))
        ofile.write('<table border=1 cellspacing=0 cellpadding=5>\n')
        ofile.write(''.join(lhead1))
        ofile.write('\n')
        for row in ltable1:
            ofile.write('<tr>')
            ofile.write(''.join(row))
            ofile.write('</tr>\n')
        ofile.write('</table>\n')
        ofile.write('''<p>Cells in <span style="color: royalblue;">blue</span> indicate a difference > %s%% between the cell value and the value in the previous iteration (in increasing order).<br>\n
                    Cells in <span style="color: darkorange;">orange</span> indicate a difference > %s%% between cell values and previous iteration.<br>\n
                    Cells in <span style="color: crimson;">red</span> indicate a difference > %s%% between cell values and previous iteration.</p>\n'''  %(round(step*100, 2), round(200*step, 2), round(300*step, 2)))
        ofile.write('<hr/>\n')
        ofile.write('<h3>Percent variation, per layer, by percentage of variation in initial weight.</h3>\n')
        ofile.write('<table border=1 cellspacing=0 cellpadding=5>\n')
        ofile.write(''.join(lhead1))
        ofile.write('\n')
        for row in ltable2:
            ofile.write('<tr>')
            ofile.write(''.join(row))
            ofile.write('</tr>\n')
        ofile.write('</table>\n')
        ofile.write('''<p>Cells in <span style="color: royalblue;">blue</span> indicate a difference > %s%% between the cell value and the value in the previous iteration (in increasing order).<br>\n
                    Cells in <span style="color: darkorange;">orange</span> indicate a difference > %s%% between cell values and previous iteration.<br>\n
                    Cells in <span style="color: crimson;">red</span> indicate a difference > %s%% between cell values and previous iteration.</p>\n'''  %(round(step*100, 2), round(200*step, 2), round(300*step, 2)))
        ofile.write('</html>')
        ofile.close()

    def runSanityChecks(self):
        """
        Double check to see if basic things are correct (analysis types, weights sum to 1.0, etc.)
        """
        lfactors = len(self.baseQuery.getFactors())
        lweights = len(self.baseQuery.getFactorWeights())
        loweights = len(self.baseQuery.getOrderWeights())
        sumweights = sum(self.baseQuery.getFactorWeights())
        sumoweights = sum(self.baseQuery.getOrderWeights())
        if not lfactors:
            raise MCEliteError("At least one factor is required for an analysis.")
        if self.mceType in ['WLC', 'OWA']:
            if lfactors != lweights:
                raise MCEliteError("There must be one factor weight per factor. Only %s factors and %s weights available." %(lfactors, lweights))
            if  sumweights != 1.0:
                raise MCEliteError("Factor weights must sum to 1.0. Current sum is %s" %(sumweights))
        if self.mceType == 'OWA':
            if lfactors != loweights:
                raise MCEliteError("There must be one order weight per factor. Only %s factors and %s order weights available." %(lfactors, loweights))
            if  sumoweights != 1.0:
                raise MCEliteError("Factor weights must sum to 1.0. Current sum is %s" %(sumoweights))

    def writeMCEConfig(self):
        # Irritating, but this seems needed to deal with line endings across platforms
        # This could be done with XML, but then, as GvR says, not human-readable
        nl = '\n'
        # Local over-ride of self.dconfig_sections source functions
        dformat_sections = {
                     'constraints':nl.join(self.dconfig_sections['constraints']['source']()),
                     'factors':nl.join(self.dconfig_sections['factors']['source']()),
                     'weights':nl.join([str(x) for x in self.dconfig_sections['weights']['source']()]),
                     'oweights':nl.join([str(x) for x in self.dconfig_sections['oweights']['source']()]),
                     'sensitivity':nl.join([str(x) for x in self.getSensitivityIndexes()]),
                     'end':nl,
                     }
        basepath = self.getResultsPath()
        filename = os.path.join(basepath, '%s_configuration_%s.txt' %( self.getResultsFileRoot(), self.mceType))
        try:
            fHandle = open(filename, 'w')
        except:
            raise MCEliteError("File %s cannot be created. Directory may not exist, or you may not have write privileges" %(filename))
        for sect in self.config_sections:
            fHandle.write('%s%s' %(sect, nl))
            val = dformat_sections.get(sect, self.dconfig_sections[sect]['source']())
            if val:
                fHandle.write('%s%s' %(val, nl))
        fHandle.close()

    def readMCEConfig(self, filepath):
        if not filepath: return
        dread = {}
        csect = self.config_sections
        dcsect = self.dconfig_sections
        conf = open(self.configurationFile, 'rU').readlines()
        conf = [x.strip() for x in conf]
        self.configurationFile = filepath
        for sect in csect:
            dread[sect] = {'index':None,
                             'val':[],
                             }
            dread[sect]['index'] = conf.index(sect)
        for ix, sect in enumerate(csect):
            if sect == 'end':
                continue
            val_start = dread[sect]['index']+1
            val_end = dread[csect[ix+1]]['index']
            # Apply type conversions to incoming text: float(), int(), str
            try:
                dread[sect]['val'] = [dcsect[sect]['type'](x) for x in conf[val_start:val_end]]
            except ValueError:
                dread[sect]['val'] = []
            dcsect[sect]['target'](dread[sect]['val'])
            if -999 not in dread['sensitivity']['val']:
                self.setSensitivity(True)

    def writeResultsFile(self):
        outfilepath = self.rp.writeToFile(rasterOb=self.baseQuery.getResults(), 
                            filepath=self.resultsFilePath,
                            gdal_output_format=self.gdal_output_format)
        print('{0} written'.format(outfilepath))
        self.setResultsFilePath(outfilepath)       
                                
    def runQuery(self):
        # Parameters that can be passed for debugging or extra functions:
        # pd is the QGIS Progress Dialog (shows progress of analysis)
        self.runSanityChecks()
        self.writeMCEConfig()
        self.baseQuery.runQuery()
        self.writeResultsFile()
        if self.sensitivity == True:
            self.runSensitivityAnalysis()


class QgisQueryManager(BaseQueryManager):
    '''
    This class is to manage the interaction with QGIS.
    It should be imported into the QGIS dialog (MCEliteDialog.py) and it will manage 
    the transfer of information from the Qt form to a QueryObject, 
    which will then execute the query and return the results  
    '''
        
    def setEnv(self, inEnv=None):
        if inEnv:
            self.env = inEnv
        else:
            self.env = 'QGIS'
       
    def getBaseMCEResultsFile(self):
        return self.baseQuery.resultsFilePath
        
    def exportDataToQueryObject(self, guiOb):
        '''
        Translates data to format used in baseQuery object. 
        ''' 
        baseQ = self.baseQuery
        for key in baseQ.mceData:
            baseQ.mceData[key] = []
        self.setSensitivity(False)
        self.setSensitivityIndex([])
        self.setMCEType(guiOb.MCEType)
        self.setGdalFormat(guiOb.output_format)
        # Loop through User Interface Dictionary and pass results to QueryObject
        # set td to active Tab 
        td = guiOb.uid[guiOb.MCEType]
        # Loop through index values (ix) of rows
        for ix in range(guiOb.maxRows):
            # Loop through criteria names and criteria dict objects of index row
            for crit, critd in td[ix].items():
                # Only loop through visible rows (as defined by GUI dmaxvisible)
                if ix > guiOb.dmaxvisible.get(crit, guiOb.dmaxvisible['rows']):
                    continue 
                # Loop through widgets in criteria: name [filepath, button, weights, oweights, checkbox] and widget
                for wname, widget in critd.items():
                    if wname == 'button': continue
                    elif wname == 'filepath': 
                        otype = crit
                        oval = widget.text()
                        # Exclude things like 'Factor 1'
                        if oval.startsWith(otype.title()): continue
                    elif wname == 'checkbox':
                        if widget.isChecked():
                            self.appendSensitivityIndex(ix)
                        continue
                    else: 
                        otype = wname
                        oval = widget.text()
                        if oval.startsWith('Wt'): continue
                        oval = float(widget.text())
                    self.baseQuery.appendToMCEData(otype, oval)
        self.baseQuery.retypeMCEData()
        # Sensitivity settings, skip Boolean overlay
        if self.mceType == 'Bool':
            return
        if self.sensitivityIndexes:
            self.setSensitivity(True)
        else:
            self.setSensitivity(False)
        self.sensitivityWeights = [self.baseQuery.getFactorWeightByIndex(x) for x in self.getSensitivityIndexes()]
        xyz = '_xyz_'
        guiID = 'sens_xyz_%s' %(self.mceType)
        setID = 'setSensitivity_xyz_'
        for rname in ['Min', 'Max', 'Step', 'Threshold']:
            # Return function and call it with returned attributes at the same time
            getattr(self, setID.replace(xyz, rname))(float(getattr(guiOb.ui, guiID.replace(xyz, rname)).text()))

    def incrementPD(self):
        newVal = self.pd.value() + 1
        self.pd.setValue(newVal)
            
    def runQuery(self, pd):
        # pd is the QGIS Progress Dialog (shows progress of analysis)
        self.pd = pd
        self.runSanityChecks()
        self.writeMCEConfig()
        self.baseQuery.runQuery()
        self.incrementPD()
        self.writeResultsFile()
        self.incrementPD()
        if self.sensitivity == True:
            self.runSensitivityAnalysis()
    


class ArcQueryManager(BaseQueryManager):
    '''
    This class manages interactions with ArcGIS.
    '''

    def setEnv(self, inEnv=None):
        if inEnv:
            self.env = inEnv
        else:
            self.env = 'ESRI'       
    
            
class IdrisiQueryManager(BaseQueryManager):
    '''
    This class manages interactions with IDRISI
    '''
    def __init__(self):
        BaseQueryManager.__init__(self) 
        try:
            import win32com
        except ImportError:
            print('Window modules [win32com] not available.')
            print('Please install or configure win32com module.')
            raise ImportError

    def setEnv(self, inEnv=None):
        if inEnv:
            self.env = inEnv
        else:
            self.env = 'IDRISI'

if __name__ == "__main__":
    # Doctest testing not implemented yet.
    import doctest
    doctest.testmod()
    