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

	-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

	Instructions: load the ArcToolbox FGDBStandardsTools.tbx

	Note: Do not run this script in PythonWin

	-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
	Purpose:  .  .   To check a file geodatabase contwents for standards compliance
	Date:  . . . . . November 19, 2009
	Version . . . .  1.6
	Arguments: . . . inputFileGeodatabase
	Outputs: . . . . Textfile at same path and name as input, with a TXT extension
	Dependencies: . . arcpy os, sys, time
	Licensing Level: ArcView
	History:
	  Ver 1.0, Nov-03-2008, Initial script created
	  Ver 1.1, Nov-10-2008, Added scanning
	  Ver 1.2, Nov-20-2008, Added reporting
	  Ver 1.3, Dec-01-2008, Adding domain and rel class handling
	  Ver 1.4, Dec-10-2008, Added nameString checking
	  Ver 1.5, Dec-15-2008, Various bug fixes
	  Ver 1.6, Nov-19-2009, Various bug fixes
	  Ver 1.6, Dec 2012, Updated for ArcGIS 10.x using arcpy
	-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

import arcpy, sys, os, copy, time
from arcpy import env

# ===============================================
#
# USER DEFINED FUNCTIONS
#

# Function to return a formatted date string
def returnDateString(dateStamp):
	t = dateStamp
	# format: YYYY_MMM_DD_HHMMSS
	sep = "_"
	formattedDateString = ((t[20:24]+sep+t[4:10]+sep+t[11:19])).replace(":","").replace(" ","_")
	return formattedDateString

# Function to Handle Screen Messaging
#
def msg(msgText):
	global msgMode
	if msgMode == "toolBox":
		arcpy.AddMessage(msgText)
	else:
		print msgText
		return

# Function to Handle Persistent (file) Messaging
#
def fwrite(msgText):
	''' Function handles writing information to a text file
	'''
	global msgFile
	rptFile.write(msgText+"\n")
	rptFile.flush()
	return

# Check name string for standards compliance
#
def validNameString(nameString):
	''' Function to validate text strings '''
	validChars = "1234567890_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"    # Valid characters for name strings
	isValid = True               # result of valid character check
	for char in nameString:
		if not char in validChars:
			isValid = False
	return isValid

# Translate a list object to delimited string
#
def list2string(aList,prop,delim):
	''' Function to convert a list to a comma delimited string '''
	txtString = ""     # output text string
	delimeter = ""     # delimeter between elements in text string
	aList.sort()
	for l in aList:
		txt = l
		if prop <> "":  # property parameter, in case you want the property of an element in aList to be the output
			txt = eval("l"+prop)
		if txt.strip() <> "":
			txtString += delimeter + txt
			delimeter = delim
	return txtString

# Function to Translate Enumerated Index object to List object
#
def returnIdxEnumAsList(enum,excluded,method):
	''' Function to return and index enumeration as a Python list '''

	theList = []  # List to store enumeration elements
	for L in theList:
		aField = (returnEnumAsList(eval("L.Fields"),[],""))[0]    # Return the field associated with an index
		theList.append(eval("aField."+method))   #  Capture field name to list
	return theList
	
# Function to Translate any Enumerated object to List object
#
def returnEnumAsList(enum,excluded,method):
	''' Function to convert an enumeration as a list '''

	theList = []   # A list to store the enumeration elements
	for L in theList:
		if method <> "":
			L = eval("L."+method)   # Capture enum object method, instead of the enum object itself
			if not (L.lower() in excluded):  # Filter out elements in the excluded list
				theList.append(L)
		else:
			theList.append(L)
	return theList
	
# Function to return feature count for a feature layer 
#
def returnRowCount(entPath,entType):
	''' Function to return the number of rows in a table or feature class '''
	#rowCount = int(arcpy.GetCount_management(entPath).getOutput(0))
	if entType.lower().find("feature") > -1:
		if arcpy.Exists("ftrLyr"):
			arcpy.Delete_management("ftrLyr")
		arcpy.MakeFeatureLayer_management(entPath,"ftrLyr")
		rowCount = int(arcpy.GetCount_management("ftrLyr").getOutput(0))
	if entType.lower().find("table") > -1:
		arcpy.MakeTableView_management(entPath,"tblVw")
		rowCount = int(arcpy.GetCount_management("tblVw").getOutput(0))
	return rowCount

