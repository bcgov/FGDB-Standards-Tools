# File Geodatabase Standards Tools

## Usage
The File Geodatabase Standards Tools were developed to help in applying the 
GeoBC File Geodatabase Standards.  Please refer to the GeoBC File Geodatabase Standards 
document (http://geobc.gov.bc.ca/common/specs/file_geodatabase_standards.pdf) for further
further information about these tools and the standards they help enforce.

The FGDBStandardsTools.tbx toolbox contains all the tools.  Source scripts for these tools 
are contained in their individual folders.

## Requirements
Requires ESRI ArcInfo licensing & ArcMap 10.0+.

## Getting Help or Reporting an Issue
Use the Issues tab to get help or report any issues.

## Tool Descriptions:
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


## License
<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons Licence"
style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/80x15.png" /></a><br /><span
xmlns:dct="http://purl.org/dc/terms/" property="dct:title">FGDB-Standards-Tools</span> by <span
xmlns:cc="http://creativecommons.org/ns#" property="cc:attributionName">the Province of Britich Columbia
</span> is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">
Creative Commons Attribution 4.0 International License</a>.
