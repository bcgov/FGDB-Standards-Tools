'''
	Copyright 2011-16 Province of British Columbia

	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at 

	   http://www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.

	---------------------------------------------------------------------------
	ApplyDefaulTology.py
	---------------------------------------------------------------------------
	Purpose: This script will create a topology element and apply generic topology rules to each feature class.
		Generic Topology Rules that are applied:
			Polygons:  
				   Must not overlap
				   Must not have gaps
				   Must be covered by feature class of (applied if Boundary Polygon argument is used)
			Lines:	   
				   Must not have pseudonodes
				   Must not self intersect
				   Must not self overlap
				   Must be inside
			Points:
				   Must be properly inside polygons (applied if Boundary Polygon argument is used)
	Created on: October 2008
	
	Usage: ApplyDefaultTopology.py <Feature_Dataset><Topology_Name><Feature_Class{;Feature_Class}...>{Cluster_Tolerance}{Boundary_Polygon}{Validate}
	
	Arguments:
	Feature_Dataset - Feature Dataset to create the topology element in (and where the Feature Classes to apply topology to reside)
	Topology_Name	- Name of the topology element
	Feature_Class(es) - Feature Class or Feature Classes to apply topology to.  
				When multiple feature classes are selected separate feature classes by a semi colon.
				When multiple feature classes are selected, their RANK is determined by their order.
	Cluster_Tolerance - Will default to the XY tolerance of the feature dataset in Meters. 
	Boundary_Polygon - The boundary to make sure features are within.
	Validate	- Boolean variable.  When populated the topology will be validated.
	
	Outputs:
	A topology element set up according to parameters
	
	Dependencies (deprecated):
	This tool requires that the 'AddRuleToTopologyModel' model exist within its same toolbox.  
	This model runs the 'Add Rule To Topology' tool.  It is called as a work around to correct 
	a known error preventing the tool from running when called through a script tool.  
	http://support.esri.com/en/bugs/nimbus/TklNMDc4MDkz

	History:
	Date: November 8, 2012
	Modification:
	    ~ Updated script to use arcpy for ArcGIS 10+
		- added new topology rule for lines "must be inside"
		~ removed custom model as it is not necessary in ArcGIS 10 (SP5) and higher
	      ~ The "obtained from" was available in 9.2 (it was called Dependency) for FeatureLayer but has been removed 
	          in the supported type at 9.3/10.x. It was found the this this scripts parameters for "Participating
	          Feature Class" and subsequently removed.
	Level of Licensing:
	Requires ArcInfo licensing
	---------------------------------------------------------------------------
'''

# Import system modules
import arcpy, sys, os

# Scripts Arguments
if len(sys.argv) > 1:
	# Feature Dataset to create the topology element in 
	#  (and where the Feature Classes to apply topology to will reside)
	featureDataset = sys.argv[1]
