//Maya ASCII 2026 scene
//Name: trench_coat_A.ma
//Last modified: Wed, Jun 10, 2026 11:19:51 AM
//Codeset: 1252
requires maya "2026";
requires "stereoCamera" "10.0";
requires "mtoa" "5.5.4.2";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2026";
fileInfo "version" "2026";
fileInfo "cutIdentifier" "202510291147-60ec9eda33";
fileInfo "osv" "Windows 11 Pro v2009 (Build: 26200)";
fileInfo "UUID" "0997DF9B-4CD9-1B1C-6CFC-868B6E4A0C6C";
createNode transform -s -n "persp";
	rename -uid "27C588F9-448C-1D5A-D437-899507B78498";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 28 21 28 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "8DAF8BD2-4FB4-BA95-CFD4-F2B271B10556";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 44.82186966202994;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "01ADD3C8-4EF9-0AF9-405C-88A74B4BE5E2";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "155A2EEF-4A65-9461-912D-50B728635323";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "front";
	rename -uid "AC557238-4D83-DB2F-036C-39954343D66F";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "80E8B9BA-4F0F-A080-3E3B-A49E7576B5EC";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -s -n "side";
	rename -uid "0BCD15ED-45D6-EB40-0475-07948FAE4DF6";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "C7240BA5-4D05-D404-7E63-8596985FDC6A";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1000.1;
	setAttr ".ow" 30;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
	setAttr ".ai_translator" -type "string" "orthographic";
createNode transform -n "cloth_trench_coat_A";
	rename -uid "3881B8C7-44F1-3AF2-BD67-22AF55553645";
	setAttr ".rp" -type "double3" 0 77.432999999999993 0 ;
	setAttr ".sp" -type "double3" 0 77.432999999999993 0 ;
createNode transform -n "Mesh_GRP" -p "cloth_trench_coat_A";
	rename -uid "EA307EFD-4344-1F47-EA46-89BDBEF9F5CE";
createNode transform -n "cloth_jacket_mesh" -p "Mesh_GRP";
	rename -uid "BF99D9C6-490A-004E-A151-FD91120206F7";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 0 94 0 ;
	setAttr ".sp" -type "double3" 0 94 0 ;
createNode mesh -n "cloth_jacket_meshShape" -p "cloth_jacket_mesh";
	rename -uid "2A099F8B-4581-BA91-CD1A-1FA42A52D09E";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vcs" 2;
createNode mesh -n "cloth_jacket_meshShapeOrig" -p "cloth_jacket_mesh";
	rename -uid "9797DCEE-4AD9-41F1-9DC4-5B9966250FA0";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr -s 6 ".gtag";
	setAttr ".gtag[0].gtagnm" -type "string" "back";
	setAttr ".gtag[0].gtagcmp" -type "componentList" 1 "f[2]";
	setAttr ".gtag[1].gtagnm" -type "string" "bottom";
	setAttr ".gtag[1].gtagcmp" -type "componentList" 1 "f[3]";
	setAttr ".gtag[2].gtagnm" -type "string" "front";
	setAttr ".gtag[2].gtagcmp" -type "componentList" 1 "f[0]";
	setAttr ".gtag[3].gtagnm" -type "string" "left";
	setAttr ".gtag[3].gtagcmp" -type "componentList" 1 "f[5]";
	setAttr ".gtag[4].gtagnm" -type "string" "right";
	setAttr ".gtag[4].gtagcmp" -type "componentList" 1 "f[4]";
	setAttr ".gtag[5].gtagnm" -type "string" "top";
	setAttr ".gtag[5].gtagcmp" -type "componentList" 1 "f[1]";
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.33000001 0 0.66333336
		 0 0.33000001 0.25 0.66333336 0.25 0.33000001 0.5 0.66333336 0.5 0.33000001 0.75 0.66333336
		 0.75 0.33000001 1 0.66333336 1 1 0 1 0.25 0 0 0 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 8 ".pt[0:7]" -type "float3"  0 94 0 0 94 0 0 94 0 0 94 
		0 0 94 0 0 94 0 0 94 0 0 94 0;
	setAttr -s 8 ".vt[0:7]"  -26 -46 16 26 -46 16 -26 46 16 26 46 16 -26 46 -16
		 26 46 -16 -26 -46 -16 26 -46 -16;
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
createNode transform -n "cloth_collar_mesh" -p "Mesh_GRP";
	rename -uid "21620F29-4B1B-DD74-8AA5-C1A6AA784D54";
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
	setAttr ".rp" -type "double3" 0 146 -1 ;
	setAttr ".sp" -type "double3" 0 146 -1 ;
createNode mesh -n "cloth_collar_meshShape" -p "cloth_collar_mesh";
	rename -uid "F2D511CC-44EE-D94D-EC0D-3BBBAC4E959B";
	setAttr -k off ".v";
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr ".vcs" 2;
createNode mesh -n "cloth_collar_meshShapeOrig" -p "cloth_collar_mesh";
	rename -uid "135A7071-42BA-7CD0-EB42-3689552579C8";
	setAttr -k off ".v";
	setAttr ".io" yes;
	setAttr ".vir" yes;
	setAttr ".vif" yes;
	setAttr -s 6 ".gtag";
	setAttr ".gtag[0].gtagnm" -type "string" "back";
	setAttr ".gtag[0].gtagcmp" -type "componentList" 1 "f[2]";
	setAttr ".gtag[1].gtagnm" -type "string" "bottom";
	setAttr ".gtag[1].gtagcmp" -type "componentList" 1 "f[3]";
	setAttr ".gtag[2].gtagnm" -type "string" "front";
	setAttr ".gtag[2].gtagcmp" -type "componentList" 1 "f[0]";
	setAttr ".gtag[3].gtagnm" -type "string" "left";
	setAttr ".gtag[3].gtagcmp" -type "componentList" 1 "f[5]";
	setAttr ".gtag[4].gtagnm" -type "string" "right";
	setAttr ".gtag[4].gtagcmp" -type "componentList" 1 "f[4]";
	setAttr ".gtag[5].gtagnm" -type "string" "top";
	setAttr ".gtag[5].gtagcmp" -type "componentList" 1 "f[1]";
	setAttr ".uvst[0].uvsn" -type "string" "map1";
	setAttr -s 14 ".uvst[0].uvsp[0:13]" -type "float2" 0.33000001 0 0.66333336
		 0 0.33000001 0.25 0.66333336 0.25 0.33000001 0.5 0.66333336 0.5 0.33000001 0.75 0.66333336
		 0.75 0.33000001 1 0.66333336 1 1 0 1 0.25 0 0 0 0.25;
	setAttr ".cuvs" -type "string" "map1";
	setAttr ".dcc" -type "string" "Ambient+Diffuse";
	setAttr ".covm[0]"  0 1 1;
	setAttr ".cdvm[0]"  0 1 1;
	setAttr -s 8 ".pt[0:7]" -type "float3"  0 146 -1 0 146 -1 0 146 -1 
		0 146 -1 0 146 -1 0 146 -1 0 146 -1 0 146 -1;
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
createNode transform -n "Rig_GRP" -p "cloth_trench_coat_A";
	rename -uid "CA46C3D5-4264-A154-7768-3BA8FC432E58";