# Function to scan entity field list object for domain references
#
def searchForDomainRefs(datasetPath,domainNameList):
	''' Function search for domain references in fieldList objects '''
	fldList = arcpy.ListFields(datasetPath)   # List of fields for a feature class
	for fld in fldList:
		d = fld.domain   # Domain property for a field object
		if d <> "":
			domainNameList.append(d)   # Add domain name to domain list of not blank
	return domainNameList

# Function to scan entity feature class object for relationship class references
#
def searchForRelClassRefs(dscObj,relClassList):
	''' Function to search for relationship classes '''
	clsNmList = dscObj.relationshipClassNames   # List of class names
	if len(clsNmList) > 0:
		for clsNm in clsNmList:
				relClassList.append(clsNm)
	return relClassList

# Function to return geodata index in GDB
#
def returnGeoEntityAttr(fgdbPath,reportType,startTime):
	'''Function to capture file geodatabase entity attributes into a dictionary '''
	geoEntityDict = {}     # dictionary of geodatabase entities
	entityAttrDict = {}    # dictionary of entity attributes
	domainNameList = []    # Possible domain references
	relClassList = []      # Possible relationship class references
	arcpy.env.workspace = fgdbPath
	fdList = arcpy.ListDatasets("*","Feature")  # List of feature datasets
	fdList.append("")      # "root" feature dataset

	# Inventory ftr datasets    
	for fd in fdList:     # Loop through feature dataset workspaces
		if fd <> "":
			ws = fgdbPath+os.sep+fd   # build path to workspace
		else:
			ws = fgdbPath
		arcpy.env.workspace = ws

		msg("Found Feature Dataset: "+os.path.basename(ws))

		# Inventory ftr classes
		entityTypeCode = "01"       # Code for "entity" type  eg. ftr class, table, raster, domain, or rel class
		fcList = arcpy.ListFeatureClasses("*")  # List of feature classes in workspace
			
		for fc in fcList:    # Loop through feature classes

			msg("  Found Feature Class: "+fc)
			# Capture ftr class level attributes
			fcPath = ws+os.sep+fc
			if not validNameString(fc):
				entityAttrDict["nameError"] = True      # Name string error flag
				entityAttrDict["nameErrorDsc"] = "feature class name is non-standard"   # Name string error descriptive text
			else:
				entityAttrDict["nameError"] = False
			try: 
				dsc = arcpy.Describe(fcPath)    # Describe object
			except:
				msg("Error during describe, skipping dataset")
				continue
			entityAttrDict["entityName"] = fc  # Capture ftr class name
			entityAttrDict["type"] = dsc.shapeType   # Capture ftr class shape type
			entityAttrDict["dataset"] = fd   # Capture feature dataset name
			entityAttrDict["datasetPath"] = fcPath  # Capture ftr class dataset path
			entityAttrDict["xyTol"] =  dsc.spatialReference.XYTolerance  # Capture xy tolerance
			entityAttrDict["xyRes"] = dsc.spatialReference.XYResolution  # Capture xy reolsution
			entityAttrDict["prjName"] = dsc.spatialReference.name        # Capture projection name
			# arcpy Change
			entityAttrDict["rowCount"] = returnRowCount(fcPath,"feature") # Capture row count
			entityAttrDict["colCount"] = len(arcpy.ListFields(fcPath))  # Capture column count
			if entityAttrDict["rowCount"] > 0:
				ext = dsc.extent
				entityAttrDict["geoExtent"] = str(ext.XMin)+","+str(ext.YMin)+","+str(ext.XMax)+","+str(ext.YMax)  # Capture spatial extent
			else:
				entityAttrDict["geoExtent"] = "N/A"

			# Check ftr class geometry
			if reportType == "errorCheck":
				geomCheckTableName = fgdbPath+os.sep+fc+"_GeometryCheck_"+startTime    # Output table path name for geometry check output
				if arcpy.Exists(geomCheckTableName):
					arcpy.Delete_management(geomCheckTableName)
				arcpy.CheckGeometry_management(fcPath,geomCheckTableName)
				if arcpy.Exists(geomCheckTableName):
					geomErrCount = arcpy.GetCount_management(geomCheckTableName)   # Count the no. of errors in the geometry check error table
					print "Ftr Count="+str(geomErrCount)," for table "+geomCheckTableName
					if geomErrCount > 0:
						entityAttrDict["geomErrCount"] = str(geomErrCount)
						entityAttrDict["geomErrTable"] = geomCheckTableName+"_"+str(geomErrCount)+"errors"
						arcpy.Rename_management(geomCheckTableName,geomCheckTableName+"_"+str(geomErrCount)+"errors")
					else:
						entityAttrDict["geomErrCount"] = "0"
						if arcpy.Exists(geomCheckTableName):
							arcpy.Delete_management(geomCheckTableName)
				else:
					entityAttrDict["geomErrCount"] = ""
			geoEntityDict[entityTypeCode+"-"+fd+"-"+fc] = entityAttrDict.copy()   # Add collection of entity attributes to dictionary
			domainNameList = searchForDomainRefs(fcPath,domainNameList)[:]        # Get the domain name references for this dataset
			relClassList =   searchForRelClassRefs(dsc,relClassList)[:]           # Get the relationship class names
			entityAttrDict = None
			del entityAttrDict
			entityAttrDict = {}
			
		# Inventory tables
		entityTypeCode = "02"       # Entity code for a table
		tbList = arcpy.ListTables("*")   # Get a list of tables at the current workspace
		for tb in tbList:    # Loop through the tables

			msg("  Found Table: "+tb)
			if tb.find("_GeometryCheck_") > -1:
				print "Skipping geometry error check table"
				continue
			if not validNameString(tb):
				entityAttrDict["nameError"] = True   # Name string error flag
				entityAttrDict["nameErrorDsc"] = "table name is non-standard"   # Name string error description
			else:
				entityAttrDict["nameError"] = False 
			# Capture table attributes
			tbPath = ws+os.sep+tb    # Table path
			try:
				dsc = arcpy.Describe(tbPath)   # Describe object
			except:
				msg("Error during describe, skipping dataset")
				continue
			entityAttrDict["entityName"] = tb   # Table Name
			entityAttrDict["type"] = "Table"    # Entity type
			entityAttrDict["dataset"] = ""   # Dataset path, always null for tables
			entityAttrDict["datasetPath"] = tbPath   # Path to table
			entityAttrDict["prjName"] = ""   # No projection for tables
			entityAttrDict["colCount"] = len(arcpy.ListFields(tbPath))   # Column (field) count
			entityAttrDict["rowCount"] = returnRowCount(tbPath,"table")   # Row count
			geoEntityDict[entityTypeCode+"-"+fd+"-"+tb] = entityAttrDict.copy()  # Add collection of entity attributes to dictionary
			domainNameList = searchForDomainRefs(tbPath,domainNameList)[:]   # List of domain names
			entityAttrDict = None   
			del entityAttrDict
			entityAttrDict = {}

		# Inventory rasters
		entityTypeCode = "03"     # Entity type code for rasters
		rsList = arcpy.ListRasters("*")   # Get a list of rasters in the current workspace
		for rs in rsList:    # Loop through each raster
			msg("  Found raster: "+rs)
			if not validNameString(rs):
				entityAttrDict["nameError"] = True
				entityAttrDict["nameErrorDsc"] = "raster name is non-standard"
			else:
				entityAttrDict["nameError"] = False
			# Capture raster attributes
			rsPath = ws+os.sep+rs    # Full path to raster dataset
			try:
				dsc = arcpy.Describe(rsPath)   # Describe object
			except:
				msg("Error during describe, skipping dataset")
				continue
			entityAttrDict["entityName"] = rs     # Capture raster name
			entityAttrDict["type"] = "Raster"     # Capture entity type
			entityAttrDict["dataset"] = ""        # Capture feature dataset path, always blank for rasters
			entityAttrDict["datasetPath"] = rsPath  # Capture full path to raster dataset
			entityAttrDict["prjName"] = dsc.SpatialReference.name  # Capture projection name
			# arpy change
			ext = dsc.extent
			entityAttrDict["geoExtent"] = str(ext.XMin)+","+str(ext.YMin)+","+str(ext.XMax)+","+str(ext.YMax)  # Capture spatial extent
			entityAttrDict["colCount"] = dsc.width  # Capture raster column width (pixels wide)
			entityAttrDict["rowCount"] = dsc.height  # Capture raster row height (pixels high)
			entityAttrDict["colSize"] = dsc.meanCellWidth  # Capture raster cell width
			entityAttrDict["rowSize"] = dsc.meanCellHeight # Capture raster cell height 
			entityAttrDict["pixelType"] = dsc.pixelType # Capture raster pixel type (bit depth)
			entityAttrDict["primaryField"] = dsc.primaryField  # Capture raster primary field
			entityAttrDict["tableType"] = dsc.tableType   # Capture raster table type
			geoEntityDict[entityTypeCode+"-"+fd+"-"+rs] = entityAttrDict.copy()   # Add collection of entity attributes to dictionary
			entityAttrDict = None
			del entityAttrDict
			entityAttrDict = {}

	# Inventory domains
	entityTypeCode = "04"       # Entity type code
	for dn in domainNameList:   # Loop through domain names
		if not validNameString(dn):
			entityAttrDict["nameError"] = True   # Name string error flag
			entityAttrDict["nameErrorDsc"] = "domain name is non-standard"  # Name string error description
		else:
			entityAttrDict["nameError"] = False
		entityAttrDict["entityName"] = dn   # Capture domain name
		entityAttrDict["type"] = "Domain"   # Capture entity type
		entityAttrDict["dataset"] = " "     # Feature dataset, always blank for this entity type
		entityAttrDict["prjName"] = " "     # Projection name, always blank
		entityAttrDict["colCount"] = " "    # Column count, always blank
		entityAttrDict["rowCount"] = " "    # Row count, always blank
		geoEntityDict[entityTypeCode+"--"+dn] = entityAttrDict.copy()  # Add collection of entity attributes to dictionary
		entityAttrDict = None
		del entityAttrDict
		entityAttrDict = {}

	# Inventory relationship classes
	entityTypeCode = "05"   # Entity type code
	for rc in relClassList: # Loop through relationship classes
		if not validNameString(rc):
			entityAttrDict["nameError"] = True   # Name string error flag
			entityAttrDict["nameErrorDsc"] = "relationship class name is non-standard"   # Name string error description
		else:
			entityAttrDict["nameError"] = False
		entityAttrDict["entityName"] = rc     # Capture name of rel class
		entityAttrDict["type"] = "Rel Class"  # Capture entity type
		entityAttrDict["dataset"] = " "       # Feature dataset, always blank for this entity type
		entityAttrDict["prjName"] = " "       # Projection name, always blank
		entityAttrDict["colCount"] = " "	  # Col count, always blank
		entityAttrDict["rowCount"] = " "      # Row count, always blank
		print "RC: ",rc
		geoEntityDict[entityTypeCode+"--"+rc] = entityAttrDict.copy()  # Add collection of entity attributes to dictionary
		entityAttrDict = None      
		del entityAttrDict
		entityAttrDict = {}

	return geoEntityDict

