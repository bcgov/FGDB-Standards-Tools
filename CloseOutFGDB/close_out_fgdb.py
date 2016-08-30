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
    Purpose: This script takes user-defined feature classes, checks their geometry, then repairs the geometry 
                if requested by the user.  It then adds a spatial index to each feature class, and compacts 
                and compresses the entire file geodatabase.  If input feature classes are not all from the 
                same file geodatabase, the script will end.
     
    Date: December 2008

    Arguments: argv0 = script name (does not need to be passed).  
               argv1 = feature class/classes path - must all be in the same geodatabase
               argv2 = boolean  - repair geometry or not
               These arguments are meant to be passed to this script from an ArcMap model.
                         
    Outputs: A new "Check Geometry" table will be created within the file geodatabase for each selected feature class

    Dependencies:

    History:
    ----------------------------------------------------------------------------------------------
    Date: November 8, 2012
    Modification: 
        ~ Updated script to use arcpy for ArcGIS 10+
    -----------------------------------------------------------------------------------------------
'''

# Import system modules
import arcpy, sys, string, os, os.path, sys

# Overwrite output feature classes
arcpy.OverwriteOutput = 1

#Script arguments...
try:
    argThisDataSet = ""
    argScriptName = sys.argv[0]
    argThisDataSet = sys.argv[1]
    selected_featureclass = sys.argv[1]
    
    fixGeometry = False
    argFixGeometry = sys.argv[2]
    if argFixGeometry == 'true':
        fixGeometry = True

except:
    print "no arguments"

###################################################
#########     Close out File Geodatabase  #########
###################################################
#--------------------------------------------------------------
#Work on selected feature classes
#--------------------------------------------------------------
individual_featureclasses = selected_featureclass.rsplit(';')
   
prefix = os.path.commonprefix(individual_featureclasses)
gdbPath, fileName = os.path.split(prefix)
print 'common prefix is: ' + prefix
print 'common gdbPath is: ' + gdbPath

fileExt = gdbPath[-4:]
fileExt = fileExt.lower()

# if gdbPath is not at gdb level yet (i.e. is a feature dataset), split path one more time
if fileExt <> ".gdb" :
    gdbPath, fileName = os.path.split(gdbPath)
    gdbPath = gdbPath.lstrip()
    
    fileExt = gdbPath[-4:]
    fileExt = fileExt.lower()
    
    # if splitting gdbPath did not result in a .gdb ending this time, generate an error message & end script
    if fileExt <> ".gdb":
        arcpy.AddError("Operation failed. Check to ensure you have selected feature classes from a SINGLE FILE GEODATABASE.")
        sys.exit()
              

#Start processing feature datasets
for this_featureclass in individual_featureclasses:   
    arcpy.AddMessage("Processing " + this_featureclass)
    
    #Check geometry & generate output table
    arcpy.AddMessage("...checking geometry")
    pathName, fileName = os.path.split(this_featureclass)
    outputTbl = gdbPath + "\\" + fileName + "_ChkGeometry"
    try:
        arcpy.CheckGeometry_management(this_featureclass, outputTbl)
        arcpy.AddMessage("....." + fileName + "_ChkGeometry table created")
        arcpy.AddMessage("..........done!")
    except:
        error_message = arcpy.GetMessages(2)
        arcpy.AddMessage(error_message)
        sys.exit()
 
    #Repair geometry if user selects
    if  fixGeometry is False:
        arcpy.AddMessage("...geometry has not been repaired at user request")

    if  fixGeometry is True:
        arcpy.AddMessage("...repairing geometry")
        try:
            arcpy.RepairGeometry_management(this_featureclass)
            arcpy.AddMessage("..........done!")
        except:
            error_message = arcpy.GetMessages(2)
            arcpy.AddMessage(error_message)
            sys.exit()

    #Add spatial index to feature class
    arcpy.AddMessage("...adding spatial index")
    try:
        arcpy.AddSpatialIndex_management(this_featureclass, "2100", "0", "0")
        arcpy.AddMessage("..........done!")
    except:
        error_message = arcpy.GetMessages(2)
        arcpy.AddMessage(error_message)
    arcpy.AddMessage("")
    
    
#---------------------------------------------------
#Work on file geodatabase
#----------------------------------------------------   

#Compact file geodatabase
arcpy.AddMessage("...compacting " + gdbPath)
try:
    arcpy.Compact_management(gdbPath)
    arcpy.AddMessage("..........done!")
except:
    error_message = arcpy.GetMessages(2)
    arcpy.AddMessage(error_message)
    sys.exit()


#Compress file geodatabase
arcpy.AddMessage("...compressing " + gdbPath)
try:
    arcpy.CompressFileGeodatabaseData_management(gdbPath)
    arcpy.AddMessage("..........done!")
except:
    error_message = arcpy.GetMessages(2)
    arcpy.AddMessage(error_message)
    sys.exit()



print '=======Close Out FGDB script finished======'