else:
	arcpy.AddMessage('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nMissing required argument for Feature Dataset.\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
	
if len(sys.argv) > 2:
	# Name of the topology element
	topologyName = sys.argv[2]
else:
	arcpy.AddMessage('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nMissing required argument for Topology.\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
if len(sys.argv) > 3:
	# Feature Class or Feature Classes to apply topology to.  
	#  When multiple feature classes are selected separate feature classes by a semi colon.
	#  When multiple feature classes are selected, their RANK is determined by their order.
	featureClasses = sys.argv[3]
else:
	arcpy.AddMessage('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nMissing required argument for Feature Class.\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
if len(sys.argv) > 4:
	# Will default to the XY tolerance of the feature dataset. 
	clusterTolerance = sys.argv[4] 
else:  clusterTolerance = 0
if len(sys.argv) > 5:
	# The boundary feature class to make sure features are within.
	if sys.argv[5] == '#':
		boundaryFC = ''
	else:
		# Changed to use os.path because of fragile string manipulation
		boundaryFC = os.path.basename(sys.argv[5])
		if boundaryFC >= 0:
			boundaryFC
else:  boundaryFC = ''
if len(sys.argv) > 6:
	# Boolean variable.  When populated the topology will be validated.
	if sys.argv[6] == '#':
		validateBln = ''
	else:
		validateBln = sys.argv[6]
else:  validateBln = ''

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
#  Create Topology 
#  Add Participating Feature Classes
#  Add Rules to Topology
#  Validate Topology
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# Set workspace to the Feature Dataset
arcpy.env.workspace = featureDataset

# ---------------------------------------------------------------------------
# Create Topology
# ---------------------------------------------------------------------------
try:
	if not arcpy.Exists(topologyName):
		arcpy.AddMessage('\nCreating new topology element: '+featureDataset+'\\'+topologyName+'...')
		arcpy.CreateTopology_management(featureDataset,topologyName,clusterTolerance)
	else:
		arcpy.AddWarning('Topology '+topologyName+' already exists.')
except:
	arcpy.AddError(arcpy.GetMessages(2))
	sys.exit()
			

# ---------------------------------------------------------------------------
# Loop through list of feature classes:
#	Add participating feature classes
#	Apply Topology rules to feature class
# ---------------------------------------------------------------------------
featureClassList = featureClasses.rsplit(';')
rank = 0 # Rank of participating feature classes is determined by the order they are listed

# If the optional Boundary Feature Class was given, then add it to the topology
if boundaryFC:
	# If 'boundaryFC' exists in the topology first so that rules that require it are ready to go
	if featureClassList.count(featureDataset+'\\'+boundaryFC) > 0:  
		arcpy.AddMessage('\nAdding '+boundaryFC+' to '+topologyName+' topology with a rank of '+str(featureClassList.index(featureDataset+'\\'+boundaryFC)+1)+'...')
		try:
			arcpy.AddFeatureClassToTopology_management(featureDataset+'/'+topologyName,boundaryFC,featureClassList.index(featureDataset+'\\'+boundaryFC)+1,featureClassList.index(featureDataset+'\\'+boundaryFC)+1)
		except:
			if arcpy.AddMessage(2):
				arcpy.AddWarning(arcpy.AddMessage(2))
				arcpy.AddWarning('	'+boundaryFC+' already participates in a topology and may not be available\n or the it is compressed and needs to be uncompressed before it can be added to a topology.')
	else:  # If 'boundaryFC' is not part of the list, add it to the topology first with no rules
		arcpy.AddMessage('\nAdding '+boundaryFC+' to '+topologyName+' topology with a rank of 50...')
		try:
			arcpy.AddFeatureClassToTopology_management(featureDataset+'/'+topologyName,boundaryFC,50,50)
		except:
			if arcpy.GetMessages(2) and arcpy.GetMessages(2).find('compressed') > 0:
				arcpy.AddError(arcpy.GetMessages(2))
				sys.exit()
			elif arcpy.GetMessages(2):
				arcpy.AddWarning(arcpy.GetMessages(2))
				arcpy.AddWarning('	'+boundaryFC+' already participates in a topology and may not be available.')

for featureClass in featureClassList:

	# Add participating feature class to Topology
	rank = rank + 1

	arcpy.AddMessage('\nAdding '+featureClass+' to '+topologyName+' topology with a rank of '+str(rank)+'...')
	try:
		arcpy.AddFeatureClassToTopology_management(featureDataset+'/'+topologyName,featureClass,rank,rank)
	except:
		if arcpy.GetMessages(2) and arcpy.GetMessages(2).find('compressed') > 0:
			arcpy.AddError(arcpy.GetMessages(2))
			sys.exit()
		elif arcpy.GetMessages(2):
			arcpy.AddWarning(arcpy.GetMessages(2))
		arcpy.AddWarning('	'+featureClass+' already participates in a topology and may not be available.')


	# Determine type of geometry
	featureType = arcpy.Describe(featureClass).shapeType
	# For Polygon apply rules:
	#   Must not overlap
	#   Must not have gaps
	#   Must be covered by feature class of (when boundaryFC exists)
	if featureType == 'Polygon':
		try:
			arcpy.AddMessage('	Applying '+featureClass+' Must Not Overlap rule...')
			arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Not Overlap (Area)',featureClass)
			arcpy.AddMessage('	Applying '+featureClass+' Must Not Have Gaps rule...')
			arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Not Have Gaps (Area)',featureClass)
			if boundaryFC and featureClass.find(boundaryFC) < 0:
				arcpy.AddMessage('	Applying '+featureClass+' Must Be Covered By Feature Class Of '+boundaryFC+' rule...')
				arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Be Covered By Feature Class Of (Area-Area)',featureClass,'#',featureDataset+"\\"+boundaryFC)
		except:
			if arcpy.GetMessages(1):
				arcpy.AddWarning(arcpy.GetMessages(1))
			if arcpy.GetMessages(2):
				arcpy.AddError(arcpy.GetMessages(2))
				arcpy.AddError('The Feature Class may already be participating in a different topology element or the feature class may need to be uncompressed.')
				sys.exit()
	
	# For Lines apply rules:
	#   Must not have pseudonodes
	#   Must not self intersect
	#   Must not self overlap
	#   Must be covered by boundary of (when boundaryFC exists)
	#	Must be inside
	elif featureType == 'Polyline':
		try:
			arcpy.AddMessage('	Applying '+featureClass+' Must Not Have Pseudo-Nodes rule...')
			arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Not Have Pseudo-Nodes (Line)',featureClass)
			arcpy.AddMessage('	Applying '+featureClass+' Must Not Self-Intersect rule...')
			arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Not Self-Intersect (Line)',featureClass)
			arcpy.AddMessage('	Applying '+featureClass+' Must Not Self-Overlap rule...')
			arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Not Self-Overlap (Line)',featureClass)
			if boundaryFC and featureClass.find(boundaryFC) < 0:
				arcpy.AddMessage('	Applying '+featureClass+' Must Be Inside (Line-Area) rule...')				
				arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Be Inside (Line-Area)',featureClass,'#',featureDataset+"\\"+boundaryFC)
		except:
			if arcpy.GetMessages(1):
				arcpy.AddWarning(arcpy.GetMessages(1))
			if arcpy.GetMessages(2):
				arcpy.AddError(arcpy.GetMessages(2))
				arcpy.AddError('The Feature Class may already be participating in a different topology element\n or the feature class may need to be uncompressed.')
				sys.exit()
	# For Points apply rules:
	#   Must be covered by boundary of (when boundaryFC exists)
	elif featureType == 'Point':
		if boundaryFC:
			try:
				arcpy.AddMessage('	Applying '+featureClass+' Must Be Properly Inside '+boundaryFC+' rule...')
				arcpy.AddRuleToTopology_management(featureDataset+"\\"+topologyName,'Must Be Properly Inside (Point-Area)',featureClass,'#',featureDataset+"\\"+boundaryFC)				
			except:
				if arcpy.GetMessages(1):
					arcpy.AddWarning(arcpy.GetMessages(1))
				if arcpy.GetMessages(2):
					arcpy.AddError(arcpy.GetMessages(2))
					arcpy.AddError('The Feature Class may already be participating in a different topology element\n or the feature class may need to be uncompressed.')
					sys.exit()

# ---------------------------------------------------------------------------
#  Validate Topology if validation boolean is true
# ---------------------------------------------------------------------------
if validateBln:
	arcpy.AddMessage('\nValidating new topology element...')
	arcpy.ValidateTopology_management(featureDataset+'/'+topologyName)