createNode joint -n "cloth_root" -p "Rig_GRP";
	rename -uid "C5AD7CE7-4DB7-B934-5156-6C9895200FC0";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
createNode joint -n "cloth_pelvis" -p "cloth_root";
	rename -uid "256E8B8B-4638-0669-2D3B-51B5B41C6C49";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 97 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 97 0 1;
createNode joint -n "cloth_spine_01" -p "cloth_pelvis";
	rename -uid "6830EF5D-495D-D4E8-5582-B0AB6CCBB6E0";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 5 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 102 0 1;
createNode joint -n "cloth_spine_02" -p "cloth_spine_01";
	rename -uid "6F9D9BDA-47C6-9660-65C5-62827E2F2F63";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 6 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 108 0 1;
createNode joint -n "cloth_spine_03" -p "cloth_spine_02";
	rename -uid "73746D26-4A15-3C36-20B9-0A8621530B00";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 6 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 114 0 1;
createNode joint -n "cloth_spine_04" -p "cloth_spine_03";
	rename -uid "EE29BBB9-4504-E1D5-26AC-9D999B9A2502";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 6 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 120 0 1;
createNode joint -n "cloth_spine_05" -p "cloth_spine_04";
	rename -uid "9435FFF9-4CFF-5BEE-6804-CFA1B250B7CC";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 6 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 126 0 1;
createNode joint -n "cloth_neck_01" -p "cloth_spine_05";
	rename -uid "DA0CDAA9-43A6-6B86-B86B-978BF149F87E";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 24 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 150 0 1;
createNode joint -n "cloth_neck_02" -p "cloth_neck_01";
	rename -uid "85FDA4F0-4D45-F4BE-2D19-B1890F685832";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 4 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 154 0 1;
createNode joint -n "cloth_clavicle_l" -p "cloth_spine_05";
	rename -uid "83D103C0-4523-DD35-1DEC-5CB28FAF4420";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 3 18 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 3 144 0 1;
createNode joint -n "cloth_upperarm_l" -p "cloth_clavicle_l";
	rename -uid "698354C9-4B02-8584-6CAF-B8A8FDFA9ECD";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 15 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 18 144 0 1;
createNode joint -n "cloth_lowerarm_l" -p "cloth_upperarm_l";
	rename -uid "EC395F99-457A-711A-DF34-A4B185FB005D";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 27 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 45 144 0 1;
createNode joint -n "cloth_hand_l" -p "cloth_lowerarm_l";
	rename -uid "1727E1FA-4A2E-0D66-BBA8-249423C43FD2";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 25.999999999999986 -2.8421709430404007e-14 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 70.999999999999986 143.99999999999997 0 1;
createNode joint -n "cloth_clavicle_r" -p "cloth_spine_05";
	rename -uid "AB985F22-4141-DEE8-4A52-C5A5D79D48EB";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3 18 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -3 144 0 1;
createNode joint -n "cloth_upperarm_r" -p "cloth_clavicle_r";
	rename -uid "DF6AD0EF-4DDF-03C2-E6EE-5887B25D3262";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -15 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -18 144 0 1;
createNode joint -n "cloth_lowerarm_r" -p "cloth_upperarm_r";
	rename -uid "A7627EDB-4575-1577-A6DC-41A9D2CA737C";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -27 0 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -45 144 0 1;
createNode joint -n "cloth_hand_r" -p "cloth_lowerarm_r";
	rename -uid "48565599-40FE-A63F-28FF-D0A3EC6DEAEC";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -25.999999999999986 -2.8421709430404007e-14 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -70.999999999999986 143.99999999999997 0 1;
createNode joint -n "cloth_coatTail_01" -p "cloth_spine_01";
	rename -uid "810A66DB-4A88-53BD-9134-158A124CD92C";
	setAttr ".t" -type "double3" 0 -8 -10 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode joint -n "cloth_coatTail_02" -p "cloth_coatTail_01";
	rename -uid "6DC1F951-4AB3-3550-78A1-4E95887ABD0A";
	setAttr ".t" -type "double3" 0 -30 -2 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode joint -n "cloth_thigh_l" -p "cloth_pelvis";
	rename -uid "19C8A2B0-48B0-6F5D-7F02-84AB26F02BAB";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 9 -2 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 9 95 0 1;
createNode joint -n "cloth_calf_l" -p "cloth_thigh_l";
	rename -uid "A17A823E-46F3-75FB-6A44-DBBAD5B3C16D";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 -42 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 9 53 0 1;
createNode joint -n "cloth_foot_l" -p "cloth_calf_l";
	rename -uid "060F678C-4598-32B7-2F90-BFBF6D00F58C";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 -41.999999999999993 2 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 9 11.000000000000007 2 1;
createNode joint -n "cloth_ball_l" -p "cloth_foot_l";
	rename -uid "0D4C5EEE-486D-0B9E-BF93-30A337CC3DDB";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -1.7763568394002505e-15 -8.0000000000000089 10 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 8.9999999999999982 2.9999999999999982 12 1;
createNode joint -n "cloth_thigh_r" -p "cloth_pelvis";
	rename -uid "02186AB2-4ECB-0B0B-F6AE-69A5BDD847C5";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -9 -2 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -9 95 0 1;
createNode joint -n "cloth_calf_r" -p "cloth_thigh_r";
	rename -uid "571E7C21-40F3-F8E2-B3BE-7D8FC923C65D";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 -42 0 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -9 53 0 1;
createNode joint -n "cloth_foot_r" -p "cloth_calf_r";
	rename -uid "1E201851-4275-6CE2-BC39-CB981C5750C8";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 0 -41.999999999999993 2 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -9 11.000000000000007 2 1;
createNode joint -n "cloth_ball_r" -p "cloth_foot_r";
	rename -uid "B61A650C-4358-BE24-DBF1-A3946B48C949";
	addAttr -ci true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 1.7763568394002505e-15 -8.0000000000000089 10 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 -8.9999999999999982 2.9999999999999982 12 1;
createNode transform -n "Ctrl_GRP" -p "cloth_trench_coat_A";
	rename -uid "02FACE2E-4177-1906-8506-B2AEC5A009D0";
createNode transform -n "cloth_fit_ctrl" -p "Ctrl_GRP";
	rename -uid "6622D854-48C3-49E7-5656-59915F739E70";
	addAttr -ci true -k true -sn "fit_tightness" -ln "fit_tightness" -min -1 -max 1 
		-at "double";
	addAttr -ci true -k true -sn "fit_thickness" -ln "fit_thickness" -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "fit_length" -ln "fit_length" -min -1 -max 1 -at "double";
	addAttr -ci true -k true -sn "fit_hem_length" -ln "fit_hem_length" -min -1 -max 
		1 -at "double";
	addAttr -ci true -k true -sn "fit_collar_tightness" -ln "fit_collar_tightness" -min 
		-1 -max 1 -at "double";
	setAttr -k on ".fit_tightness";
	setAttr -k on ".fit_length";
