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

    -----------------------------------------------------------------------------------------------
    Purpose: This script prepares a feature class for distribution by doing the following steps.
             -  Creates a directory in the same directory that the input .gdb file is in.
             -  Creates a filebased geodatabase in the above directory with the same name as the input feature class.
             -  Copies the input feature class into the new GDB as a temp feature class.
             xxx remed out -  Projects the temp feature class into the final featureclass using BC MOE Albers.
             xxx remed out -  Deletes the temp feature class.
             xxx remed out -  Repairs the new feature class.
             -  Compacts the new GDB.
             -  Compresses the new GDB.
     
    Date: Oct, 2008

    Arguments: argv0 = script name (does not need to be passed).  argv1 = entire path to featureclass
               i.e. "<FILEPATH>\dataset"
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

import arcpy, sys, string, os, os.path, subprocess
from arcpy import env

arcpy.AddMessage('starting script')    
    
try:
    argThisDataSet = ""
    argScriptName = sys.argv[0]
    argThisDataSet = sys.argv[1]
    selected_featureclass = sys.argv[1]
    
    ZipOutput = False
    argZipOutput = sys.argv[2]
    if argZipOutput == 'true':
        ZipOutput = True
except:
    print "no arguments"

# The below line is just for test without having to supply arguments.

for this_featureclass in individual_featureclasses:
    print this_featureclass

arcpy.AddMessage("")
arcpy.AddMessage("")      
for this_featureclass in individual_featureclasses:
    arcpy.AddMessage('processing   ' + this_featureclass)

    #-----------------------------------------------------------------------------
    # This section splits the selected file into a featureclass name and  a directory
    
    my_gdb, my_featureclass = os.path.split(this_featureclass)
    
    fileExt=os.path.splitext(my_gdb)[-1]
    fileExt = fileExt.lower()
    
    # if my_gdb is not at gdb level, split path one more time (in case input is in feature dataset)
    if fileExt <> ".gdb" :
        my_gdb, my_blank_var = os.path.split(my_gdb)
    
    
    my_directory, my_gdb = os.path.split(my_gdb)
    #-----------------------------------------------------------------------------
    
    
    #-----------------------------------------------------------------    
    # Make a distribution directory to put the new GDB's in    
    distibution_directory = my_directory + "\!distribution"
    try:
        mkdir_string = "mkdir  " + my_directory + "\\!distribution_directory"
        os.system(mkdir_string)
        #os.mkdir("!distribution_directory")      this should work but fails when calling this python function from a tool.
    except:
        who_cares = "not me" #print "" #"obviously exists already"
    #-----------------------------------------------------------------
        
    publish_gdb_path = my_directory + "\\!distribution_directory\\" + my_featureclass + ".gdb"
    publish_gdb_name = "\\!distribution_directory\\" + my_featureclass

    if not arcpy.Exists(publish_gdb_path ):
        arcpy.AddMessage("creating geodatabase  ...")
        arcpy.CreateFileGDB_management(my_directory, publish_gdb_name)
        arcpy.env.workspace =  publish_gdb_path
 
        arcpy.AddMessage("copying into temp dataset  ...")
        arcpy.FeatureClassToFeatureClass_conversion(this_featureclass, publish_gdb_path , my_featureclass)

        arcpy.AddMessage("compacting geodatabase  ...")
        arcpy.Compact_management(publish_gdb_path)
        arcpy.AddMessage("compressing geodatabase  ...")
        arcpy.CompressFileGeodatabaseData_management (publish_gdb_path)
        arcpy.AddMessage("Data now in distribution format.")
        arcpy.AddMessage("")
        arcpy.AddMessage("")
    else:
        arcpy.AddError("No work done.  Output geodatabase already exists.")
        arcpy.AddMessage("")
        arcpy.AddMessage("")
        arcpy.AddMessage("")    
    
    zip_file = publish_gdb_path + ".zip  " 
    zip_string = "zip  -r " + publish_gdb_path + ".zip  " + publish_gdb_path 
    print "zip_file  ", zip_file

    if  ZipOutput is True and arcpy.Exists(zip_file) is True:
        arcpy.AddError("No work done.  Output zip file already exists.")
        arcpy.AddMessage("")
        arcpy.AddMessage("")
    if  ZipOutput is True and arcpy.Exists(zip_file) is False:
        subprocess.call (zip_string)
        arcpy.AddMessage("Data now Zipped.")
        arcpy.AddMessage("")
        arcpy.AddMessage("")

arcpy.AddMessage("")
arcpy.AddMessage("")
arcpy.AddMessage("Distribution data now in !Distribution_Directory")
arcpy.AddMessage("")
arcpy.AddMessage("")