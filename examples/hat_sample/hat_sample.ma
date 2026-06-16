//Maya ASCII 2026 scene
//Name: hat_sample.ma
//Codeset: 1252
//
// STRUCTURAL REFERENCE — hat asset, authored to the Clothing Asset Authoring Spec.
// Teaches the required hierarchy + naming + cloth_info ONLY. Geometry is a placeholder
// box and the cloth_* joints carry placeholder positions/orient — see hat_sample/README.md.
//
requires maya "2026";
requires "stereoCamera" "10.0";
requires "mtoa" "5.5.4.2";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2026";
fileInfo "version" "2026";
createNode transform -s -n "persp";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 80 170 120 ;
	setAttr ".r" -type "double3" -15 33 0 ;
createNode camera -s -n "perspShape" -p "persp";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 200;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "cloth_hat_sample";
createNode transform -n "Mesh_GRP" -p "cloth_hat_sample";
createNode transform -n "cloth_hat_mesh" -p "Mesh_GRP";
	setAttr ".t" -type "double3" 0 165 0 ;
createNode mesh -n "cloth_hat_meshShape" -p "cloth_hat_mesh";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.33000001 0 0.66333336 0
		 0.33000001 0.25 0.66333336 0.25 0.33000001 0.5 0.66333336 0.5 0.33000001 0.75
		 0.66333336 0.75 0.33000001 1 0.66333336 1 1 0 1 0.25 0 0 0 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 8 ".vt[0:7]"  -14 -5 12 14 -5 12 -14 5 12 14 5 12 -14 5 -12
		 14 5 -12 -14 -5 -12 14 -5 -12;
	setAttr -s 12 ".ed[0:11]"  0 1 0 2 3 0 4 5 0 6 7 0 0 2 0 1 3 0 2 4 0
		 3 5 0 4 6 0 5 7 0 6 0 0 7 1 0;
	setAttr -s 6 -ch 24 ".fc[0:5]" -type "polyFaces"
		f 4 0 5 -2 -5
		mu 0 4 0 1 3 2
		f 4 1 7 -3 -7
		mu 0 4 2 3 5 4
		f 4 2 9 -4 -9
		mu 0 4 4 5 7 6
		f 4 3 11 -1 -11
		mu 0 4 6 7 9 8
		f 4 -12 -10 -8 -6
		mu 0 4 1 10 11 3
		f 4 10 4 6 8
		mu 0 4 12 0 2 13;
	setAttr ".cd" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".cvd" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pd[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".hfd" -type "dataPolyComponent" Index_Data Face 0 ;
createNode transform -n "Rig_GRP" -p "cloth_hat_sample";
createNode joint -n "cloth_root" -p "Rig_GRP";
	setAttr ".t" -type "double3" 0 0 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_pelvis" -p "cloth_root";
	setAttr ".t" -type "double3" 0 98 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_spine_01" -p "cloth_pelvis";
	setAttr ".t" -type "double3" 0 10 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_spine_02" -p "cloth_spine_01";
	setAttr ".t" -type "double3" 0 9 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_spine_03" -p "cloth_spine_02";
	setAttr ".t" -type "double3" 0 9 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_spine_04" -p "cloth_spine_03";
	setAttr ".t" -type "double3" 0 9 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_spine_05" -p "cloth_spine_04";
	setAttr ".t" -type "double3" 0 9 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_neck_01" -p "cloth_spine_05";
	setAttr ".t" -type "double3" 0 9 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_neck_02" -p "cloth_neck_01";
	setAttr ".t" -type "double3" 0 5 0 ;
	setAttr ".radi" 4;
createNode joint -n "cloth_head" -p "cloth_neck_02";
	setAttr ".t" -type "double3" 0 5 0 ;
	setAttr ".radi" 4;
createNode transform -n "Ctrl_GRP" -p "cloth_hat_sample";
createNode transform -n "cloth_fit_ctrl" -p "Ctrl_GRP";
	setAttr ".t" -type "double3" 0 185 0 ;
	addAttr -ci true -k true -sn "fit_tightness" -ln "fit_tightness" -min -1 -max 1 -at "double";
	addAttr -ci true -k true -sn "fit_height" -ln "fit_height" -min -1 -max 1 -at "double";
	addAttr -ci true -k true -sn "fit_brim_width" -ln "fit_brim_width" -min -1 -max 1 -at "double";
	addAttr -ci true -k true -sn "fit_tilt" -ln "fit_tilt" -min -1 -max 1 -at "double";
	setAttr -k on ".fit_tightness";
	setAttr -k on ".fit_height";
	setAttr -k on ".fit_brim_width";
	setAttr -k on ".fit_tilt";
createNode lightLinker -s -n "lightLinker1";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
createNode displayLayerManager -n "layerManager";
createNode displayLayer -n "defaultLayer";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
createNode renderLayer -n "defaultRenderLayer";
	setAttr ".g" yes;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :defaultShaderList1;
	setAttr -s 4 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
	setAttr -s 1 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr ".ren" -type "string" "arnold";
select -ne :defaultResolution;
	setAttr ".pa" 1;
createNode network -n "cloth_info";
	addAttr -ci true -sn "assetName" -ln "assetName" -dt "string";
	addAttr -ci true -sn "assetType" -ln "assetType" -dt "string";
	addAttr -ci true -sn "clothVersion" -ln "clothVersion" -dt "string";
	addAttr -ci true -sn "genHumanCompat" -ln "genHumanCompat" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "notes" -ln "notes" -dt "string";
	setAttr ".assetName" -type "string" "hat_sample";
	setAttr ".assetType" -type "string" "hat";
	setAttr ".clothVersion" -type "string" "1.0.0";
	setAttr ".genHumanCompat" -type "string" "v03";
	setAttr ".author" -type "string" "Snap-On Clothing (structural sample)";
	setAttr ".notes" -type "string" "Structural reference for a hat asset: correct hierarchy, cloth_ naming, and cloth_info. Placeholder geometry/skeleton — replace with a real mesh skinned to a rig-duplicated cloth_ skeleton.";
connectAttr "cloth_root.s" "cloth_pelvis.is";
connectAttr "cloth_pelvis.s" "cloth_spine_01.is";
connectAttr "cloth_spine_01.s" "cloth_spine_02.is";
connectAttr "cloth_spine_02.s" "cloth_spine_03.is";
connectAttr "cloth_spine_03.s" "cloth_spine_04.is";
connectAttr "cloth_spine_04.s" "cloth_spine_05.is";
connectAttr "cloth_spine_05.s" "cloth_neck_01.is";
connectAttr "cloth_neck_01.s" "cloth_neck_02.is";
connectAttr "cloth_neck_02.s" "cloth_head.is";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "cloth_hat_meshShape.iog" ":initialShadingGroup.dsm" -na;
// End of hat_sample.ma