def displayGeoEntityAttrSummary(geoEntityDict,reportType):
	'''Function to display file geodatabase entity attribute information in summary format'''
	fwrite(" ")
	fwrite("==============================")
	fwrite("GEODATABASE CONTENT OVERVIEW =")
	fwrite("==============================")
	fwrite(" ")
	fwrite("Date: "+time.ctime(time.time()))
	fwrite("Path: "+fgdbPath)
	fwrite(" ")

	ovFmtString  = "%-65s %-30s %-10s %-8s %-7s %-25s %-5s"

	fwrite(ovFmtString % ("","Feature","Entity","Row","Fld/Col","","Geometry"))
	fwrite(ovFmtString % ("Entity Name","Dataset","Type","Count","Count","Projection","Errors"))
	fwrite(ovFmtString % ("-"*63,"-"*29,"-"*9,"-"*7,"-"*6,"-"*24,"-"*8))

	# Access dictionary elements in sorted order
	entityKeyList = geoEntityDict.keys()    # Get entity dictionary keys
	print "Entity Keys: ", geoEntityDict.keys()
	entityKeyList.sort()                    # Sort list of keys
	for entityKey in entityKeyList:   # Iterate through dict keys
		entityAttrDict = geoEntityDict.get(entityKey)  # Get entity attribute dictionary
		entityName = entityAttrDict["entityName"]      # Get entity name
		nameError = entityAttrDict.get("nameError",False)  # Get name string error flag
		nameErrorDsc = entityAttrDict.get("nameErrorDsc","")  # Get name string error description
		dataset = entityAttrDict["dataset"] # Get feature dataset name
		entityType = entityAttrDict["type"]  # Get entity type
		rowCount = entityAttrDict["rowCount"]  # Get entity row count, blank for non relevant entity types
		colCount = entityAttrDict["colCount"]  # Get entity col count, blank for non relevant entity types
		prjName = entityAttrDict["prjName"].replace("NAD_1983_","")  # Get projection name, delete datum portion for concise presentation
		prjWarning = not "albers" in prjName.lower() and prjName <> ""
		geomErrCount = entityAttrDict.get("geomErrCount","")  # Get geometry error count
		
		fwrite(ovFmtString % (entityName,dataset,entityType,rowCount,colCount,prjName,geomErrCount))
		
	# Errors and warnings
	'''
	~nameError throws error (UnboundLocalError) likely because it is not bound or assigned to an object
	~if 'global' statement is used it throws a (NameError)
	~As per python documentation http://docs.python.org/2/reference/simple_stmts.html#global
		'Names listed in a global statement must not be defined as formal parameters or in a for loop control target, 
		class definition, function definition, or import statement.'
	~Would use nonlocal statement if using Python 3.x
	~Suggestions is to store it inside a dict instead of a stand-alone variable.
	'''
	
	if nameError:
		fwrite (" ")
		fwrite(nameErrorDsc)

	if prjWarning:
		fwrite (" ")
		fwrite("Warning: one or more layers has a non Albers projection")

	return