createNode transform -n "cloth_coatTail_ctrl" -p "Ctrl_GRP";
	rename -uid "FC9A5DB2-4FE9-523C-9B45-DB8EF5BCBAF8";
	addAttr -ci true -k true -sn "swing" -ln "swing" -min -10 -max 10 -at "double";
createNode transform -n "cloth_fit_ffdLattice" -p "Ctrl_GRP";
	rename -uid "EFF9B448-47CB-C445-D766-898D9243C724";
	setAttr ".t" -type "double3" 0 99.5 0 ;
createNode lattice -n "cloth_fit_ffdLatticeShape" -p "cloth_fit_ffdLattice";
	rename -uid "ADABC5E3-4F1D-B806-0F2A-92A40EFC65FA";
	setAttr -k off ".v";
	setAttr ".td" 6;
	setAttr ".cc" -type "lattice" 2 6 2 24 -0.5 -0.5 -0.5 0.5 -0.5
		 -0.5 -0.5 -0.29999999999999999 -0.5 0.5 -0.29999999999999999 -0.5 -0.5 -0.099999999999999978
		 -0.5 0.5 -0.099999999999999978 -0.5 -0.5 0.10000000000000003 -0.5 0.5 0.10000000000000003
		 -0.5 -0.5 0.30000000000000004 -0.5 0.5 0.30000000000000004 -0.5 -0.5 0.5 -0.5 0.5
		 0.5 -0.5 -0.5 -0.5 0.5 0.5 -0.5 0.5 -0.5 -0.29999999999999999 0.5 0.5 -0.29999999999999999
		 0.5 -0.5 -0.099999999999999978 0.5 0.5 -0.099999999999999978 0.5 -0.5 0.10000000000000003
		 0.5 0.5 0.10000000000000003 0.5 -0.5 0.30000000000000004 0.5 0.5 0.30000000000000004
		 0.5 -0.5 0.5 0.5 0.5 0.5 0.5 ;
createNode transform -n "cloth_fit_ffdBase" -p "Ctrl_GRP";
	rename -uid "8914381E-411A-F418-8C9B-8C825C94AD61";
	setAttr ".t" -type "double3" 0 99.5 0 ;
	setAttr ".s" -type "double3" 52 103 32 ;
createNode baseLattice -n "cloth_fit_ffdBaseShape" -p "cloth_fit_ffdBase";
	rename -uid "5761DC58-4DBA-388E-7C22-58AA6006E776";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "B97FBDD3-44C4-A5C1-D8D2-F1ABC8A475D4";
	setAttr -s 2 ".lnk";
	setAttr -s 2 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "2544F360-43A8-D482-17C1-F6A923328D49";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "87AFB1B7-4F5D-91DA-7D57-2F97D77BF147";
createNode displayLayerManager -n "layerManager";
	rename -uid "B50EDBCC-4A7C-6FC6-DD3E-4ABE55DD7BE6";
createNode displayLayer -n "defaultLayer";
	rename -uid "D171B950-4416-32A6-B8EC-1E90681B96A2";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "76692A9F-4C33-44BD-A8EB-F191212C249E";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "4C70AB9B-4159-89D0-6623-77AAF7AEAA97";
	setAttr ".g" yes;
createNode skinCluster -n "cloth_jacket_mesh_skinCluster";
	rename -uid "6CC574F3-49D2-D16B-A2D0-20B3B2208B08";
	setAttr -s 8 ".wl";
	setAttr ".wl[0:7].w"
		2 21 0.47010070804297677 22 0.52989929195702334
		2 17 0.47010070804297677 18 0.52989929195702334
		2 13 0.39589041095890409 14 0.60410958904109591
		2 9 0.39589041095890409 10 0.60410958904109591
		2 13 0.39589041095890409 14 0.60410958904109591
		2 9 0.39589041095890409 10 0.60410958904109591
		2 21 0.484032994534905 22 0.51596700546509511
		2 17 0.484032994534905 18 0.51596700546509511;
	setAttr -s 25 ".pm";
	setAttr ".pm[0]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 0 -0 1;
	setAttr ".pm[1]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -97 -0 1;
	setAttr ".pm[2]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -102 -0 1;
	setAttr ".pm[3]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -108 -0 1;
	setAttr ".pm[4]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -114 -0 1;
	setAttr ".pm[5]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -120 -0 1;
	setAttr ".pm[6]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -126 -0 1;
	setAttr ".pm[7]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -150 -0 1;
	setAttr ".pm[8]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -154 -0 1;
	setAttr ".pm[9]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -3 -144 -0 1;
	setAttr ".pm[10]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -18 -144 -0 1;
	setAttr ".pm[11]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -45 -144 -0 1;
	setAttr ".pm[12]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -70.999999999999986 -143.99999999999997 -0 1;
	setAttr ".pm[13]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 3 -144 -0 1;
	setAttr ".pm[14]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 18 -144 -0 1;
	setAttr ".pm[15]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 45 -144 -0 1;
	setAttr ".pm[16]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 70.999999999999986 -143.99999999999997 -0 1;
	setAttr ".pm[17]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -9 -95 -0 1;
	setAttr ".pm[18]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -9 -53 -0 1;
	setAttr ".pm[19]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -9 -11.000000000000007 -2 1;
	setAttr ".pm[20]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -8.9999999999999982 -2.9999999999999982 -12 1;
	setAttr ".pm[21]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 9 -95 -0 1;
	setAttr ".pm[22]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 9 -53 -0 1;
	setAttr ".pm[23]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 9 -11.000000000000007 -2 1;
	setAttr ".pm[24]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 8.9999999999999982 -2.9999999999999982 -12 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr -s 25 ".ma";
	setAttr -s 25 ".dpf[0:24]"  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 
		4 4 4 4 4;
	setAttr -s 25 ".lw";
	setAttr -s 25 ".lw";
	setAttr ".ucm" yes;
	setAttr -s 25 ".ifcl";
	setAttr -s 25 ".ifcl";
createNode dagPose -n "bindPose1";
	rename -uid "29A167A8-4AF0-49B4-3555-1383C049346E";
	setAttr -s 25 ".wm";
	setAttr -s 25 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 97 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 5 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[3]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[4]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[5]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[6]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 6 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[7]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 24 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[8]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 4 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[9]" -type "matrix" "xform" 1 1 1 0 0 0 0 3 18 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[10]" -type "matrix" "xform" 1 1 1 0 0 0 0 15 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[11]" -type "matrix" "xform" 1 1 1 0 0 0 0 27 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[12]" -type "matrix" "xform" 1 1 1 0 0 0 0 25.999999999999972 -5.6843418860808015e-14
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[13]" -type "matrix" "xform" 1 1 1 0 0 0 0 -3 18 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[14]" -type "matrix" "xform" 1 1 1 0 0 0 0 -15 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[15]" -type "matrix" "xform" 1 1 1 0 0 0 0 -27 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[16]" -type "matrix" "xform" 1 1 1 0 0 0 0 -25.999999999999972 -5.6843418860808015e-14
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[17]" -type "matrix" "xform" 1 1 1 0 0 0 0 9 -2 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 -42 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[19]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 -41.999999999999986
		 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[20]" -type "matrix" "xform" 1 1 1 0 0 0 0 -3.5527136788005009e-15
		 -8.0000000000000107 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[21]" -type "matrix" "xform" 1 1 1 0 0 0 0 -9 -2 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[22]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 -42 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[23]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 -41.999999999999986
		 2 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[24]" -type "matrix" "xform" 1 1 1 0 0 0 0 3.5527136788005009e-15
		 -8.0000000000000107 10 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr -s 25 ".m";
	setAttr -s 25 ".p";
	setAttr ".bp" yes;
