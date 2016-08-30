'''
    Copyright 2015-16 Province of British Columbia

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at 

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    ----------------------------------------------------------------------------------------------
    Purpose: This script checks the geometry of all featureclasses in a file based geodatabase.
             The code that does the work comes directly from the esri help for check_geometry.  All
             I did was wrap it in a few lines of code that allow it to loop through a bunch of
             FGDB's supplied to it from a tool.
             `
    Date: Oct, 2008

    Arguments: argv0 = script name (does not need to be passed).  argv1 = entire path to featureclass
               i.e. "<FILEPATH>\myProject.gdb"
               These arguments are meant to be passed to this script from an ArcMap model.
    Outputs:

    Dependencies:

    History:
    ----------------------------------------------------------------------------------------------
    Date: November 8, 2012
    Modification:
        ~ Updated script to use arcpy for ArcGIS 10+
    -----------------------------------------------------------------------------------------------
'''

import arcpy, sys, string, os, os.path
   
try:
    argThisDataSet = ""
    argScriptName = sys.argv[0]
    argThisDirectory = sys.argv[1]
    argThisGdbName = sys.argv[2]
    argThisDatasetName = sys.argv[3]
    argThisTolerance = sys.argv[4]        
    
except:
    print "no arguments"

# add .gdb to the gdb name if it is not already there.
fileExt=os.path.splitext(argThisGdbName)[-1]
if fileExt <> '.gdb' :
    argThisGdbName = argThisGdbName + ".gdb"

#create the gdb if it does not exist.
arcpy.AddMessage("");arcpy.AddMessage("")
if not arcpy.Exists(argThisDirectory + "\\" +  argThisGdbName):
    arcpy.CreateFileGDB_management(argThisDirectory, argThisGdbName)
    arcpy.AddMessage ("The Geodatabase " + argThisDirectory +"\\" +  argThisGdbName + " has been created.")

else:
    arcpy.AddWarning ("The Geodatabase " + argThisDirectory +"\\" +  argThisGdbName + " already exists.")
    
if     argThisDatasetName <> "#" :
        
    #create the feature dataset if it does not exist.
    arcpy.AddMessage("")
    if not arcpy.Exists(argThisDirectory + "\\" +  argThisGdbName + "\\" + argThisDatasetName):
    
        #Create Spatial Reference for Albers
        sr = "PROJCS['PCS_Albers',\
            GEOGCS['GCS_North_American_1983',\
            DATUM['D_North_American_1983',SPHEROID['GRS_1980',\
            6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],\
            UNIT['Degree',0.0174532925199433]],\
            PROJECTION['Albers'],\
            PARAMETER['False_Easting',1000000.0],\
            PARAMETER['False_Northing',0.0],\
            PARAMETER['Central_Meridian',-126.0],\
            PARAMETER['Standard_Parallel_1',50.0],\
            PARAMETER['Standard_Parallel_2',58.5],\
            PARAMETER['Latitude_Of_Origin',45.0],\
            UNIT['Meter',1.0]];IsHighPrecision"
         
        #Set xy tolerances    
        tolerance_string = str(argThisTolerance) + " Meters"
        #print tolerance_string
        arcpy.env.XYTolerance = tolerance_string
        arcpy.env.ZTolerance = tolerance_string
    
        arcpy.CreateFeatureDataset_management(argThisDirectory + "\\" +  argThisGdbName, argThisDatasetName, sr)
        arcpy.AddMessage ("The Feature Dataset " + argThisDirectory + "\\" +  argThisGdbName + "\\" +  argThisDatasetName + " has been created.")
    
    else:
        arcpy.AddWarning ("The Feature Dataset " + argThisDirectory + "\\" +  argThisGdbName + "\\" +  argThisDatasetName + " already exists.")
            
arcpy.AddMessage("");arcpy.AddMessage("")