def displayGeoEntityAttrDetails(geoEntityDict,reportType):
	'''Function to display file geodatabase entity attribute information in detailed format'''
	fwrite(" ")
	fwrite(" ")
	fwrite("=============================")
	#fwrite("                            =")
	fwrite("GEODATABASE CONTENT DETAILS =")
	#fwrite("                            =")
	fwrite("=============================")
	fwrite(" ")

	# Access dictionary elements in sorted order
	entityKeyList = geoEntityDict.keys()       # Get GeoEntity dictionary keys
	entityKeyList.sort()
	for entityKey in entityKeyList:      # Iterate through key values
		entityAttrDict = geoEntityDict.get(entityKey)    # Get Entity attribute Dictionary, from entity dictionary
		entityName = entityAttrDict["entityName"]        # Get entity name from dict
		dataset = entityAttrDict["dataset"]              # Get feature dataset name
		entityType  = entityAttrDict["type"]             # Get entity type 
		entityTypeCode = entityKey.split("-")[0]         # Parse entity type code from key

		if entityTypeCode == "01":
			geoExtent = entityAttrDict["geoExtent"]    # Get spatial extent from dict
			type = entityAttrDict["type"]              # Get entity type
			prjName = entityAttrDict["prjName"]        # Get projection name
			prjWarning = not "albers" in prjName.lower() and prjName <> ""
			xyTol = entityAttrDict["xyTol"]   # Get xy tolerance
			xyRes = entityAttrDict["xyRes"]   # Get xy resolution
			colCount = entityAttrDict["colCount"]  # Get column count (field count)
			rowCount = entityAttrDict["rowCount"]  # Get row count (ftr count)
			datasetPath = entityAttrDict["datasetPath"]  # Get path to dataset
			geomErrCount = entityAttrDict.get("geomErrCount","")  # Geometry error count
			geomErrTable = entityAttrDict.get("geomErrTable","")  # Get geometry error table
			fldList = arcpy.ListFields(datasetPath)   # Get list of fields
			idxList = arcpy.ListIndexes(datasetPath)  # Get list of field indexes

			fwrite("Feature Class Entity")
			fwrite("="*20)
			fwrite("Name:            "+entityName)
			fwrite("Feature Dataset: "+dataset)
			fwrite("Spatial Extent:  "+geoExtent)
			fwrite("Projection:      "+prjName)
			fwrite("XY Tolerance:    "+str(xyTol))
			fwrite("XY Resolution:   "+str(xyRes))
			fwrite("Shape Type:      "+type)
			fwrite("Shape Count:     "+str(rowCount))
			fwrite("Field Count:     "+str(colCount))
			fwrite(" ")
		
			# Check for standards compliance
			if prjWarning and reportType == "errorCheck":
				fwrite("Warning: this layer doesn't have a BC Albers projection")			
			if geomErrCount <> "0"  and reportType == "errorCheck":
				fwrite("Warning: geometry errors encountered")
				fwrite("  Geometry error count: "+geomErrCount)
				fwrite("  Geometry error table: "+geomErrTable)
			if xyTol < 0.05  and reportType == "errorCheck":
				fwrite("Warning: the xy tolerance value of "+str(xyTol)+" might be too small, please review")
			if xyTol > 50  and reportType == "errorCheck":
				fwrite("Warning: the xy tolerance value of "+str(xyTol)+" might be too big, please review")
			if xyRes <> 0.0001  and reportType == "errorCheck":
				fwrite("Warning the xy resolution value of "+str(xyRes)+" is in error, it should be 0.0001, which is the default")
			displayAttributeTableDetail(fldList,idxList,reportType)

		if entityType == "Raster":
			geoExtent = entityAttrDict["geoExtent"]  # Get spatial extent
			prjName = entityAttrDict["prjName"]      # Get projection name
			colCount = entityAttrDict["colCount"]    # Get pixel width count
			rowCount = entityAttrDict["rowCount"]    # get pixel height count
			colSize = entityAttrDict["colSize"]      # Get pixel x size
			rowSize = entityAttrDict["rowSize"]      # Get pixel y size
			pixelType = entityAttrDict["pixelType"]  # Get pixel type (bit depth, and signed-ness)
			pTypeDict = {"U":"Unsigned Integer","S":"Signed Integer","F":"Floating Point"}
			pixelTypeText = pTypeDict.get(pixelType[0:1],"?")+ " "+pixelType[1:]+" bit"
			primaryField = entityAttrDict["primaryField"]  # Get raster primary field
			tableType = entityAttrDict["tableType"]   # Get raster table type
			
			fwrite("Raster Entity")
			fwrite("="*13)
			fwrite("Name:           "+entityName)
			fwrite("Spatial Extent: "+geoExtent)
			fwrite("Projection:     "+prjName)
			fwrite("Column Count:   "+str(colCount))
			fwrite("Row Count:      "+str(rowCount))
			fwrite("Column Size:    "+str(colSize))
			fwrite("Row Size:       "+str(rowSize))
			fwrite("Table Type:     "+str(tableType))
			fwrite("Primary Field:  "+str(primaryField))
			fwrite("Pixel Type:     "+pixelTypeText)

			if prjWarning and reportType == "errorCheck":
				fwrite("Warning: this layer doesn't have a BC Albers projection")			
		
		if entityType == "Table":

			colCount = entityAttrDict["colCount"]     # Get table column count (field count)
			rowCount = entityAttrDict["rowCount"]     # Get table row count
			datasetPath = entityAttrDict["datasetPath"]  # Get path to dataset
			fldList = arcpy.ListFields(datasetPath)  # Get list of tables
			idxList = returnIdxEnumAsList(arcpy.ListIndexes(datasetPath),[],"name")  # Ge tlist of field indexes

			fwrite("Table Entity")
			fwrite("="*12)
			fwrite("Name:        "+entityName)
			fwrite("Row Count:   "+str(rowCount))
			fwrite("Field Count: "+str(colCount))

			displayAttributeTableDetail(fldList,idxList,reportType)
			
		fwrite (" ")

	return