createNode skinCluster -n "cloth_collar_mesh_skinCluster";
	rename -uid "08E23B63-4083-50F1-7E05-0984285FDA07";
	setAttr -s 8 ".wl";
	setAttr ".wl[0:7].w"
		2 13 0.55777684739376177 14 0.44222315260623823
		2 9 0.55777684739376177 10 0.44222315260623823
		2 13 0.54485321910041573 14 0.45514678089958438
		2 9 0.54485321910041573 10 0.45514678089958438
		2 13 0.53535393038717261 14 0.46464606961282739
		2 9 0.53535393038717261 10 0.46464606961282739
		2 13 0.54293133294864393 14 0.45706866705135607
		2 9 0.54293133294864393 10 0.45706866705135607;
	setAttr -s 25 ".pm";
	setAttr ".pm[0]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 0 -0 1;
	setAttr ".pm[1]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -97 -0 1;
	setAttr ".pm[2]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -102 -0 1;
	setAttr ".pm[3]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -108 -0 1;
	setAttr ".pm[4]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -114 -0 1;
	setAttr ".pm[5]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -120 -0 1;
	setAttr ".pm[6]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -126 -0 1;
	setAttr ".pm[7]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -150 -0 1;
	setAttr ".pm[8]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 -154 -0 1;
	setAttr ".pm[9]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -3 -144 -0 1;
	setAttr ".pm[10]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -18 -144 -0 1;
	setAttr ".pm[11]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -45 -144 -0 1;
	setAttr ".pm[12]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -70.999999999999986 -143.99999999999997 -0 1;
	setAttr ".pm[13]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 3 -144 -0 1;
	setAttr ".pm[14]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 18 -144 -0 1;
	setAttr ".pm[15]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 45 -144 -0 1;
	setAttr ".pm[16]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 70.999999999999986 -143.99999999999997 -0 1;
	setAttr ".pm[17]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -9 -95 -0 1;
	setAttr ".pm[18]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -9 -53 -0 1;
	setAttr ".pm[19]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -9 -11.000000000000007 -2 1;
	setAttr ".pm[20]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -8.9999999999999982 -2.9999999999999982 -12 1;
	setAttr ".pm[21]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 9 -95 -0 1;
	setAttr ".pm[22]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 9 -53 -0 1;
	setAttr ".pm[23]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 9 -11.000000000000007 -2 1;
	setAttr ".pm[24]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 8.9999999999999982 -2.9999999999999982 -12 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr -s 25 ".ma";
	setAttr -s 25 ".dpf[0:24]"  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 
		4 4 4 4 4;
	setAttr -s 25 ".lw";
	setAttr -s 25 ".lw";
	setAttr ".ucm" yes;
	setAttr -s 25 ".ifcl";
	setAttr -s 25 ".ifcl";
createNode ffd -n "cloth_fit_ffd";
	rename -uid "F28B3EB9-4C95-8C1B-BCFE-79A35BA295F1";
	setAttr -s 2 ".ip";
	setAttr -s 2 ".og";
	setAttr -s 2 ".orggeom";
createNode animCurveUU -n "cloth_fit_ffdLattice_scaleX";
	rename -uid "DB77BE3F-47A9-F16F-F15A-C9A641CB2A09";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -1 56.160000000000004 0 52 1 47.84;
createNode animCurveUU -n "cloth_fit_ffdLattice_scaleZ";
	rename -uid "0DD77B00-4D91-EDD9-9FB1-4396866FC322";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -1 34.56 0 32 1 29.44;
createNode animCurveUU -n "cloth_fit_ffdLattice_scaleY";
	rename -uid "16DA5499-4C6F-945E-EB67-2381C95A59FC";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -1 92.7 0 103 1 113.30000000000001;
createNode network -n "cloth_info";
	rename -uid "66D08118-46EB-B066-24FF-D482BC733FDD";
	addAttr -ci true -sn "assetName" -ln "assetName" -dt "string";
	addAttr -ci true -sn "assetType" -ln "assetType" -dt "string";
	addAttr -ci true -sn "clothVersion" -ln "clothVersion" -dt "string";
	addAttr -ci true -sn "genHumanCompat" -ln "genHumanCompat" -dt "string";
	addAttr -ci true -sn "author" -ln "author" -dt "string";
	addAttr -ci true -sn "notes" -ln "notes" -dt "string";
	setAttr ".assetName" -type "string" "trench_coat_A";
	setAttr ".assetType" -type "string" "coat";
	setAttr ".clothVersion" -type "string" "1.0.0";
	setAttr ".genHumanCompat" -type "string" "v03";
	setAttr ".author" -type "string" "Snap-On Clothing (example)";
	setAttr ".notes" -type "string" "Generated by examples/build_example_asset.py — skinned + fit lattice.";
