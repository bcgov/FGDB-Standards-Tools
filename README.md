# FGDB-Standards-Tools

FGDBStandardsTools - File Geodatabase Standards Tools.

The File Geodatabase Standards Tools were developed to help in applying the 
GeoBC File Geodatabase Standards.  Please refer to the GeoBC File Geodatabase Standards 
document (http://geobc.gov.bc.ca/common/specs/file_geodatabase_standards.pdf) for further
further information about these tools and the standards they help enforce.

The FGDBStandardsTools.tbx toolbox contains all the tools.  Source scripts for these tools 
are contained in their individual folders.


###Tool Descriptions:

**CheckFGDB - Checking/Reporting Tool**

	This tool inventories the contents of a file geodatabase  reporting out into text 
	file a summary of the entities and their properties.  The output reports consists 
	of two sections.  The first section contains a consise summary of the entities 
	found within the geodatabase.  The second section contains detailed information 
	about each entity.

**CreateFgdbAndDatasets - Create New File Geodatabase with Feature Dataset Tool**

	The Create New File Geodatabase tool is a shortcut to create a new FGDB with a 
	feature dataset in the BC Albers projection and the specified XY tolerance.  If 
	the geodatabase already exists, the script will continue and create the new feature 
	dataset within it.

**ApplyDefaultTopology - Apply Default Topology Tool**

	The Apply Default Topology tool creates a new topology element in the indicated 
	feature dataset, applies the standard generic topology rules to the selected 
	feature classes, and optionally validates the topology to find errors.
	Users may wish to edit the topology element afterwards to apply additional more 
	specific topology rules afterwards.

**CloseOutFGDB - FGDB Project Close-out Tool**

	The FGDB Project Close-out tool is used to close-out a FGDB once a project is 
	complete.  It compacts the geodatabase, compresses the geodatabase, re-calculates 
	the spatial indexes of feature classes, runs the Check Geometry command, 
	and (optionally) runs the Repair Geometry command.

**PrepareFeatureClassForDistribution - FGDB Publication/Distribution Tool**

	The Publication and Distribution tool prepares individual feature classes for 
	publication and/or distribution by copying them to their own geodatabases that 
	conform to the publication standards.  The tool puts selected feature classes each 
	in their own FGDB named the same as the feature class name, compresses the new 
	FGDB, and (optionally) zips the FGDB giving it a name <FGDB name>.gdb.zip. 


##License
Copyright 2015 Province of British Columbia

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at 

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