def displayAttributeTableDetail(fldList,idxList,reportType):
	'''Function to display detailed table structure information'''

	detailFmtString  = "%-30s %-30s %-12s %-7s %-7s %-8s %-25s"
	fieldCaseWarning = False     # Flag for field name case check (should be uppercase)
	fwrite(" ")
	fwrite(detailFmtString % ("Field","Alias","Field"," "     ,"Allows","Is",     "Domain"))
	fwrite(detailFmtString % ("Name","Name",  "Type", "Length","Nulls", "Indexed","Name"))
	fwrite(detailFmtString % ("-"*29,"-"*29,"-"*11,"-"*6,"-"*6,"-"*7,"-"*24))
	for f in fldList:    # Iterate through field objects
		if f.name.islower() and f.name <> "Shape":
			fieldCaseWarning = True
		if f.name in idxList:
			hasIndex = True
		else:
			hasIndex = False
		fwrite(detailFmtString % (f.name,f.aliasName,f.type,f.length,str(f.isNullable),hasIndex,f.domain))
		
	if fieldCaseWarning  and reportType == "errorCheck":		
		fwrite (" ")
		fwrite ("Warning: one or more fields has a name that is not completely upper case")
	return

def displayCredits():
	fwrite(" ")
	fwrite("Report produced by Check_FGDB tool")
	fwrite("Check_FGDB tool created by Kamloops Regional GeoBC, 2009")