createNode script -n "uiConfigurationScriptNode";
	rename -uid "67A63195-48DA-B608-45A2-E2912F2877FC";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"|top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n"
		+ "            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -excludeObjectPreset \"All\" \n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"|side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n"
		+ "            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n"
		+ "            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -excludeObjectPreset \"All\" \n"
		+ "            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"|front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n"
		+ "            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n"
		+ "            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n"
		+ "            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -excludeObjectPreset \"All\" \n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n"
		+ "            -camera \"|persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n"
		+ "            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n"
		+ "            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -excludeObjectPreset \"All\" \n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1551\n            -height 804\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n"
		+ "            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -showUfeItems 1\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n"
		+ "            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n"
		+ "            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -showUfeItems 1\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n"
		+ "            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -ufeFilter \"USD\" \"InactivePrims\" -ufeFilterValue 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n"
		+ "            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n"
		+ "                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -showUfeItems 1\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n"
		+ "                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayValues 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -showPlayRangeShades \"on\" \n                -lockPlayRangeShades \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -tangentScale 1\n                -tangentLineThickness 1\n                -keyMinScale 1\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -preSelectionHighlight 0\n                -limitToSelectedCurves 0\n                -constrainDrag 0\n                -valueLinesToggle 0\n                -outliner \"graphEditor1OutlineEd\" \n                -highlightAffectedCurves 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n"
		+ "\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n"
		+ "                -showParentContainers 0\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 1\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -showUfeItems 1\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n"
		+ "                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -hierarchyBelow 0\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayValues 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n"
		+ "                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n"
		+ "                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -connectedGraphingMode 1\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -showUnitConversions 0\n                -editorMode \"default\" \n"
		+ "                -hasWatchpoint 0\n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -connectionStyle \"bezier\" \n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -connectedGraphingMode 1\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n"
		+ "                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -showUnitConversions 0\n                -editorMode \"default\" \n                -hasWatchpoint 0\n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n"
		+ "\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"motionMakerEditorPanel\" (localizedPanelLabel(\"MotionMaker Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"MotionMaker Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\n{ string $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"|persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"smoothShaded\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 0\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n"
		+ "                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n"
		+ "                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -controllers 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n"
		+ "                -clipGhosts 1\n                -bluePencil 1\n                -greasePencils 0\n                -excludeObjectPreset \"All\" \n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n            stereoCameraView -e \n                -pluginObjects \"gpuCacheDisplayFilter\" 1 \n                $editorName; };\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n"
		+ "\t\t\t\t-removeAllPanels\n\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -bluePencil 1\\n    -greasePencils 0\\n    -excludeObjectPreset \\\"All\\\" \\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1551\\n    -height 804\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -bluePencil 1\\n    -greasePencils 0\\n    -excludeObjectPreset \\\"All\\\" \\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1551\\n    -height 804\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "42853BF4-48C9-DED7-03B6-FCB2913A7D7D";
	setAttr ".b" -type "string" "playbackOptions -min 0 -max 165 -ast 0 -aet 165 ";
	setAttr ".st" 6;
select -ne :time1;
	setAttr ".o" 0;
select -ne :hardwareRenderingGlobals;
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
	setAttr ".fprt" yes;
	setAttr ".rtfm" 1;
select -ne :renderPartition;
	setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
	setAttr -s 6 ".s";
select -ne :postProcessList1;
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :standardSurface1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :openPBR_shader1;
	setAttr ".bc" -type "float3" 0.40000001 0.40000001 0.40000001 ;
	setAttr ".sr" 0.5;
select -ne :initialShadingGroup;
	setAttr -s 2 ".dsm";
	setAttr ".ro" yes;
select -ne :initialParticleSE;
	setAttr ".ro" yes;
select -ne :defaultRenderGlobals;
	addAttr -ci true -h true -sn "dss" -ln "defaultSurfaceShader" -dt "string";
	setAttr ".ren" -type "string" "arnold";
	setAttr ".dss" -type "string" "openPBR_shader1";
select -ne :defaultResolution;
	setAttr ".pa" 1;
select -ne :defaultColorMgtGlobals;
	setAttr ".cfe" yes;
	setAttr ".cfp" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".vtn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".vn" -type "string" "ACES 1.0 SDR-video";
	setAttr ".dn" -type "string" "sRGB";
	setAttr ".wsn" -type "string" "ACEScg";
	setAttr ".otn" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".potn" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -ne :hardwareRenderGlobals;
	setAttr ".ctrs" 256;
	setAttr ".btrs" 512;
connectAttr "cloth_fit_ffd.og[0]" "cloth_jacket_meshShape.i";
connectAttr "cloth_fit_ffd.og[1]" "cloth_collar_meshShape.i";
connectAttr "cloth_root.s" "cloth_pelvis.is";
connectAttr "cloth_pelvis.s" "cloth_spine_01.is";
connectAttr "cloth_spine_01.s" "cloth_spine_02.is";
connectAttr "cloth_spine_02.s" "cloth_spine_03.is";
connectAttr "cloth_spine_03.s" "cloth_spine_04.is";
connectAttr "cloth_spine_04.s" "cloth_spine_05.is";
connectAttr "cloth_spine_05.s" "cloth_neck_01.is";
connectAttr "cloth_neck_01.s" "cloth_neck_02.is";
connectAttr "cloth_spine_05.s" "cloth_clavicle_l.is";
connectAttr "cloth_clavicle_l.s" "cloth_upperarm_l.is";
connectAttr "cloth_upperarm_l.s" "cloth_lowerarm_l.is";
connectAttr "cloth_lowerarm_l.s" "cloth_hand_l.is";
connectAttr "cloth_spine_05.s" "cloth_clavicle_r.is";
connectAttr "cloth_clavicle_r.s" "cloth_upperarm_r.is";
connectAttr "cloth_upperarm_r.s" "cloth_lowerarm_r.is";
connectAttr "cloth_lowerarm_r.s" "cloth_hand_r.is";
connectAttr "cloth_spine_01.s" "cloth_coatTail_01.is";
connectAttr "cloth_coatTail_01.s" "cloth_coatTail_02.is";
connectAttr "cloth_pelvis.s" "cloth_thigh_l.is";
connectAttr "cloth_thigh_l.s" "cloth_calf_l.is";
connectAttr "cloth_calf_l.s" "cloth_foot_l.is";
connectAttr "cloth_foot_l.s" "cloth_ball_l.is";
connectAttr "cloth_pelvis.s" "cloth_thigh_r.is";
connectAttr "cloth_thigh_r.s" "cloth_calf_r.is";
connectAttr "cloth_calf_r.s" "cloth_foot_r.is";
connectAttr "cloth_foot_r.s" "cloth_ball_r.is";
connectAttr "cloth_fit_ffdLattice_scaleX.o" "cloth_fit_ffdLattice.sx";
connectAttr "cloth_fit_ffdLattice_scaleZ.o" "cloth_fit_ffdLattice.sz";
connectAttr "cloth_fit_ffdLattice_scaleY.o" "cloth_fit_ffdLattice.sy";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "cloth_jacket_meshShapeOrig.w" "cloth_jacket_mesh_skinCluster.ip[0].ig"
		;
connectAttr "cloth_jacket_meshShapeOrig.o" "cloth_jacket_mesh_skinCluster.orggeom[0]"
		;
connectAttr "bindPose1.msg" "cloth_jacket_mesh_skinCluster.bp";
connectAttr "cloth_root.wm" "cloth_jacket_mesh_skinCluster.ma[0]";
connectAttr "cloth_pelvis.wm" "cloth_jacket_mesh_skinCluster.ma[1]";
connectAttr "cloth_spine_01.wm" "cloth_jacket_mesh_skinCluster.ma[2]";
connectAttr "cloth_spine_02.wm" "cloth_jacket_mesh_skinCluster.ma[3]";
connectAttr "cloth_spine_03.wm" "cloth_jacket_mesh_skinCluster.ma[4]";
connectAttr "cloth_spine_04.wm" "cloth_jacket_mesh_skinCluster.ma[5]";
connectAttr "cloth_spine_05.wm" "cloth_jacket_mesh_skinCluster.ma[6]";
connectAttr "cloth_neck_01.wm" "cloth_jacket_mesh_skinCluster.ma[7]";
connectAttr "cloth_neck_02.wm" "cloth_jacket_mesh_skinCluster.ma[8]";
connectAttr "cloth_clavicle_l.wm" "cloth_jacket_mesh_skinCluster.ma[9]";
connectAttr "cloth_upperarm_l.wm" "cloth_jacket_mesh_skinCluster.ma[10]";
connectAttr "cloth_lowerarm_l.wm" "cloth_jacket_mesh_skinCluster.ma[11]";
connectAttr "cloth_hand_l.wm" "cloth_jacket_mesh_skinCluster.ma[12]";
connectAttr "cloth_clavicle_r.wm" "cloth_jacket_mesh_skinCluster.ma[13]";
connectAttr "cloth_upperarm_r.wm" "cloth_jacket_mesh_skinCluster.ma[14]";
connectAttr "cloth_lowerarm_r.wm" "cloth_jacket_mesh_skinCluster.ma[15]";
connectAttr "cloth_hand_r.wm" "cloth_jacket_mesh_skinCluster.ma[16]";
connectAttr "cloth_thigh_l.wm" "cloth_jacket_mesh_skinCluster.ma[17]";
connectAttr "cloth_calf_l.wm" "cloth_jacket_mesh_skinCluster.ma[18]";
connectAttr "cloth_foot_l.wm" "cloth_jacket_mesh_skinCluster.ma[19]";
connectAttr "cloth_ball_l.wm" "cloth_jacket_mesh_skinCluster.ma[20]";
connectAttr "cloth_thigh_r.wm" "cloth_jacket_mesh_skinCluster.ma[21]";
connectAttr "cloth_calf_r.wm" "cloth_jacket_mesh_skinCluster.ma[22]";
connectAttr "cloth_foot_r.wm" "cloth_jacket_mesh_skinCluster.ma[23]";
connectAttr "cloth_ball_r.wm" "cloth_jacket_mesh_skinCluster.ma[24]";
connectAttr "cloth_root.liw" "cloth_jacket_mesh_skinCluster.lw[0]";
connectAttr "cloth_pelvis.liw" "cloth_jacket_mesh_skinCluster.lw[1]";
connectAttr "cloth_spine_01.liw" "cloth_jacket_mesh_skinCluster.lw[2]";
connectAttr "cloth_spine_02.liw" "cloth_jacket_mesh_skinCluster.lw[3]";
connectAttr "cloth_spine_03.liw" "cloth_jacket_mesh_skinCluster.lw[4]";
connectAttr "cloth_spine_04.liw" "cloth_jacket_mesh_skinCluster.lw[5]";
connectAttr "cloth_spine_05.liw" "cloth_jacket_mesh_skinCluster.lw[6]";
connectAttr "cloth_neck_01.liw" "cloth_jacket_mesh_skinCluster.lw[7]";
connectAttr "cloth_neck_02.liw" "cloth_jacket_mesh_skinCluster.lw[8]";
connectAttr "cloth_clavicle_l.liw" "cloth_jacket_mesh_skinCluster.lw[9]";
connectAttr "cloth_upperarm_l.liw" "cloth_jacket_mesh_skinCluster.lw[10]";
connectAttr "cloth_lowerarm_l.liw" "cloth_jacket_mesh_skinCluster.lw[11]";
connectAttr "cloth_hand_l.liw" "cloth_jacket_mesh_skinCluster.lw[12]";
connectAttr "cloth_clavicle_r.liw" "cloth_jacket_mesh_skinCluster.lw[13]";
connectAttr "cloth_upperarm_r.liw" "cloth_jacket_mesh_skinCluster.lw[14]";
connectAttr "cloth_lowerarm_r.liw" "cloth_jacket_mesh_skinCluster.lw[15]";
connectAttr "cloth_hand_r.liw" "cloth_jacket_mesh_skinCluster.lw[16]";
connectAttr "cloth_thigh_l.liw" "cloth_jacket_mesh_skinCluster.lw[17]";
connectAttr "cloth_calf_l.liw" "cloth_jacket_mesh_skinCluster.lw[18]";
connectAttr "cloth_foot_l.liw" "cloth_jacket_mesh_skinCluster.lw[19]";
connectAttr "cloth_ball_l.liw" "cloth_jacket_mesh_skinCluster.lw[20]";
connectAttr "cloth_thigh_r.liw" "cloth_jacket_mesh_skinCluster.lw[21]";
connectAttr "cloth_calf_r.liw" "cloth_jacket_mesh_skinCluster.lw[22]";
connectAttr "cloth_foot_r.liw" "cloth_jacket_mesh_skinCluster.lw[23]";
connectAttr "cloth_ball_r.liw" "cloth_jacket_mesh_skinCluster.lw[24]";
connectAttr "cloth_root.obcc" "cloth_jacket_mesh_skinCluster.ifcl[0]";
connectAttr "cloth_pelvis.obcc" "cloth_jacket_mesh_skinCluster.ifcl[1]";
connectAttr "cloth_spine_01.obcc" "cloth_jacket_mesh_skinCluster.ifcl[2]";
connectAttr "cloth_spine_02.obcc" "cloth_jacket_mesh_skinCluster.ifcl[3]";
connectAttr "cloth_spine_03.obcc" "cloth_jacket_mesh_skinCluster.ifcl[4]";
connectAttr "cloth_spine_04.obcc" "cloth_jacket_mesh_skinCluster.ifcl[5]";
connectAttr "cloth_spine_05.obcc" "cloth_jacket_mesh_skinCluster.ifcl[6]";
connectAttr "cloth_neck_01.obcc" "cloth_jacket_mesh_skinCluster.ifcl[7]";
connectAttr "cloth_neck_02.obcc" "cloth_jacket_mesh_skinCluster.ifcl[8]";
connectAttr "cloth_clavicle_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[9]";
connectAttr "cloth_upperarm_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[10]";
connectAttr "cloth_lowerarm_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[11]";
connectAttr "cloth_hand_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[12]";
connectAttr "cloth_clavicle_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[13]";
connectAttr "cloth_upperarm_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[14]";
connectAttr "cloth_lowerarm_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[15]";
connectAttr "cloth_hand_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[16]";
connectAttr "cloth_thigh_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[17]";
connectAttr "cloth_calf_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[18]";
connectAttr "cloth_foot_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[19]";
connectAttr "cloth_ball_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[20]";
connectAttr "cloth_thigh_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[21]";
connectAttr "cloth_calf_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[22]";
connectAttr "cloth_foot_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[23]";
connectAttr "cloth_ball_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[24]";
connectAttr "cloth_root.msg" "bindPose1.m[0]";
connectAttr "cloth_pelvis.msg" "bindPose1.m[1]";
connectAttr "cloth_spine_01.msg" "bindPose1.m[2]";
connectAttr "cloth_spine_02.msg" "bindPose1.m[3]";
connectAttr "cloth_spine_03.msg" "bindPose1.m[4]";
connectAttr "cloth_spine_04.msg" "bindPose1.m[5]";
connectAttr "cloth_spine_05.msg" "bindPose1.m[6]";
connectAttr "cloth_neck_01.msg" "bindPose1.m[7]";
connectAttr "cloth_neck_02.msg" "bindPose1.m[8]";
connectAttr "cloth_clavicle_l.msg" "bindPose1.m[9]";
connectAttr "cloth_upperarm_l.msg" "bindPose1.m[10]";
connectAttr "cloth_lowerarm_l.msg" "bindPose1.m[11]";
connectAttr "cloth_hand_l.msg" "bindPose1.m[12]";
connectAttr "cloth_clavicle_r.msg" "bindPose1.m[13]";
connectAttr "cloth_upperarm_r.msg" "bindPose1.m[14]";
connectAttr "cloth_lowerarm_r.msg" "bindPose1.m[15]";
connectAttr "cloth_hand_r.msg" "bindPose1.m[16]";
connectAttr "cloth_thigh_l.msg" "bindPose1.m[17]";
connectAttr "cloth_calf_l.msg" "bindPose1.m[18]";
connectAttr "cloth_foot_l.msg" "bindPose1.m[19]";
connectAttr "cloth_ball_l.msg" "bindPose1.m[20]";
connectAttr "cloth_thigh_r.msg" "bindPose1.m[21]";
connectAttr "cloth_calf_r.msg" "bindPose1.m[22]";
connectAttr "cloth_foot_r.msg" "bindPose1.m[23]";
connectAttr "cloth_ball_r.msg" "bindPose1.m[24]";
connectAttr "bindPose1.w" "bindPose1.p[0]";
connectAttr "bindPose1.m[0]" "bindPose1.p[1]";
connectAttr "bindPose1.m[1]" "bindPose1.p[2]";
connectAttr "bindPose1.m[2]" "bindPose1.p[3]";
connectAttr "bindPose1.m[3]" "bindPose1.p[4]";
connectAttr "bindPose1.m[4]" "bindPose1.p[5]";
connectAttr "bindPose1.m[5]" "bindPose1.p[6]";
connectAttr "bindPose1.m[6]" "bindPose1.p[7]";
connectAttr "bindPose1.m[7]" "bindPose1.p[8]";
connectAttr "bindPose1.m[6]" "bindPose1.p[9]";
connectAttr "bindPose1.m[9]" "bindPose1.p[10]";
connectAttr "bindPose1.m[10]" "bindPose1.p[11]";
connectAttr "bindPose1.m[11]" "bindPose1.p[12]";
connectAttr "bindPose1.m[6]" "bindPose1.p[13]";
connectAttr "bindPose1.m[13]" "bindPose1.p[14]";
connectAttr "bindPose1.m[14]" "bindPose1.p[15]";
connectAttr "bindPose1.m[15]" "bindPose1.p[16]";
connectAttr "bindPose1.m[1]" "bindPose1.p[17]";
connectAttr "bindPose1.m[17]" "bindPose1.p[18]";
connectAttr "bindPose1.m[18]" "bindPose1.p[19]";
connectAttr "bindPose1.m[19]" "bindPose1.p[20]";
connectAttr "bindPose1.m[1]" "bindPose1.p[21]";
connectAttr "bindPose1.m[21]" "bindPose1.p[22]";
connectAttr "bindPose1.m[22]" "bindPose1.p[23]";
connectAttr "bindPose1.m[23]" "bindPose1.p[24]";
connectAttr "cloth_root.bps" "bindPose1.wm[0]";
connectAttr "cloth_pelvis.bps" "bindPose1.wm[1]";
connectAttr "cloth_spine_01.bps" "bindPose1.wm[2]";
connectAttr "cloth_spine_02.bps" "bindPose1.wm[3]";
connectAttr "cloth_spine_03.bps" "bindPose1.wm[4]";
connectAttr "cloth_spine_04.bps" "bindPose1.wm[5]";
connectAttr "cloth_spine_05.bps" "bindPose1.wm[6]";
connectAttr "cloth_neck_01.bps" "bindPose1.wm[7]";
connectAttr "cloth_neck_02.bps" "bindPose1.wm[8]";
connectAttr "cloth_clavicle_l.bps" "bindPose1.wm[9]";
connectAttr "cloth_upperarm_l.bps" "bindPose1.wm[10]";
connectAttr "cloth_lowerarm_l.bps" "bindPose1.wm[11]";
connectAttr "cloth_hand_l.bps" "bindPose1.wm[12]";
connectAttr "cloth_clavicle_r.bps" "bindPose1.wm[13]";
connectAttr "cloth_upperarm_r.bps" "bindPose1.wm[14]";
connectAttr "cloth_lowerarm_r.bps" "bindPose1.wm[15]";
connectAttr "cloth_hand_r.bps" "bindPose1.wm[16]";
connectAttr "cloth_thigh_l.bps" "bindPose1.wm[17]";
connectAttr "cloth_calf_l.bps" "bindPose1.wm[18]";
connectAttr "cloth_foot_l.bps" "bindPose1.wm[19]";
connectAttr "cloth_ball_l.bps" "bindPose1.wm[20]";
connectAttr "cloth_thigh_r.bps" "bindPose1.wm[21]";
connectAttr "cloth_calf_r.bps" "bindPose1.wm[22]";
connectAttr "cloth_foot_r.bps" "bindPose1.wm[23]";
connectAttr "cloth_ball_r.bps" "bindPose1.wm[24]";
connectAttr "cloth_collar_meshShapeOrig.w" "cloth_collar_mesh_skinCluster.ip[0].ig"
		;
connectAttr "cloth_collar_meshShapeOrig.o" "cloth_collar_mesh_skinCluster.orggeom[0]"
		;
connectAttr "cloth_root.wm" "cloth_collar_mesh_skinCluster.ma[0]";
connectAttr "cloth_pelvis.wm" "cloth_collar_mesh_skinCluster.ma[1]";
connectAttr "cloth_spine_01.wm" "cloth_collar_mesh_skinCluster.ma[2]";
connectAttr "cloth_spine_02.wm" "cloth_collar_mesh_skinCluster.ma[3]";
connectAttr "cloth_spine_03.wm" "cloth_collar_mesh_skinCluster.ma[4]";
connectAttr "cloth_spine_04.wm" "cloth_collar_mesh_skinCluster.ma[5]";
connectAttr "cloth_spine_05.wm" "cloth_collar_mesh_skinCluster.ma[6]";
connectAttr "cloth_neck_01.wm" "cloth_collar_mesh_skinCluster.ma[7]";
connectAttr "cloth_neck_02.wm" "cloth_collar_mesh_skinCluster.ma[8]";
connectAttr "cloth_clavicle_l.wm" "cloth_collar_mesh_skinCluster.ma[9]";
connectAttr "cloth_upperarm_l.wm" "cloth_collar_mesh_skinCluster.ma[10]";
connectAttr "cloth_lowerarm_l.wm" "cloth_collar_mesh_skinCluster.ma[11]";
connectAttr "cloth_hand_l.wm" "cloth_collar_mesh_skinCluster.ma[12]";
connectAttr "cloth_clavicle_r.wm" "cloth_collar_mesh_skinCluster.ma[13]";
connectAttr "cloth_upperarm_r.wm" "cloth_collar_mesh_skinCluster.ma[14]";
connectAttr "cloth_lowerarm_r.wm" "cloth_collar_mesh_skinCluster.ma[15]";
connectAttr "cloth_hand_r.wm" "cloth_collar_mesh_skinCluster.ma[16]";
connectAttr "cloth_thigh_l.wm" "cloth_collar_mesh_skinCluster.ma[17]";
connectAttr "cloth_calf_l.wm" "cloth_collar_mesh_skinCluster.ma[18]";
connectAttr "cloth_foot_l.wm" "cloth_collar_mesh_skinCluster.ma[19]";
connectAttr "cloth_ball_l.wm" "cloth_collar_mesh_skinCluster.ma[20]";
connectAttr "cloth_thigh_r.wm" "cloth_collar_mesh_skinCluster.ma[21]";
connectAttr "cloth_calf_r.wm" "cloth_collar_mesh_skinCluster.ma[22]";
connectAttr "cloth_foot_r.wm" "cloth_collar_mesh_skinCluster.ma[23]";
connectAttr "cloth_ball_r.wm" "cloth_collar_mesh_skinCluster.ma[24]";
connectAttr "cloth_root.liw" "cloth_collar_mesh_skinCluster.lw[0]";
connectAttr "cloth_pelvis.liw" "cloth_collar_mesh_skinCluster.lw[1]";
connectAttr "cloth_spine_01.liw" "cloth_collar_mesh_skinCluster.lw[2]";
connectAttr "cloth_spine_02.liw" "cloth_collar_mesh_skinCluster.lw[3]";
connectAttr "cloth_spine_03.liw" "cloth_collar_mesh_skinCluster.lw[4]";
connectAttr "cloth_spine_04.liw" "cloth_collar_mesh_skinCluster.lw[5]";
connectAttr "cloth_spine_05.liw" "cloth_collar_mesh_skinCluster.lw[6]";
connectAttr "cloth_neck_01.liw" "cloth_collar_mesh_skinCluster.lw[7]";
connectAttr "cloth_neck_02.liw" "cloth_collar_mesh_skinCluster.lw[8]";
connectAttr "cloth_clavicle_l.liw" "cloth_collar_mesh_skinCluster.lw[9]";
connectAttr "cloth_upperarm_l.liw" "cloth_collar_mesh_skinCluster.lw[10]";
connectAttr "cloth_lowerarm_l.liw" "cloth_collar_mesh_skinCluster.lw[11]";
connectAttr "cloth_hand_l.liw" "cloth_collar_mesh_skinCluster.lw[12]";
connectAttr "cloth_clavicle_r.liw" "cloth_collar_mesh_skinCluster.lw[13]";
connectAttr "cloth_upperarm_r.liw" "cloth_collar_mesh_skinCluster.lw[14]";
connectAttr "cloth_lowerarm_r.liw" "cloth_collar_mesh_skinCluster.lw[15]";
connectAttr "cloth_hand_r.liw" "cloth_collar_mesh_skinCluster.lw[16]";
connectAttr "cloth_thigh_l.liw" "cloth_collar_mesh_skinCluster.lw[17]";
connectAttr "cloth_calf_l.liw" "cloth_collar_mesh_skinCluster.lw[18]";
connectAttr "cloth_foot_l.liw" "cloth_collar_mesh_skinCluster.lw[19]";
connectAttr "cloth_ball_l.liw" "cloth_collar_mesh_skinCluster.lw[20]";
connectAttr "cloth_thigh_r.liw" "cloth_collar_mesh_skinCluster.lw[21]";
connectAttr "cloth_calf_r.liw" "cloth_collar_mesh_skinCluster.lw[22]";
connectAttr "cloth_foot_r.liw" "cloth_collar_mesh_skinCluster.lw[23]";
connectAttr "cloth_ball_r.liw" "cloth_collar_mesh_skinCluster.lw[24]";
connectAttr "cloth_root.obcc" "cloth_collar_mesh_skinCluster.ifcl[0]";
connectAttr "cloth_pelvis.obcc" "cloth_collar_mesh_skinCluster.ifcl[1]";
connectAttr "cloth_spine_01.obcc" "cloth_collar_mesh_skinCluster.ifcl[2]";
connectAttr "cloth_spine_02.obcc" "cloth_collar_mesh_skinCluster.ifcl[3]";
connectAttr "cloth_spine_03.obcc" "cloth_collar_mesh_skinCluster.ifcl[4]";
connectAttr "cloth_spine_04.obcc" "cloth_collar_mesh_skinCluster.ifcl[5]";
connectAttr "cloth_spine_05.obcc" "cloth_collar_mesh_skinCluster.ifcl[6]";
connectAttr "cloth_neck_01.obcc" "cloth_collar_mesh_skinCluster.ifcl[7]";
connectAttr "cloth_neck_02.obcc" "cloth_collar_mesh_skinCluster.ifcl[8]";
connectAttr "cloth_clavicle_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[9]";
connectAttr "cloth_upperarm_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[10]";
connectAttr "cloth_lowerarm_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[11]";
connectAttr "cloth_hand_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[12]";
connectAttr "cloth_clavicle_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[13]";
connectAttr "cloth_upperarm_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[14]";
connectAttr "cloth_lowerarm_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[15]";
connectAttr "cloth_hand_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[16]";
connectAttr "cloth_thigh_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[17]";
connectAttr "cloth_calf_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[18]";
connectAttr "cloth_foot_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[19]";
connectAttr "cloth_ball_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[20]";
connectAttr "cloth_thigh_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[21]";
connectAttr "cloth_calf_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[22]";
connectAttr "cloth_foot_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[23]";
connectAttr "cloth_ball_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[24]";
connectAttr "bindPose1.msg" "cloth_collar_mesh_skinCluster.bp";
connectAttr "cloth_jacket_mesh_skinCluster.og[0]" "cloth_fit_ffd.ip[0].ig";
connectAttr "cloth_collar_mesh_skinCluster.og[0]" "cloth_fit_ffd.ip[1].ig";
connectAttr "cloth_jacket_meshShapeOrig.o" "cloth_fit_ffd.orggeom[0]";
connectAttr "cloth_collar_meshShapeOrig.o" "cloth_fit_ffd.orggeom[1]";
connectAttr "cloth_fit_ffdLatticeShape.wm" "cloth_fit_ffd.dlm";
connectAttr "cloth_fit_ffdLatticeShape.lo" "cloth_fit_ffd.dlp";
connectAttr "cloth_fit_ffdBaseShape.wm" "cloth_fit_ffd.blm";
connectAttr "cloth_fit_ctrl.fit_tightness" "cloth_fit_ffdLattice_scaleX.i";
connectAttr "cloth_fit_ctrl.fit_tightness" "cloth_fit_ffdLattice_scaleZ.i";
connectAttr "cloth_fit_ctrl.fit_length" "cloth_fit_ffdLattice_scaleY.i";
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
connectAttr "cloth_jacket_meshShape.iog" ":initialShadingGroup.dsm" -na;
connectAttr "cloth_collar_meshShape.iog" ":initialShadingGroup.dsm" -na;
// End of trench_coat_A.ma
