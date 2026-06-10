//Maya ASCII 2026 scene
//Name: sample_coat.ma
requires maya "2026";
createNode transform -n "cloth_sample_coat";
createNode transform -n "Mesh_GRP" -p "cloth_sample_coat";
createNode transform -n "Rig_GRP" -p "cloth_sample_coat";
createNode transform -n "Ctrl_GRP" -p "cloth_sample_coat";
createNode joint -n "cloth_root" -p "Rig_GRP";
createNode joint -n "cloth_pelvis" -p "cloth_root";
createNode joint -n "cloth_spine_01" -p "cloth_pelvis";
createNode joint -n "cloth_spine_02" -p "cloth_spine_01";
createNode transform -n "cloth_fit_ctrl" -p "Ctrl_GRP";
	addAttr -ci true -k true -sn "fit_tightness" -ln "fit_tightness" -min -1 -max 1 -at "double";
	addAttr -ci true -k true -sn "fit_thickness" -ln "fit_thickness" -min 0 -max 1 -at "double";
createNode mesh -n "cloth_jacket_meshShape" -p "Mesh_GRP";
createNode network -n "cloth_info";
	addAttr -ci true -sn "assetName" -ln "assetName" -dt "string";
	addAttr -ci true -sn "assetType" -ln "assetType" -dt "string";
	addAttr -ci true -sn "clothVersion" -ln "clothVersion" -dt "string";
	addAttr -ci true -sn "genHumanCompat" -ln "genHumanCompat" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
setAttr ".assetName" -type "string" "sample_coat_A";
setAttr ".assetType" -type "string" "coat";
setAttr ".clothVersion" -type "string" "1.0.0";
setAttr ".genHumanCompat" -type "string" "v03, v04";
setAttr ".author" -type "string" "Test \"Q\" Author";
// End of sample_coat.ma