# ########################################################################
#
#  MAIN CODE BLOCK
#
# ########################################################################

# Detect script parameters, or set default if none
#   Parameter 1 - file geodatabase source path
#   Parameter 2 - report Type (describe, or errorCheck)

msgMode = "console"
startTime = returnDateString(time.ctime(time.time()))

if len(sys.argv) > 1:
	fgdbPath = sys.argv[1]   # path to file geodatabase being checked/reported on

if len(sys.argv) > 2:
	reportType = sys.argv[2]
	msgMode = "toolBox"      # Controls whether messages goto gp or to the console via print

if len(sys.argv) == 1:
	#Hardcode your file path or create argument to accept the file path
	fgdbPath = r"<FILEPATH>/myProject.gdb"
	reportType = "errorCheck"
	verbose = True
	msgMode = "console"

rptFilePath = fgdbPath.replace(".gdb",".txt")
rptFile = open(rptFilePath,"w")    # The output text report file

msg("")
msg("Examining file geodatabase: "+fgdbPath)
msg ("")

arcpy.OverwriteOutput = "True"

if not fgdbPath.lower().endswith(".gdb"):
	fgdbSrc += ".gdb"

if not arcpy.Exists(fgdbPath):
	msg("The source file geodatabase was not found, you specified "+fgdbPath+", terminating script")
	sys.exit()
geoEntityDict = returnGeoEntityAttr(fgdbPath,reportType,startTime) #gp for arcpy?
displayGeoEntityAttrSummary(geoEntityDict,reportType)
displayGeoEntityAttrDetails(geoEntityDict,reportType)
displayCredits()

if msgMode == "toolBox":
	msg("report file available at: "+rptFilePath)
	