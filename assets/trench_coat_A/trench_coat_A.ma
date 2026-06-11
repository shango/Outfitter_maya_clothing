//Maya ASCII 2026 scene
//Name: trench_coat_A.ma
//Last modified: Thu, Jun 11, 2026 10:50:16 AM
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
fileInfo "UUID" "611F5541-4A9B-E6EB-8EAE-42AEEEB6422A";
createNode transform -s -n "persp";
	rename -uid "F8EECCA7-4DAE-9DA5-53A2-2884E6154248";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 28 21 28 ;
	setAttr ".r" -type "double3" -27.938352729602379 44.999999999999972 -5.172681101354183e-14 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "C7370298-4E34-18FB-6A77-17BDBF0F0581";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 44.82186966202994;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "F43DF560-475B-FB36-2E61-47B6F03B40C1";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 1000.1 0 ;
	setAttr ".r" -type "double3" -90 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "49E1FEBD-40FB-0037-813B-E99734B54E8E";
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
	rename -uid "7A0C601E-409C-40D2-BF0E-7DAD657AED9A";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 0 0 1000.1 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "FF25E347-41BF-D998-7124-519C5BA0A2F8";
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
	rename -uid "90D2B436-4FB6-5ECA-E52F-EA99E65B80DA";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1000.1 0 0 ;
	setAttr ".r" -type "double3" 0 90 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "6A62A4E4-44C7-DF80-0148-EAA66273A522";
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
	rename -uid "DA33706E-42E9-8E51-E25C-E3A2408C6AC8";
	setAttr ".rp" -type "double3" 1.6208943399931286e-05 94.200613157989736 14.675905856587022 ;
	setAttr ".sp" -type "double3" 1.6208943399931286e-05 94.200613157989736 14.675905856587022 ;
createNode transform -n "Mesh_GRP" -p "cloth_trench_coat_A";
	rename -uid "EEA5B5D0-4C16-2AEE-8B40-15A41B8EED68";
createNode transform -n "cloth_jacket_mesh" -p "Mesh_GRP";
	rename -uid "C9B3140E-478A-326D-6E12-19AB3CD74F4F";
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
	rename -uid "5277F017-4BA5-41CA-950D-AFAD61AB3004";
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
	rename -uid "CF992882-4EF4-0943-2C17-48A9F516FD9B";
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
	rename -uid "DAFD47C8-478F-9B10-04BE-A6B3731F3562";
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
	rename -uid "92E21816-4ECF-9619-C2B6-1FAB2D9C722D";
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
	rename -uid "6F554361-4481-331B-B3FB-C4B0DA6F75D5";
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
	rename -uid "50016287-4055-CD85-0BD0-94BEEF8F26C1";
	setAttr ".r" -type "double3" -90 0 0 ;
createNode joint -n "cloth_root" -p "Rig_GRP";
	rename -uid "6A3C7A43-4112-2AB0-B3E2-AF9367E0BA4B";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "jointTRSData" -ln "jointTRSData" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 0 -1 0 0 1 0 0 0 0 0 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".jointTRSData" -type "string" (
		"(dp0&lf;Vupperarm_bicep_l&lf;p1&lf;(dp2&lf;S'rotation'&lf;p3&lf;(F-2.112087093159394e-16&lf;F1.6101558074909054e-14&lf;F-1.948089742396404e-14&lf;tp4&lf;sS'translate'&lf;p5&lf;(F0.4296336514963315&lf;F-3.0014054840172104&lf;F-0.33568228722386095&lf;tp6&lf;sS'scale'&lf;p7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp8&lf;ssVthigh_fwd_r&lf;p9&lf;(dp10&lf;g3&lf;(F-3.2351075555054503e-09&lf;F-3.554814002738346e-09&lf;F4.6893499014910565e-09&lf;tp11&lf;sg5&lf;(F-5.8879919004175605&lf;F7.159845239867742&lf;F-0.8596299999494192&lf;tp12&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp13&lf;ssVupperarm_twist_02_r&lf;p14&lf;(dp15&lf;g3&lf;(F-5.715515410477199e-05&lf;F0.239297380467856&lf;F-0.013684890989370199&lf;tp16&lf;sg5&lf;(F-16.831266561863387&lf;F1.8815802156346706e-05&lf;F-0.00023473533977380612&lf;tp17&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp18&lf;ssVthigh_fwd_l&lf;p19&lf;(dp20&lf;g3&lf;(F-3.0625942677403114e-09&lf;F3.73169190518625e-08&lf;F5.2113571248109e-09&lf;tp21&lf;sg5&lf;(F5.892345071609&lf;F-7.144273484161924&lf;F0.8632194689173218&lf;tp22&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp23&lf;ssVupperarm_twist_02_l&lf;p24&lf;(dp25&lf;g3&lf;(F-5.715515410371704e-05&lf;F0.2392973804688322&lf;F-0.013684890989424315&lf;tp26&lf;sg5&lf;(F16.83153379318587&lf;F1.7763568394002505e-15&lf;F0.0&lf;tp27&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp28&lf;ssVspine_02&lf;p29&lf;(dp30&lf;g3&lf;(F-1.2132853246549658e-20&lf;F-5.763105292111093e-19&lf;F-2.3854160140597598e-15&lf;tp31&lf;sg5&lf;(F4.64819543873827&lf;F0.0&lf;F9.247810850432359e-15&lf;tp32&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp33&lf;ssVspine_03&lf;p34&lf;(dp35&lf;g3&lf;(F3.8839555994523184e-42&lf;F9.390828412829445e-18&lf;F4.739395799433465e-23&lf;tp36&lf;sg5&lf;(F7.10706776307444&lf;F7.105427357601002e-15&lf;F-1.6302063865492045e-14&lf;tp37&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp38&lf;ssVspine_04&lf;p39&lf;(dp40&lf;g3&lf;(F-5.823769558343841e-19&lf;F4.246498636292384e-20&lf;F1.590277269640821e-15&lf;tp41&lf;sg5&lf;(F8.248942899748158&lf;F3.552713678800501e-15&lf;F-2.1010970741031088e-14&lf;tp42&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp43&lf;ssVspine_05&lf;p44&lf;(dp45&lf;g3&lf;(F-1.4559423895859602e-19&lf;F4.659679162086993e-18&lf;F1.4908847995874568e-16&lf;tp46&lf;sg5&lf;(F16.308254953927232&lf;F-7.105427357601002e-15&lf;F2.3062281251373662e-14&lf;tp47&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp48&lf;ssVindex_metacarpal_r&lf;p49&lf;(dp50&lf;g3&lf;(F-4.808104147368675e-15&lf;F2.4351121779955047e-15&lf;F2.2363275104040347e-15&lf;tp51&lf;sg5&lf;(F-3.457892340165678&lf;F-0.010593711576447618&lf;F1.529324513338704&lf;tp52&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp53&lf;ssVupperarm_bicep_r&lf;p54&lf;(dp55&lf;g3&lf;(F3.1557065980145833e-14&lf;F5.367186024969683e-15&lf;F6.361109362927035e-15&lf;tp56&lf;sg5&lf;(F-0.570192043047129&lf;F3.0080906171650774&lf;F0.15133974465763345&lf;tp57&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp58&lf;ssVlowerarm_in_r&lf;p59&lf;(dp60&lf;g3&lf;(F2.5444437451708134e-14&lf;F0.0&lf;F0.0&lf;tp61&lf;sg5&lf;(F-1.5514355804486115&lf;F-0.21415705989632272&lf;F2.2829596952656743&lf;tp62&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp63&lf;ssVwrist_inner_l&lf;p64&lf;(dp65&lf;g3&lf;(F-5.1497652947915144e-14&lf;F-9.541664044390552e-15&lf;F-4.174478019420861e-15&lf;tp66&lf;sg5&lf;(F-0.08634634823715714&lf;F1.6269678363065907&lf;F-0.47525639176425827&lf;tp67&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp68&lf;ssVthigh_out_r&lf;p69&lf;(dp70&lf;g3&lf;(F-1.122660004060381e-09&lf;F7.74599041022121e-09&lf;F1.0052238419628676e-08&lf;tp71&lf;sg5&lf;(F-5.490222724311039&lf;F-1.2357139686785958&lf;F4.529304741894016&lf;tp72&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp73&lf;ssVclavicle_l&lf;p74&lf;(dp75&lf;g3&lf;(F-2.7034714792439897e-14&lf;F6.659286364314223e-15&lf;F359.99999999999994&lf;tp76&lf;sg5&lf;(F5.434344857110261&lf;F0.9364505906511198&lf;F-0.866799571158099&lf;tp77&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp78&lf;ssVupperarm_twist_01_r&lf;p79&lf;(dp80&lf;g3&lf;(F-6.1858806299137406e-15&lf;F-2.4343783062529425e-15&lf;F-9.660793900053754e-15&lf;tp81&lf;sg5&lf;(F-8.639670830686583&lf;F0.09629670980522409&lf;F0.16541554783053414&lf;tp82&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp83&lf;ssVball_r&lf;p84&lf;(dp85&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp86&lf;sg5&lf;(F5.70729832865123&lf;F11.471707953183119&lf;F0.00175755891641316&lf;tp87&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp88&lf;ssVthigh_twistCor_01_r&lf;p89&lf;(dp90&lf;g3&lf;(F-7.966473664013811e-13&lf;F7.136261186895984e-18&lf;F-1.5803581998339445e-10&lf;tp91&lf;sg5&lf;(F-6.110667527536862e-13&lf;F-2.0383694732117874e-13&lf;F7.105427357601002e-15&lf;tp92&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp93&lf;ssVthigh_twistCor_01_l&lf;p94&lf;(dp95&lf;g3&lf;(F-7.679131785889907e-13&lf;F-6.227958139655539e-18&lf;F-1.5803582267887843e-10&lf;tp96&lf;sg5&lf;(F6.252776074688882e-13&lf;F2.0294876890147862e-13&lf;F-1.0658141036401503e-14&lf;tp97&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp98&lf;ssVindex_03_l&lf;p99&lf;(dp100&lf;g3&lf;(F-5.308123295365481e-21&lf;F2.1581542102166356e-40&lf;F4.6590149061444796e-18&lf;tp101&lf;sg5&lf;(F2.3173075307279305&lf;F2.842170943040401e-14&lf;F9.769962616701378e-15&lf;tp102&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp103&lf;ssVball_l&lf;p104&lf;(dp105&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp106&lf;sg5&lf;(F-5.707299374390027&lf;F-11.471697092323957&lf;F-0.0017138404028358423&lf;tp107&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp108&lf;ssVupperarm_twist_01_l&lf;p109&lf;(dp110&lf;g3&lf;(F2.5988450325576927e-15&lf;F1.4877974460841166e-16&lf;F3.2046487033437818e-15&lf;tp111&lf;sg5&lf;(F8.63996069843948&lf;F-0.09628023891043291&lf;F-0.16557725147991675&lf;tp112&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp113&lf;ssVclavicle_r&lf;p114&lf;(dp115&lf;g3&lf;(F180.0&lf;F180.0&lf;F-180.0&lf;tp116&lf;sg5&lf;(F5.433600703058573&lf;F0.9365499957792274&lf;F0.8688515061571342&lf;tp117&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp118&lf;ssVwrist_inner_r&lf;p119&lf;(dp120&lf;g3&lf;(F-1.2709794684129601e-14&lf;F3.1805546814635168e-15&lf;F-3.578124016646457e-15&lf;tp121&lf;sg5&lf;(F0.05073241165543152&lf;F-1.456593948087047&lf;F0.4146242448130657&lf;tp122&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp123&lf;ssVthigh_out_l&lf;p124&lf;(dp125&lf;g3&lf;(F-7.841617927850014e-09&lf;F-1.611360794686607e-08&lf;F-6.402664334885883e-09&lf;tp126&lf;sg5&lf;(F5.488080642544915&lf;F1.2215333393427994&lf;F-4.541695609589556&lf;tp127&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp128&lf;ssVclavicle_out_l&lf;p129&lf;(dp130&lf;g3&lf;(F2.1369351765716433e-15&lf;F-3.0719030044415276e-10&lf;F1.3674210922985612e-14&lf;tp131&lf;sg5&lf;(F10.05977550712825&lf;F0.047623277898917404&lf;F5.124009981794558&lf;tp132&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp133&lf;ssVthigh_l&lf;p134&lf;(dp135&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp136&lf;sg5&lf;(F-3.011926735188311&lf;F-0.06340308345171675&lf;F-10.395847431675032&lf;tp137&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp138&lf;ssVcalf_correctiveRoot_l&lf;p139&lf;(dp140&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp141&lf;sg5&lf;(F7.105427357601002e-15&lf;F-4.440892098500626e-16&lf;F-8.881784197001252e-15&lf;tp142&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp143&lf;ssVclavicle_out_r&lf;p144&lf;(dp145&lf;g3&lf;(F1.5853077242196556e-14&lf;F-1.733539619516481e-08&lf;F-1.1745378447666112e-14&lf;tp146&lf;sg5&lf;(F-10.296855532639404&lf;F0.1711587055647632&lf;F-5.132314944700084&lf;tp147&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp148&lf;ssVfoot_l&lf;p149&lf;(dp150&lf;g3&lf;(F3.1060104311167183e-18&lf;F-3.975696764194372e-15&lf;F-7.450785178706153e-17&lf;tp151&lf;sg5&lf;(F-38.868305766260185&lf;F-1.8835664532534935e-06&lf;F-6.242941395839807e-06&lf;tp152&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp153&lf;ssVthigh_correctiveRoot_l&lf;p154&lf;(dp155&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp156&lf;sg5&lf;(F1.4210854715202004e-14&lf;F2.6645352591003757e-15&lf;F3.552713678800501e-15&lf;tp157&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp158&lf;ssVspine_01&lf;p159&lf;(dp160&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp161&lf;sg5&lf;(F2.303684184416582&lf;F3.552713678800501e-15&lf;F8.632417697329586e-16&lf;tp162&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp163&lf;ssVupperarm_out_r&lf;p164&lf;(dp165&lf;g3&lf;(F0.0&lf;F7.727962875304028e-09&lf;F0.0&lf;tp166&lf;sg5&lf;(F-0.0015998720624850193&lf;F-0.26206737267851477&lf;F-5.478375142778077&lf;tp167&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp168&lf;ssVmiddle_03_l&lf;p169&lf;(dp170&lf;g3&lf;(F-6.212020862233431e-18&lf;F-7.442292181433567e-17&lf;F3.975754016095629e-16&lf;tp171&lf;sg5&lf;(F2.7046150315646855&lf;F-7.105427357601002e-15&lf;F-7.105427357601002e-15&lf;tp172&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp173&lf;ssVring_02_r&lf;p174&lf;(dp175&lf;g3&lf;(F3.7272125173400593e-17&lf;F-9.93923337957349e-17&lf;F-9.541615512977564e-15&lf;tp176&lf;sg5&lf;(F-3.9621715292690425&lf;F1.5004568538756757e-05&lf;F-4.923994394800957e-05&lf;tp177&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp178&lf;ssVthumb_01_r&lf;p179&lf;(dp180&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp181&lf;sg5&lf;(F-2.4749759005593006&lf;F-1.2059805117236948&lf;F2.2430633666914694&lf;tp182&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp183&lf;ssVthumb_01_l&lf;p184&lf;(dp185&lf;g3&lf;(F-1.3517357396219944e-14&lf;F-7.951386703658789e-15&lf;F3.1805546814635168e-15&lf;tp186&lf;sg5&lf;(F2.4749410357123125&lf;F1.2059493890390485&lf;F-2.242953361528688&lf;tp187&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp188&lf;ssVring_02_l&lf;p189&lf;(dp190&lf;g3&lf;(F2.4848083448933737e-17&lf;F-1.4287647983136886e-16&lf;F-1.272226725726705e-14&lf;tp191&lf;sg5&lf;(F3.962151505953962&lf;F-1.4210854715202004e-14&lf;F-3.907985046680551e-14&lf;tp192&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp193&lf;ssVupperarm_out_l&lf;p194&lf;(dp195&lf;g3&lf;(F0.0&lf;F7.727962875304028e-09&lf;F0.0&lf;tp196&lf;sg5&lf;(F-0.13826645305934449&lf;F0.26872367525577534&lf;F5.293475235855169&lf;tp197&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp198&lf;ssVmiddle_03_r&lf;p199&lf;(dp200&lf;g3&lf;(F-1.5530052155583591e-18&lf;F-7.454425034680117e-17&lf;F1.5902788573384142e-15&lf;tp201&lf;sg5&lf;(F-2.7046326736289075&lf;F1.1443238847164139e-05&lf;F2.466278816015688e-05&lf;tp202&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp203&lf;ssVankle_fwd_r&lf;p204&lf;(dp205&lf;g3&lf;(F3.602972100095387e-16&lf;F-2.882377680076312e-15&lf;F1.1927080055488187e-14&lf;tp206&lf;sg5&lf;(F-1.6349691499013561&lf;F4.197070299797255&lf;F-0.4635870315139865&lf;tp207&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp208&lf;ssVthigh_correctiveRoot_r&lf;p209&lf;(dp210&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp211&lf;sg5&lf;(F0.0&lf;F-1.7763568394002505e-15&lf;F-5.329070518200751e-15&lf;tp212&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp213&lf;ssVcalf_correctiveRoot_r&lf;p214&lf;(dp215&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp216&lf;sg5&lf;(F7.105427357601002e-15&lf;F-8.881784197001252e-16&lf;F-1.7763568394002505e-15&lf;tp217&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp218&lf;ssVthigh_bck_lwr_l&lf;p219&lf;(dp220&lf;g3&lf;(F2.5444437451708134e-14&lf;F0.0&lf;F0.0&lf;tp221&lf;sg5&lf;(F-5.597656441629496&lf;F9.947071814613224&lf;F1.4709560480788824&lf;tp222&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp223&lf;ssVupperarm_twistCor_01_r&lf;p224&lf;(dp225&lf;g3&lf;(F-5.715515408476811e-05&lf;F0.2392973804678571&lf;F-0.013684890989359285&lf;tp226&lf;sg5&lf;(F0.22332124117612295&lf;F-0.09634080925396127&lf;F-0.16646707192127508&lf;tp227&lf;sg7&lf;(F0.9999999999999997&lf;F1.0&lf;F0.9999999999999998&lf;tp228&lf;ssVhand_r&lf;p229&lf;(dp230&lf;g3&lf;(F-1.9878466759146967e-16&lf;F-4.770832022195275e-15&lf;F-3.1805546814635168e-15&lf;tp231&lf;sg5&lf;(F-24.320337470574643&lf;F-0.0002950651889577216&lf;F0.0003046297929785169&lf;tp232&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp233&lf;ssVthumb_03_l&lf;p234&lf;(dp235&lf;g3&lf;(F-3.416611474228386e-17&lf;F-4.7366659074529904e-17&lf;F-4.246498636292382e-20&lf;tp236&lf;sg5&lf;(F2.5261795391662645&lf;F3.552713678800501e-14&lf;F-4.263256414560601e-14&lf;tp237&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp238&lf;ssVhand_l&lf;p239&lf;(dp240&lf;g3&lf;(F-6.6592863643142385e-15&lf;F-3.1805546814635168e-15&lf;F-3.1805546814635164e-15&lf;tp241&lf;sg5&lf;(F24.32004358863988&lf;F0.0&lf;F1.4210854715202004e-14&lf;tp242&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp243&lf;ssVthumb_03_r&lf;p244&lf;(dp245&lf;g3&lf;(F-2.174207301781701e-17&lf;F-2.348920388532016e-17&lf;F-4.770874487181638e-15&lf;tp246&lf;sg5&lf;(F-2.526164976356057&lf;F-4.6664516247574284e-05&lf;F7.370655225713563e-06&lf;tp247&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp248&lf;ssVupperarm_twistCor_01_l&lf;p249&lf;(dp250&lf;g3&lf;(F-5.7155154111593384e-05&lf;F0.23929738046885052&lf;F-0.013684890989412526&lf;tp251&lf;sg5&lf;(F-0.22347730841758562&lf;F0.09633378358038591&lf;F0.16651206011033537&lf;tp252&lf;sg7&lf;(F0.9999999999999999&lf;F1.0&lf;F0.9999999999999999&lf;tp253&lf;ssVthigh_bck_lwr_r&lf;p254&lf;(dp255&lf;g3&lf;(F-2.5444437451708134e-14&lf;F0.0&lf;F0.0&lf;tp256&lf;sg5&lf;(F5.844458568800249&lf;F-10.021941949068122&lf;F-1.8531909603709966&lf;tp257&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp258&lf;ssVupperarm_in_r&lf;p259&lf;(dp260&lf;g3&lf;(F-4.0183257565534246e-10&lf;F-4.683048712998474e-10&lf;F-3.3057467384465757e-10&lf;tp261&lf;sg5&lf;(F-5.2225564187980495&lf;F1.2711843167447734&lf;F3.8834782317378966&lf;tp262&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp263&lf;ssVlowerarm_fwd_r&lf;p264&lf;(dp265&lf;g3&lf;(F2.5444437451708134e-14&lf;F0.0&lf;F0.0&lf;tp266&lf;sg5&lf;(F-1.3920519520020491&lf;F2.2598182327670386&lf;F-0.5667739685873983&lf;tp267&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp268&lf;ssVlowerarm_out_r&lf;p269&lf;(dp270&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp271&lf;sg5&lf;(F-0.6170078789895399&lf;F-1.280766963895374&lf;F-2.1175791102128443&lf;tp272&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp273&lf;ssVankle_bck_r&lf;p274&lf;(dp275&lf;g3&lf;(F-1.8803787149980595e-14&lf;F3.9756933518293936e-15&lf;F-1.1877383888590321e-14&lf;tp276&lf;sg5&lf;(F-0.6507357602611608&lf;F-3.799005098240129&lf;F0.5425226013393445&lf;tp277&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp278&lf;ssVupperarm_bck_r&lf;p279&lf;(dp280&lf;g3&lf;(F-1.631032968523696e-08&lf;F-1.793436243543718e-08&lf;F6.623600521598822e-09&lf;tp281&lf;sg5&lf;(F-1.613973273688245&lf;F-5.899539327146831&lf;F-0.6838130492740362&lf;tp282&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp283&lf;ssVupperarm_bck_l&lf;p284&lf;(dp285&lf;g3&lf;(F-1.631031696301823e-08&lf;F-1.7934362477562443e-08&lf;F6.623600333685193e-09&lf;tp286&lf;sg5&lf;(F1.453320472410553&lf;F5.922331709928633&lf;F0.5193119630590957&lf;tp287&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp288&lf;ssVankle_bck_l&lf;p289&lf;(dp290&lf;g3&lf;(F4.821925894076175e-14&lf;F4.709965190659037e-08&lf;F7.032007635867419e-15&lf;tp291&lf;sg5&lf;(F0.7196897359995171&lf;F3.149843256350702&lf;F-0.1865279959374142&lf;tp292&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp293&lf;ssVlowerarm_fwd_l&lf;p294&lf;(dp295&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp296&lf;sg5&lf;(F1.3286701233338505&lf;F-2.523348037160204&lf;F0.4477197471650243&lf;tp297&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp298&lf;ssVmiddle_01_r&lf;p299&lf;(dp300&lf;g3&lf;(F-2.3854160110976384e-15&lf;F5.665363026356887e-15&lf;F-1.8884543421189624e-14&lf;tp301&lf;sg5&lf;(F-5.182307875635303&lf;F1.2473883217012371e-05&lf;F4.441538994015559e-05&lf;tp302&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp303&lf;ssVcalf_twist_02_l&lf;p304&lf;(dp305&lf;g3&lf;(F-1.2813263656616176e-15&lf;F1.2695893467522358e-18&lf;F-7.368169808403853e-17&lf;tp306&lf;sg5&lf;(F-12.958133997348298&lf;F-0.13437907398599447&lf;F0.11553495636094979&lf;tp307&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp308&lf;ssVlowerarm_twist_01_r&lf;p309&lf;(dp310&lf;g3&lf;(F-1.6743337480238544e-18&lf;F-1.428764306601375e-15&lf;F-1.2424050610833987e-17&lf;tp311&lf;sg5&lf;(F-15.709295982891412&lf;F0.0653041102279559&lf;F0.03263931215387572&lf;tp312&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp313&lf;ssVspine_04_latissimus_r&lf;p314&lf;(dp315&lf;g3&lf;(F-2.1200329155989934e-09&lf;F-2.0738501467058974e-08&lf;F9.430233311509153e-09&lf;tp316&lf;sg5&lf;(F-7.8201672809249345&lf;F3.0343685369015496&lf;F11.943057680552283&lf;tp317&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp318&lf;ssVspine_04_latissimus_l&lf;p319&lf;(dp320&lf;g3&lf;(F5.5057566312661764e-09&lf;F1.6766699921248585e-08&lf;F7.858422271679882e-09&lf;tp321&lf;sg5&lf;(F-7.810114020338162&lf;F3.0346754472192004&lf;F-11.935268925526474&lf;tp322&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp323&lf;ssVlowerarm_twist_01_l&lf;p324&lf;(dp325&lf;g3&lf;(F2.0627063804459095e-16&lf;F1.0062276329226985e-15&lf;F-1.2320628108123222e-17&lf;tp326&lf;sg5&lf;(F15.709011726426546&lf;F-0.06554904986637666&lf;F-0.03229837036940353&lf;tp327&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp328&lf;ssVcalf_twist_02_r&lf;p329&lf;(dp330&lf;g3&lf;(F-1.0969433948738022e-15&lf;F-1.1337156085782787e-17&lf;F-7.38058228600257e-17&lf;tp331&lf;sg5&lf;(F12.958172261711361&lf;F0.13438813926951898&lf;F-0.11546192380812315&lf;tp332&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp333&lf;ssVmiddle_01_l&lf;p334&lf;(dp335&lf;g3&lf;(F-1.5902773407317584e-15&lf;F-2.087239009710433e-15&lf;F2.8966260080954173e-32&lf;tp336&lf;sg5&lf;(F5.182243307643894&lf;F4.263256414560601e-14&lf;F-2.4868995751603507e-14&lf;tp337&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp338&lf;ssVcalf_knee_r&lf;p339&lf;(dp340&lf;g3&lf;(F-9.373939481779854e-15&lf;F-6.433371167720549e-09&lf;F1.1927080056014457e-14&lf;tp341&lf;sg5&lf;(F-0.04499406685729923&lf;F4.304237479045141&lf;F-0.11863616250326992&lf;tp342&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp343&lf;ssVclavicle_scap_r&lf;p344&lf;(dp345&lf;g3&lf;(F-7.2333774824279544e-12&lf;F-5.447464020267169e-09&lf;F2.099599539267737e-08&lf;tp346&lf;sg5&lf;(F-8.497017971073436&lf;F-5.6879741751418536&lf;F2.203234247844506&lf;tp347&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp348&lf;ssVclavicle_pec_l&lf;p349&lf;(dp350&lf;g3&lf;(F5.934906090541604e-09&lf;F-4.328964219255888e-09&lf;F-6.3721458878959175e-09&lf;tp351&lf;sg5&lf;(F-7.859747892191649&lf;F-9.235935633950017&lf;F-9.161680251024567&lf;tp352&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp353&lf;ssVcalf_knee_l&lf;p354&lf;(dp355&lf;g3&lf;(F1.1771779534322956e-14&lf;F-6.4333697762278764e-09&lf;F-6.9574633663623315e-15&lf;tp356&lf;sg5&lf;(F0.04207871964077725&lf;F-4.30754958067433&lf;F0.1160674853346002&lf;tp357&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp358&lf;ssVclavicle_scap_l&lf;p359&lf;(dp360&lf;g3&lf;(F-2.0063835062731552e-11&lf;F-8.936741229731349e-09&lf;F2.0529569357960723e-08&lf;tp361&lf;sg5&lf;(F8.269065264677947&lf;F5.697957688764333&lf;F-2.2342434592936797&lf;tp362&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp363&lf;ssVfoot_r&lf;p364&lf;(dp365&lf;g3&lf;(F3.4942617350063054e-18&lf;F2.2716118211881422e-36&lf;F-7.449571893381498e-17&lf;tp366&lf;sg5&lf;(F38.8683479675059&lf;F4.218847493575595e-15&lf;F-1.7763568394002505e-15&lf;tp367&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp368&lf;ssVupperarm_in_l&lf;p369&lf;(dp370&lf;g3&lf;(F-4.0185802536309686e-10&lf;F-4.683430379560251e-10&lf;F-3.305746816879782e-10&lf;tp371&lf;sg5&lf;(F5.574552996471354&lf;F-1.4832878115397845&lf;F-4.299906325106548&lf;tp372&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp373&lf;ssVlowerarm_out_l&lf;p374&lf;(dp375&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp376&lf;sg5&lf;(F0.5829331297469622&lf;F0.9090844050165288&lf;F1.8502389625441538&lf;tp377&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp378&lf;ssVthumb_02_l&lf;p379&lf;(dp380&lf;g3&lf;(F6.0918383961604464e-33&lf;F7.299124513124281e-17&lf;F9.563794368712256e-15&lf;tp381&lf;sg5&lf;(F4.316671956003702&lf;F0.0&lf;F3.552713678800501e-14&lf;tp382&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp383&lf;ssVankle_fwd_l&lf;p384&lf;(dp385&lf;g3&lf;(F2.4532823392578864e-14&lf;F-3.8486528438178006e-08&lf;F-7.156248041532465e-15&lf;tp386&lf;sg5&lf;(F1.2908153718236504&lf;F-3.768957865912955&lf;F-0.07680916272578031&lf;tp387&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp388&lf;ssVthumb_02_r&lf;p389&lf;(dp390&lf;g3&lf;(F3.975693351829394e-16&lf;F-1.584065319869525e-15&lf;F1.2723383479765737e-14&lf;tp391&lf;sg5&lf;(F-4.316661343859899&lf;F-2.3635732418370026e-05&lf;F-4.3211523554020914e-05&lf;tp392&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp393&lf;ssVindex_metacarpal_l&lf;p394&lf;(dp395&lf;g3&lf;(F-4.708711813572941e-15&lf;F9.939233379573501e-17&lf;F2.4848083448933726e-15&lf;tp396&lf;sg5&lf;(F3.4579468886887668&lf;F0.010562601629231949&lf;F-1.5292670130053594&lf;tp397&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp398&lf;ssVlowerarm_in_l&lf;p399&lf;(dp400&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp401&lf;sg5&lf;(F1.3306420256329048&lf;F0.24547389055802427&lf;F-2.7035021548269356&lf;tp402&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp403&lf;ssVlowerarm_twist_02_r&lf;p404&lf;(dp405&lf;g3&lf;(F-6.721600698588516e-18&lf;F-5.715057220481254e-15&lf;F-3.2583346120769835e-23&lf;tp406&lf;sg5&lf;(F-7.8497274814736855&lf;F0.10257835424635431&lf;F0.03918630802392897&lf;tp407&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp408&lf;ssVcalf_twist_01_l&lf;p409&lf;(dp410&lf;g3&lf;(F-8.492997272584769e-20&lf;F-1.1848489498583718e-23&lf;F-7.454422664982217e-17&lf;tp411&lf;sg5&lf;(F-25.92498684096225&lf;F-0.08807316453161773&lf;F0.10071990957672128&lf;tp412&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp413&lf;ssVupperarm_r&lf;p414&lf;(dp415&lf;g3&lf;(F-1.0933156717530838e-15&lf;F1.2424041724466842e-17&lf;F-1.987846675914698e-15&lf;tp416&lf;sg5&lf;(F-14.246069020159924&lf;F-3.984049673277923e-06&lf;F-0.00038072217765261485&lf;tp417&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp418&lf;ssVcalf_twistCor_02_r&lf;p419&lf;(dp420&lf;g3&lf;(F7.504981906187296e-13&lf;F5.256448295143624e-18&lf;F5.706716964926347e-10&lf;tp421&lf;sg5&lf;(F-1.2789769243681803e-12&lf;F2.353672812205332e-14&lf;F0.0&lf;tp422&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp423&lf;ssVthigh_bck_l&lf;p424&lf;(dp425&lf;g3&lf;(F-3.3281960298549105e-10&lf;F7.492530405354367e-09&lf;F-1.1907707579416888e-10&lf;tp426&lf;sg5&lf;(F3.5690050994295888&lf;F10.405499415408876&lf;F2.1497621859770657&lf;tp427&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp428&lf;ssVindex_02_l&lf;p429&lf;(dp430&lf;g3&lf;(F-3.727212517340059e-17&lf;F3.8825130388958945e-18&lf;F-7.279711947929802e-20&lf;tp431&lf;sg5&lf;(F4.25400585260217&lf;F-2.842170943040401e-14&lf;F-7.105427357601002e-15&lf;tp432&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp433&lf;ssVthigh_bck_r&lf;p434&lf;(dp435&lf;g3&lf;(F4.547938750138404e-10&lf;F1.2473182494297477e-09&lf;F1.8459230383879978e-10&lf;tp436&lf;sg5&lf;(F-3.570662230365997&lf;F-10.412042020771928&lf;F-2.17580140441963&lf;tp437&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp438&lf;ssVindex_02_r&lf;p439&lf;(dp440&lf;g3&lf;(F-3.727212517340059e-17&lf;F3.1060104311167156e-18&lf;F-8.492997272584769e-20&lf;tp441&lf;sg5&lf;(F-4.254001839627506&lf;F2.1309285713755344e-05&lf;F8.939731338131196e-05&lf;tp442&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp443&lf;ssVneck_02&lf;p444&lf;(dp445&lf;g3&lf;(F-2.426570649309934e-19&lf;F-3.727212517340059e-17&lf;F2.84363747966008e-22&lf;tp446&lf;sg5&lf;(F5.450919182046334&lf;F1.4210854715202004e-14&lf;F1.3086753902769033e-14&lf;tp447&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp448&lf;ssVneck_01&lf;p449&lf;(dp450&lf;g3&lf;(F3.1060104311167156e-18&lf;F-1.941256519447947e-18&lf;F-9.541663760026802e-15&lf;tp451&lf;sg5&lf;(F11.10442132885018&lf;F1.4210854715202004e-14&lf;F1.2705114738054135e-14&lf;tp452&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp453&lf;ssVcalf_twist_01_r&lf;p454&lf;(dp455&lf;g3&lf;(F-6.066426623274834e-20&lf;F-1.2424077269935359e-17&lf;F-7.454424442255643e-17&lf;tp456&lf;sg5&lf;(F25.925076009789063&lf;F0.08808086210734589&lf;F-0.10067777201496497&lf;tp457&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp458&lf;ssVupperarm_l&lf;p459&lf;(dp460&lf;g3&lf;(F-3.578124016646457e-15&lf;F-7.454425034680119e-17&lf;F-3.975693351829396e-16&lf;tp461&lf;sg5&lf;(F14.246126391528867&lf;F3.9968028886505635e-15&lf;F-2.842170943040401e-14&lf;tp462&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp463&lf;ssVlowerarm_twist_02_l&lf;p464&lf;(dp465&lf;g3&lf;(F8.251007514582334e-16&lf;F4.01248648404208e-15&lf;F-4.9282568712817974e-17&lf;tp466&lf;sg5&lf;(F7.849649281922929&lf;F-0.10263520133286619&lf;F-0.039097261663499694&lf;tp467&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp468&lf;ssVhead&lf;p469&lf;(dp470&lf;g3&lf;(F-4.6590156466750695e-18&lf;F5.056973233161904e-17&lf;F1.113193759360567e-14&lf;tp471&lf;sg5&lf;(F5.366716115241388&lf;F-7.105427357601002e-15&lf;F3.309852392163748e-14&lf;tp472&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp473&lf;ssVthigh_twist_02_l&lf;p474&lf;(dp475&lf;g3&lf;(F-9.220968467377749e-16&lf;F-4.926728712348722e-17&lf;F2.279365015779531e-18&lf;tp476&lf;sg5&lf;(F-28.47903032534198&lf;F0.17386366818659837&lf;F0.0056687508871462455&lf;tp477&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp478&lf;ssVthigh_fwd_lwr_r&lf;p479&lf;(dp480&lf;g3&lf;(F-2.5444437451708134e-14&lf;F0.0&lf;F0.0&lf;tp481&lf;sg5&lf;(F-0.4782982245318834&lf;F6.809431755534755&lf;F-0.7662289287193396&lf;tp482&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp483&lf;ssVring_metacarpal_r&lf;p484&lf;(dp485&lf;g3&lf;(F-6.957463365701443e-16&lf;F4.969616689786745e-16&lf;F-3.1805546814635168e-15&lf;tp486&lf;sg5&lf;(F-2.804780390195006&lf;F-0.22716314349776212&lf;F-1.059677422149715&lf;tp487&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp488&lf;ssVpinky_03_l&lf;p489&lf;(dp490&lf;g3&lf;(F-1.1647539116687691e-18&lf;F3.7344922292879887e-17&lf;F-2.385414873642646e-15&lf;tp491&lf;sg5&lf;(F1.6696361810729314&lf;F-4.973799150320701e-14&lf;F7.105427357601002e-15&lf;tp492&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp493&lf;ssVlowerarm_r&lf;p494&lf;(dp495&lf;g3&lf;(F-1.1181637552020177e-16&lf;F1.2734642767578534e-16&lf;F1.2132853246549658e-19&lf;tp496&lf;sg5&lf;(F-25.246899842795102&lf;F2.8223703232299613e-05&lf;F-0.0003521030096464983&lf;tp497&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp498&lf;ssVpinky_01_r&lf;p499&lf;(dp500&lf;g3&lf;(F1.7393658414253607e-16&lf;F-1.8636062586700284e-17&lf;F-6.359944609015365e-15&lf;tp501&lf;sg5&lf;(F-4.397007478658836&lf;F-4.320010107505823e-05&lf;F-2.742241442632576e-05&lf;tp502&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp503&lf;ssVthigh_twist_01_r&lf;p504&lf;(dp505&lf;g3&lf;(F-2.4265706493099345e-18&lf;F-4.9695017594386094e-17&lf;F1.2430155545048131e-17&lf;tp506&lf;sg5&lf;(F14.287114027195173&lf;F-0.2111677104455696&lf;F-0.0656104539200193&lf;tp507&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp508&lf;ssVclavicle_pec_r&lf;p509&lf;(dp510&lf;g3&lf;(F9.293300890747829e-09&lf;F-5.707670764203161e-09&lf;F-6.492766834151767e-09&lf;tp511&lf;sg5&lf;(F-7.865587754738414&lf;F-9.462906268526464&lf;F9.48653599414189&lf;tp512&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp513&lf;ssVpinky_01_l&lf;p514&lf;(dp515&lf;g3&lf;(F2.4848083448933823e-17&lf;F-1.0094533901129326e-15&lf;F-1.113038837990675e-14&lf;tp516&lf;sg5&lf;(F4.3969685310509234&lf;F-1.4210854715202004e-14&lf;F-6.039613253960852e-14&lf;tp517&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp518&lf;ssVthigh_twist_01_l&lf;p519&lf;(dp520&lf;g3&lf;(F-2.4209895368165213e-16&lf;F-4.9583558853672917e-17&lf;F6.810511763785889e-18&lf;tp521&lf;sg5&lf;(F-14.287183632223432&lf;F0.21116362092060248&lf;F0.06561795810833893&lf;tp522&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp523&lf;ssVlowerarm_l&lf;p524&lf;(dp525&lf;g3&lf;(F-7.454425034680117e-17&lf;F8.386228164015132e-17&lf;F7.279711947929797e-20&lf;tp526&lf;sg5&lf;(F25.247300689778797&lf;F-5.329070518200751e-15&lf;F-4.263256414560601e-14&lf;tp527&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp528&lf;ssVpinky_03_r&lf;p529&lf;(dp530&lf;g3&lf;(F3.8825130388958945e-19&lf;F1.2436174577713411e-17&lf;F3.791516639546773e-22&lf;tp531&lf;sg5&lf;(F-1.669605250518572&lf;F-8.182164268788483e-05&lf;F-2.731165606206787e-05&lf;tp532&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp533&lf;ssVthigh_fwd_lwr_l&lf;p534&lf;(dp535&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp536&lf;sg5&lf;(F0.39812935021383566&lf;F-7.309934383244445&lf;F0.6883540989376549&lf;tp537&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp538&lf;ssVring_metacarpal_l&lf;p539&lf;(dp540&lf;g3&lf;(F1.2827915178708273e-31&lf;F-6.1623246953355635e-15&lf;F-2.3854160110976376e-15&lf;tp541&lf;sg5&lf;(F2.8047746330326007&lf;F0.22714913893837263&lf;F1.0596930230372124&lf;tp542&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp543&lf;ssVlowerarm_bck_r&lf;p544&lf;(dp545&lf;g3&lf;(F2.5444437451708134e-14&lf;F1.821991149690184e-07&lf;F7.600179899673703e-23&lf;tp546&lf;sg5&lf;(F-1.5862762297890214&lf;F-3.40166381371057&lf;F0.8892462340683522&lf;tp547&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp548&lf;ssVlowerarm_correctiveRoot_l&lf;p549&lf;(dp550&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp551&lf;sg5&lf;(F-3.552713678800501e-14&lf;F0.0&lf;F-5.684341886080802e-14&lf;tp552&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp553&lf;ssVpinky_02_l&lf;p554&lf;(dp555&lf;g3&lf;(F1.8636062586700294e-17&lf;F-7.76502607779179e-18&lf;F1.2722218725854067e-14&lf;tp556&lf;sg5&lf;(F2.6964561558300915&lf;F2.842170943040401e-14&lf;F3.552713678800501e-15&lf;tp557&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp558&lf;ssVcalf_twistCor_02_l&lf;p559&lf;(dp560&lf;g3&lf;(F7.786203609148045e-13&lf;F2.2381283947562397e-18&lf;F5.706716775610707e-10&lf;tp561&lf;sg5&lf;(F1.2931877790833823e-12&lf;F-2.3092638912203256e-14&lf;F-5.329070518200751e-15&lf;tp562&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp563&lf;ssVlowerarm_correctiveRoot_r&lf;p564&lf;(dp565&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp566&lf;sg5&lf;(F3.552713678800501e-14&lf;F0.0&lf;F-1.4210854715202004e-14&lf;tp567&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp568&lf;ssVpelvis&lf;p569&lf;(dp570&lf;g3&lf;(F-8.746525374024675e-15&lf;F1.9369081048443843e-14&lf;F-8.348956038841735e-15&lf;tp571&lf;sg5&lf;(F0.00010491341864091094&lf;F-2.2175793100900107&lf;F91.97877241348029&lf;tp572&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp573&lf;ssVlowerarm_bck_l&lf;p574&lf;(dp575&lf;g3&lf;(F0.0&lf;F1.821991149690184e-07&lf;F0.0&lf;tp576&lf;sg5&lf;(F1.3859786452671514&lf;F3.3413824665105096&lf;F-1.1761296577728615&lf;tp577&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp578&lf;ssVthigh_in_r&lf;p579&lf;(dp580&lf;g3&lf;(F-1.799777415242335e-11&lf;F1.7811260677643742e-08&lf;F-1.1301263803149778e-08&lf;tp581&lf;sg5&lf;(F9.68590753589298&lf;F0.7278592457790922&lf;F-8.591039347640994&lf;tp582&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp583&lf;ssVindex_01_l&lf;p584&lf;(dp585&lf;g3&lf;(F5.367186024969684e-15&lf;F-1.5902773407317588e-15&lf;F9.442271710594815e-15&lf;tp586&lf;sg5&lf;(F5.011096571254832&lf;F-4.263256414560601e-14&lf;F-3.552713678800501e-14&lf;tp587&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp588&lf;ssVupperarm_tricep_r&lf;p589&lf;(dp590&lf;g3&lf;(F3.7924387363587275e-14&lf;F6.075963094069785e-09&lf;F-6.5598940285076466e-15&lf;tp591&lf;sg5&lf;(F-0.2668024100145914&lf;F-4.4614700865646535&lf;F-0.06149644816963473&lf;tp592&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp593&lf;ssVthigh_twistCor_02_l&lf;p594&lf;(dp595&lf;g3&lf;(F-9.700266400628902e-13&lf;F4.420414151584964e-17&lf;F-1.9859764446290498e-10&lf;tp596&lf;sg5&lf;(F6.039613253960852e-13&lf;F1.8474111129762605e-13&lf;F-7.105427357601002e-15&lf;tp597&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp598&lf;ssVindex_03_r&lf;p599&lf;(dp600&lf;g3&lf;(F-4.549819967456126e-21&lf;F1.849846171874749e-40&lf;F4.659014165613886e-18&lf;tp601&lf;sg5&lf;(F-2.317379606058509&lf;F-3.482151544176304e-05&lf;F-1.4542190249322573e-05&lf;tp602&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp603&lf;ssVwrist_outer_r&lf;p604&lf;(dp605&lf;g3&lf;(F-2.5456861493432594e-14&lf;F-3.379339349054985e-15&lf;F3.1805546814635168e-15&lf;tp606&lf;sg5&lf;(F-0.03274741621405042&lf;F1.6563393407212317&lf;F0.025852490706835596&lf;tp607&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp608&lf;ssVwrist_outer_l&lf;p609&lf;(dp610&lf;g3&lf;(F-5.783391422739323e-14&lf;F9.34287937679908e-15&lf;F4.373262687012329e-15&lf;tp611&lf;sg5&lf;(F-0.03377910590610611&lf;F-1.4964501513575073&lf;F-0.18007976338952147&lf;tp612&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp613&lf;ssVpinky_metacarpal_r&lf;p614&lf;(dp615&lf;g3&lf;(F1.3914926731402885e-14&lf;F-1.5902773407317588e-15&lf;F1.5902773407317582e-15&lf;tp616&lf;sg5&lf;(F-2.558789946909897&lf;F-0.5003207482651391&lf;F-2.0640128067549632&lf;tp617&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp618&lf;ssVupperarm_tricep_l&lf;p619&lf;(dp620&lf;g3&lf;(F1.2424042072290844e-17&lf;F6.0759658770551315e-09&lf;F6.5598940305191614e-15&lf;tp621&lf;sg5&lf;(F0.11027252258691078&lf;F4.4684969383725015&lf;F-0.13297608266564964&lf;tp622&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp623&lf;ssVthigh_twistCor_02_r&lf;p624&lf;(dp625&lf;g3&lf;(F-9.971666437558038e-13&lf;F7.130715464304176e-18&lf;F-1.9859764570803904e-10&lf;tp626&lf;sg5&lf;(F-6.252776074688882e-13&lf;F-1.829647544582258e-13&lf;F7.105427357601002e-15&lf;tp627&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp628&lf;ssVindex_01_r&lf;p629&lf;(dp630&lf;g3&lf;(F-1.987846675914698e-16&lf;F-1.7241821476758432e-34&lf;F-9.93923337957349e-17&lf;tp631&lf;sg5&lf;(F-5.011125795495047&lf;F1.255617310391699e-05&lf;F-3.957483904848402e-05&lf;tp632&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp633&lf;ssVthigh_in_l&lf;p634&lf;(dp635&lf;g3&lf;(F7.81972953015046e-10&lf;F1.783717115280913e-08&lf;F2.898665566940874e-09&lf;tp636&lf;sg5&lf;(F-9.624813217005851&lf;F-0.7872489589315337&lf;F8.569114048741081&lf;tp637&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp638&lf;ssVmiddle_metacarpal_l&lf;p639&lf;(dp640&lf;g3&lf;(F5.168401357378214e-15&lf;F4.721135855297406e-15&lf;F6.162324695335562e-15&lf;tp641&lf;sg5&lf;(F2.9473948030703525&lf;F-1.4210854715202004e-14&lf;F2.4868995751603507e-14&lf;tp642&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp643&lf;ssVring_01_r&lf;p644&lf;(dp645&lf;g3&lf;(F3.7272125173400585e-16&lf;F-9.939233379573484e-17&lf;F-1.90833280887811e-14&lf;tp646&lf;sg5&lf;(F-4.653074699202811&lf;F-2.4532645610975123e-05&lf;F5.51067713736586e-05&lf;tp647&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp648&lf;ssVupperarm_correctiveRoot_r&lf;p649&lf;(dp650&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp651&lf;sg5&lf;(F1.4210854715202004e-14&lf;F-4.440892098500626e-15&lf;F2.842170943040401e-14&lf;tp652&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp653&lf;ssVcalf_kneeBack_l&lf;p654&lf;(dp655&lf;g3&lf;(F8.63470899849898e-15&lf;F-9.039156283186074e-11&lf;F6.957463365694632e-15&lf;tp656&lf;sg5&lf;(F0.2417278422375233&lf;F4.878562416091983&lf;F0.29022114718005376&lf;tp657&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp658&lf;ssVcalf_kneeBack_r&lf;p659&lf;(dp660&lf;g3&lf;(F-2.35124989635446e-14&lf;F-9.039096647785796e-11&lf;F-1.1330726052695231e-14&lf;tp661&lf;sg5&lf;(F-0.2449349235955367&lf;F-4.883272954147831&lf;F-0.3136576664737962&lf;tp662&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp663&lf;ssVring_01_l&lf;p664&lf;(dp665&lf;g3&lf;(F3.354491265606054e-16&lf;F-3.975693351829396e-16&lf;F-1.9084881093996662e-14&lf;tp666&lf;sg5&lf;(F4.653086398712624&lf;F4.263256414560601e-14&lf;F-1.0658141036401503e-14&lf;tp667&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp668&lf;ssVupperarm_correctiveRoot_l&lf;p669&lf;(dp670&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp671&lf;sg5&lf;(F2.842170943040401e-14&lf;F0.0&lf;F1.4210854715202004e-14&lf;tp672&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp673&lf;ssVmiddle_metacarpal_r&lf;p674&lf;(dp675&lf;g3&lf;(F2.5842006786891076e-15&lf;F3.0811623476677818e-15&lf;F4.721135855297408e-15&lf;tp676&lf;sg5&lf;(F-2.9473407769463975&lf;F-3.6594834583070224e-05&lf;F5.6656297143575785e-05&lf;tp677&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp678&lf;ssVthigh_twist_02_r&lf;p679&lf;(dp680&lf;g3&lf;(F7.939739164542105e-16&lf;F-5.006542507309081e-17&lf;F1.0461552711837454e-17&lf;tp681&lf;sg5&lf;(F28.47895122626658&lf;F-0.17387919837305565&lf;F-0.005720635786287787&lf;tp682&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp683&lf;ssVring_03_r&lf;p684&lf;(dp685&lf;g3&lf;(F-3.1060104311167156e-18&lf;F-1.9897879324341458e-16&lf;F-4.2464986362923846e-20&lf;tp686&lf;sg5&lf;(F-3.0146802324974686&lf;F-4.5867904766794254e-05&lf;F6.070594956142372e-05&lf;tp687&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp688&lf;ssVupperarm_fwd_r&lf;p689&lf;(dp690&lf;g3&lf;(F2.5414619751459016e-11&lf;F-1.8553765734468644e-11&lf;F6.818250487293744e-10&lf;tp691&lf;sg5&lf;(F-3.1383986238786576&lf;F6.085192473500279&lf;F0.3701752564989107&lf;tp692&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp693&lf;ssVcalf_r&lf;p694&lf;(dp695&lf;g3&lf;(F7.765026077791785e-19&lf;F-7.453211749355463e-17&lf;F5.963577942910489e-16&lf;tp696&lf;sg5&lf;(F42.6392716823317&lf;F-1.7763568394002505e-15&lf;F1.2434497875801753e-14&lf;tp697&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp698&lf;ssVupperarm_twistCor_02_r&lf;p699&lf;(dp700&lf;g3&lf;(F-5.7155154104789345e-05&lf;F0.2392973804678591&lf;F-0.01368489098937418&lf;tp701&lf;sg5&lf;(F-4.263256414560601e-14&lf;F7.105427357601002e-15&lf;F5.684341886080802e-14&lf;tp702&lf;sg7&lf;(F0.9999999999999997&lf;F1.0&lf;F0.9999999999999998&lf;tp703&lf;ssVmiddle_02_r&lf;p704&lf;(dp705&lf;g3&lf;(F-7.45442503468011e-17&lf;F4.080521203879585e-16&lf;F2.2263640113179687e-14&lf;tp706&lf;sg5&lf;(F-4.584910207198277&lf;F-3.1438676543871225e-05&lf;F-3.066261484363508e-05&lf;tp707&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp708&lf;ssVpinky_metacarpal_l&lf;p709&lf;(dp710&lf;g3&lf;(F-3.180554681463515e-15&lf;F1.3318572728628474e-14&lf;F3.180554681463515e-15&lf;tp711&lf;sg5&lf;(F2.558828022670248&lf;F0.5003618244700903&lf;F2.064049345253842&lf;tp712&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp713&lf;ssVthigh_r&lf;p714&lf;(dp715&lf;g3&lf;(F-3.620782510119271e-33&lf;F-2.3854160110976376e-15&lf;F1.7393658414253607e-16&lf;tp716&lf;sg5&lf;(F-3.012337184531063&lf;F-0.06336612202783964&lf;F10.395765560224552&lf;tp717&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp718&lf;ssVmiddle_02_l&lf;p719&lf;(dp720&lf;g3&lf;(F-8.696829207126799e-17&lf;F4.158171464657503e-16&lf;F1.9082854907504484e-14&lf;tp721&lf;sg5&lf;(F4.58496782082122&lf;F-1.4210854715202004e-14&lf;F-2.842170943040401e-14&lf;tp722&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp723&lf;ssVpinky_02_r&lf;p724&lf;(dp725&lf;g3&lf;(F1.2424041724466862e-17&lf;F-7.765026077791789e-17&lf;F-9.706282597239736e-20&lf;tp726&lf;sg5&lf;(F-2.696477533033118&lf;F3.068206100920179e-05&lf;F5.3911045487353704e-05&lf;tp727&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp728&lf;ssVupperarm_twistCor_02_l&lf;p729&lf;(dp730&lf;g3&lf;(F-5.715515410377221e-05&lf;F0.23929738046881302&lf;F-0.013684890989438625&lf;tp731&lf;sg5&lf;(F8.526512829121202e-14&lf;F7.105427357601002e-15&lf;F-4.263256414560601e-14&lf;tp732&lf;sg7&lf;(F0.9999999999999999&lf;F1.0&lf;F0.9999999999999999&lf;tp733&lf;ssVcalf_l&lf;p734&lf;(dp735&lf;g3&lf;(F2.717759127227125e-18&lf;F-7.451998464030805e-17&lf;F5.963555193810652e-16&lf;tp736&lf;sg5&lf;(F-42.63936190162267&lf;F-7.829074149423576e-06&lf;F-4.4586872256502375e-05&lf;tp737&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp738&lf;ssVring_03_l&lf;p739&lf;(dp740&lf;g3&lf;(F0.0&lf;F0.0&lf;F0.0&lf;tp741&lf;sg5&lf;(F3.0147511882823608&lf;F-4.973799150320701e-14&lf;F-1.0658141036401503e-14&lf;tp742&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp743&lf;ssVupperarm_fwd_l&lf;p744&lf;(dp745&lf;g3&lf;(F2.5408755603765092e-11&lf;F-1.8548994902446404e-11&lf;F6.818210730360224e-10&lf;tp746&lf;sg5&lf;(F2.998532437400442&lf;F-6.078429423751953&lf;F-0.5550002675375794&lf;tp747&lf;sg7&lf;(F1.0&lf;F1.0&lf;F1.0&lf;tp748&lf;ss.");
	setAttr ".fbxID" 2;
createNode joint -n "cloth_pelvis" -p "cloth_root";
	rename -uid "D942DDCF-4680-3B98-856B-5683233D4432";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" -3.4314998759166197e-17 -2.280866146087646 95.896781921386719 ;
	setAttr ".r" -type "double3" 90 -93.633106949967612 -90 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0 0.99799027986901845 -0.063367194090933832 0 0 -0.063367194090933832 -0.99799027986901856 0
		 -1 0 0 0 -3.4314998759166197e-17 95.896781921386719 2.280866146087646 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_spine_01" -p "cloth_pelvis";
	rename -uid "FC909550-45FE-61B7-B798-8A8EA435CA87";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" 3.6770534515378444 3.1974423109204508e-14 -4.6633694517662523e-16 ;
	setAttr ".r" -type "double3" 0 0 -14.457321828304899 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999967 0.99999999999999989 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0 0.98220797016103378 0.18779644126591263 0 0 0.18779644126591258 -0.98220797016103367 0
		 -0.99999999999999989 0 0 0 4.3202194641745901e-16 99.566445524580317 2.0478615863412775 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_spine_02" -p "cloth_spine_01";
	rename -uid "1E386F4D-4D1F-1DF0-82E2-2983ED9B50FA";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 6.7950572967531286 9.5923269327613525e-14 1.8559423937126041e-16 ;
	setAttr ".r" -type "double3" 0 0 3.464469508424771 ;
	setAttr ".s" -type "double3" 1.0000000000000004 1 1 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0 0.99176140629857201 0.12809884065314286 0 0 0.12809884065314273 -0.99176140629857146 0
		 -0.99999999999999989 0 0 0 2.4642770704619865e-16 106.24060495915215 3.3239491648693935 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_spine_03" -p "cloth_spine_02";
	rename -uid "EF6F96A7-4D7E-D06C-671C-B8AFEFB32510";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 7.2382278442387076 -8.8817841970012523e-15 1.2292061026365013e-16 ;
	setAttr ".r" -type "double3" 0 0 10.946079405533517 ;
	setAttr ".s" -type "double3" 1 0.99999999999999978 1.0000000000000002 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0 0.99804167658749543 -0.062552472328610637 0 0 -0.062552472328610859 -0.99804167658749476 0
		 -1 0 0 0 1.2350709678254855e-16 113.41919998506381 4.2511577600996784 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_spine_04" -p "cloth_spine_03";
	rename -uid "79BDFEF6-4077-1CFC-1F41-F0B7C0456169";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" 8.5238933563226453 5.8619775700208265e-14 2.5231056665821328e-16 ;
	setAttr ".r" -type "double3" 0.00044952872060361214 3.0332133116374176e-21 5.8669839318741621 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999933 1.0000000000000007 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 1.0587911840678751e-22 0.98641974755132811 -0.16424396987644307 0
		 -7.8457562567302043e-06 -0.16424396987138823 -0.98641974752096717 0 -0.99999999996922273 1.288618154288315e-06 7.7392089061130656e-06 0
		 -1.2880346987566473e-16 121.92640080146107 3.7179671567962194 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_spine_05" -p "cloth_spine_04";
	rename -uid "F5C2F3E0-4C48-FCA5-43AB-67BD884F5E61";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "blendParent1" -ln "blendParent1" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" 19.439800262451271 -1.7817315978163606e-07 8.113023057185198e-13 ;
	setAttr ".r" -type "double3" -0.00044949784299974259 5.3458783320776006e-06 0.68138935939440159 ;
	setAttr ".s" -type "double3" 0.99999999999999911 1 1.0000000000000013 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -1.829647540611791e-13 0.98439676970875611 -0.17596306370077827 0
		 1.5895229593952719e-11 -0.17596306370077869 -0.984396769708756 0 -1.000000000000002 -2.9770832073280402e-12 -1.5615017611930542e-11 0
		 5.8647207603300461e-13 141.10220369806035 0.52509736383962569 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".blendParent1" -type "string" "1.000000";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_neck_01" -p "cloth_spine_05";
	rename -uid "388B9326-4635-94A9-740C-6ABD9DAA1EC4";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 7;
	setAttr ".t" -type "double3" 11.887765884399784 0 2.6319229856308895e-10 ;
	setAttr ".r" -type "double3" 0 0 -23.928404052334635 ;
	setAttr ".s" -type "double3" 0.99999999999999933 1.0000000000000013 1.0000000000000016 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -6.6142615222588202e-12 0.97116051578906593 0.23842661884175742 0
		 1.4454872689196054e-11 0.23842661884175756 -0.97116051578906759 0 -1.0000000000000036 -2.9770832073280446e-12 -1.5615017611930568e-11 0
		 -2.6478086864843252e-10 152.80448203371745 -1.5667103417369521 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_neck_02" -p "cloth_neck_01";
	rename -uid "E026ECEE-40A8-19DE-DED2-A3820CDC4F0B";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".t" -type "double3" 5.1102595329284384 -6.3948846218409017e-14 -4.1190754660921805e-14 ;
	setAttr ".r" -type "double3" -9.7964785669111407e-05 1.895758319773386e-22 1.9135286365136512 ;
	setAttr ".s" -type "double3" 1 0.99999999999999989 1 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -6.1279080757366205e-12 0.97858030038111066 0.20586547963661234 0
		 1.7098227286057003e-06 0.20586547963631158 -0.9785803003796818 0 -0.99999999999854183 3.5198747946787048e-07 -1.6732001008821332e-06 0
		 -2.985402708911774e-10 157.76736431753221 -0.34828843989690395 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_head" -p "cloth_neck_02";
	rename -uid "78AC3270-446C-0B1A-7564-36AF013939C4";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" 4.9129710197449299 -7.1054273576010019e-14 7.8960811457015612e-10 ;
	setAttr ".r" -type "double3" 9.5866408829364331e-05 -2.0167570239287175e-05 11.880169672716002 ;
	setAttr ".s" -type "double3" 0.999999999999997 1.0000000000000016 0.99999999999999967 ;
	setAttr ".dla" yes;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -2.9770827775646986e-12 0.99999961746090582 1.82437533464403e-07 0
		 1.5615017701927793e-11 1.8243753418557276e-07 -0.9999996174609127 0 -1.0000000000000033 -2.977078786716028e-12 -1.5615012254447151e-11 0
		 -1.1182548667971345e-09 162.57508002348578 0.6631353833000988 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_clavicle_l" -p "cloth_spine_05";
	rename -uid "4486315F-4E37-97C1-2150-2D9A83CC9A34";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "blendParent1" -ln "blendParent1" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 7;
	setAttr ".t" -type "double3" 5.5162687301644269 1.314766049384982 -1.4279042482530175 ;
	setAttr ".r" -type "double3" -16.736414880536611 99.168774102490772 -26.875616334153221 ;
	setAttr ".s" -type "double3" 1.0000000000000004 1.0000000000000002 0.99999999999999944 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.98722325287428303 -0.15258975006428871 -0.045897899294439624 0
		 -0.045885930423861222 0.0036018072398125499 -0.99894019259099887 0 0.15259334970260416 0.9882830541701717 -0.0034459347953300487 0
		 1.427904248273496 146.30105055478433 -1.7398136340319308 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".blendParent1" -type "string" "1.000000";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_upperarm_l" -p "cloth_clavicle_l";
	rename -uid "6368C074-41B0-8C1A-FC39-59A1EB49D167";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "blendParent1" -ln "blendParent1" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".t" -type "double3" 17.809522630964835 2.0104433673395761e-09 -9.8569330475584138e-09 ;
	setAttr ".r" -type "double3" -4.3373453941524289 46.029604231526136 -4.3585188196119882 ;
	setAttr ".s" -type "double3" 1.0000000000000007 1.0000000000000004 0.99999999999999922 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.57603356952398899 -0.8170906446104228 0.023413783794530126 0
		 -0.032592099667534707 -0.051578496259220549 -0.99813697144374836 0 0.81677602916633019 0.57419729815957765 -0.056341645037431158 0
		 19.009879110556408 143.5834999380269 -2.5572333122043447 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".blendParent1" -type "string" "1.000000";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_lowerarm_l" -p "cloth_upperarm_l";
	rename -uid "28CE3AB5-4AC2-E755-66E4-FABA848A3BFF";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" 27.771139141657898 2.9752040830999249e-09 -2.0293100533308461e-11 ;
	setAttr ".r" -type "double3" 1.5379129913322994e-13 2.9039300422364665e-09 -38.978821942126636 ;
	setAttr ".s" -type "double3" 0.99999999999999778 0.99999999999999978 1.0000000000000027 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.46829763423518478 -0.60274413661567139 0.64606256008621465 0
		 0.33700778024997413 -0.55407307150020002 -0.76120219882060192 0 0.81677602916633241 0.57419729815957921 -0.056341645037431311 0
		 35.006987519959431 120.89196195503879 -1.9070058675822716 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_lowerarm_twist_02_l" -p "cloth_lowerarm_l";
	rename -uid "F1B0481D-4363-639F-7F1F-D3951EF019C0";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" 9.0836915969845577 2.7711166694643907e-13 -7.1054273576010019e-14 ;
	setAttr ".r" -type "double3" 1.2856753636117328 -1.7275330717196193 1.9858281262409585 ;
	setAttr ".s" -type "double3" 0.99999999999999567 1 1.0000000000000022 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.50409945374199816 -0.60398964764526486 0.61731736600229226 0
		 0.33849060588977736 -0.51942179398053145 -0.78461817740898399 0 0.7945488345352959 0.60448172387231192 -0.057395420824676004 0
		 39.260858804949336 115.41682076717704 3.9616273117874452 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_lowerarm_twist_01_l" -p "cloth_lowerarm_l";
	rename -uid "DDC6B461-48A6-85F0-8C0A-75A6886CBFC6";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" 18.167383193969414 1.8474111129762605e-13 -8.5265128291212022e-14 ;
	setAttr ".r" -type "double3" 1.2856753621314321 -1.7275254942412186 1.9858282116666979 ;
	setAttr ".s" -type "double3" 0.99999999999999567 1 1.0000000000000022 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.504099348161136 -0.60398972682179586 0.61731737475220905 0
		 0.33849060664975905 -0.51942179486136186 -0.78461817649800658 0 0.7945489011970267 0.60448164400333959 -0.057395339168168191 0
		 43.514730089939327 109.94167718488202 9.8302623048443163 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_hand_l" -p "cloth_lowerarm_l";
	rename -uid "4538F88C-4F7E-727C-F097-4A9C5F2514EA";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" 27.251073837279936 1.9184653865522705e-13 -8.5265128291212022e-14 ;
	setAttr ".r" -type "double3" -67.770758831993689 1.4734712640021723 1.8489164332192987 ;
	setAttr ".s" -type "double3" 0.99999999999999745 1.0000000000000007 1.0000000000000029 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.45776605878178878 -0.63486684214115308 0.62241009646140766 0
		 -0.6455090492760025 -0.71872770835154665 -0.25835740467524998 0 0.61136593193453992 -0.28350409873130777 -0.73882144207675005 0
		 47.768600928325959 104.46653698313743 15.698892660829127 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_metacarpal_l" -p "cloth_hand_l";
	rename -uid "E7FEC1A7-4ABD-BD4F-F8B5-4B8A0989DDB3";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 3.444506168480391 -0.38468081624374406 -2.3793244397218665 ;
	setAttr ".r" -type "double3" 3.2877464944600794 7.3255016776270905 -0.60616239441687825 ;
	setAttr ".s" -type "double3" 0.99999999999999489 1.000000000000002 1.0000000000000031 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.3828247102713212 -0.58595975173661574 0.71421064405449275 0
		 -0.6014025057542387 -0.74492322350988671 -0.28879879051776403 0 0.7012562066319028 -0.31896875765200255 -0.6375726801790027 0
		 48.139055987552858 103.23075848426039 19.700072811376138 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_01_l" -p "cloth_index_metacarpal_l";
	rename -uid "7E644518-4E29-245C-A7F6-52A01FBE1B59";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 5.8770980834961932 0.043181736022205541 0.24087569117548924 ;
	setAttr ".r" -type "double3" -1.3429259284809103e-14 -1.3462918630465948e-13 23.372999658581023 ;
	setAttr ".s" -type "double3" 0.99999999999999389 1.0000000000000016 1.0000000000000049 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.11282514553323686 -0.83339937934376607 0.541032703758897 0
		 -0.70392486769285179 -0.4513367723982652 -0.54843879872664192 0 0.70125620651728926 -0.31896868712858517 -0.63757268487021534 0
		 50.531900323176821 99.678011313594297 23.73150791658631 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_02_l" -p "cloth_index_01_l";
	rename -uid "0D258B8C-41ED-A31E-6A07-AE8064F05B85";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" 4.0799999237060618 5.6843418860808015e-14 -3.1974423109204508e-14 ;
	setAttr ".r" -type "double3" -5.0951279423058275e-14 -1.2226045108180672e-13 14.892568419110622 ;
	setAttr ".s" -type "double3" 0.99999999999998967 1.0000000000000058 1.0000000000000044 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.071878367801288007 -0.92140161924435326 0.3819062551786333 0
		 -0.70927619093516969 -0.2219861663449483 -0.66906557912387488 0 0.70125614179952289 -0.31896891263821953 -0.63757233185344964 0
		 50.992225061720788 96.277745298420271 25.938920259541064 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_03_l" -p "cloth_index_02_l";
	rename -uid "D430AD98-42D0-D1C6-2A1C-319E18A89070";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" 2.5950000286102863 2.8421709430404007e-14 -7.1054273576010019e-14 ;
	setAttr ".r" -type "double3" -6.581298975385556e-14 -1.1982479697484097e-13 12.516400997546848 ;
	setAttr ".s" -type "double3" 0.99999999999998501 1.0000000000000131 1.0000000000000009 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.22388381388581446 -0.94761237257265629 0.22783043025352478 0
		 -0.67684263984381676 -0.017024814707322311 -0.7359310234528964 0 0.7012563918308613 -0.31896894172254714 -0.63757264406503988 0
		 50.805730274602958 93.886692134559155 26.92996282235223 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_metacarpal_l" -p "cloth_hand_l";
	rename -uid "F5596357-4DBA-9A6A-73A0-B4992388FD08";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 3.3758335117435294 -0.75357074676698232 -0.18286437211174444 ;
	setAttr ".r" -type "double3" -4.2725002624341881 -0.13075113385393103 -2.3183916030960132 ;
	setAttr ".s" -type "double3" 0.999999999999995 1.000000000000002 1.0000000000000024 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.48489773119608209 -0.60591837975925655 0.63066432901552072 0
		 -0.67018645321653003 -0.7207363475009132 -0.17717086426884454 0 0.56189350260303061 -0.33675293970300962 -0.75556170956284463 0
		 49.688582620705056 102.91678239821388 18.129843504393527 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_01_l" -p "cloth_middle_metacarpal_l";
	rename -uid "5EBB38CD-4A7C-BF44-45ED-C8B3AAEEEA6A";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 6.0982089042662935 1.7053025658242404e-13 -3.5527136788005009e-15 ;
	setAttr ".r" -type "double3" -2.9849635172452557e-14 1.6792332148016177e-14 31.572682030173283 ;
	setAttr ".s" -type "double3" 0.99999999999999611 1.0000000000000031 1.0000000000000024 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.062225495669627207 -0.89359128709144686 0.44454811734181143 0
		 -0.82486585549361968 -0.2968039006703202 -0.48114852460197066 0 0.56189350248019387 -0.33675285768516761 -0.75556171132423033 0
		 52.645590277826741 99.221760378678837 21.975762047850893 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_02_l" -p "cloth_middle_01_l";
	rename -uid "C17CBA20-4C5B-6508-3752-648577DAD562";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" 5.169000148773307 -1.5631940186722204e-13 9.2370555648813024e-14 ;
	setAttr ".r" -type "double3" -2.7278473962867738e-14 1.3218543304041277e-14 20.769210477739012 ;
	setAttr ".s" -type "double3" 0.99999999999999245 1.0000000000000073 1.0000000000000016 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.23431898608882951 -0.94077017194003132 0.24504236604270399 0
		 -0.79332824509644595 0.03935510564406397 -0.60752033295625851 0 0.56189349479000572 -0.33675306750187811 -0.75556131395598347 0
		 52.967232078635348 94.602789841406278 24.273631367182816 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_03_l" -p "cloth_middle_02_l";
	rename -uid "9EC62A51-4E1A-655E-1D87-3E9F82F5B813";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" 2.4739999771119159 4.2632564145606011e-14 -4.6185277824406512e-14 ;
	setAttr ".r" -type "double3" -1.2916364976337363e-14 1.5968002090006723e-14 9.9999999709532297 ;
	setAttr ".s" -type "double3" 0.99999999999998734 1.0000000000000135 0.99999999999999789 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.36851928419353081 -0.91964389745761499 0.13582465476018205 0
		 -0.74058727702713745 0.20212058522969648 -0.64084188780618456 0 0.56189364705205236 -0.33675303955210589 -0.75556163923421937 0
		 52.387556965377058 92.275308491730343 24.879860919498665 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thumb_01_l" -p "cloth_hand_l";
	rename -uid "673A5CDC-4A5F-CB39-0E5D-40B1450D19B1";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 1.9924465422483948 1.3566048098398653 -2.5815360557459091 ;
	setAttr ".r" -type "double3" 73.564463955610094 39.90417842190142 20.508675516543203 ;
	setAttr ".s" -type "double3" 0.99999999999999578 1.0000000000000027 1.0000000000000024 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.23677733573802998 -0.46744583427812364 0.85172258675780266 0
		 0.35804510181719196 -0.85693298279194319 -0.37076948487111361 0 0.9031833692042176 0.21716528948474759 0.37026899990533607 0
		 46.226711453183285 102.95844053308552 18.495820172867624 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thumb_02_l" -p "cloth_thumb_01_l";
	rename -uid "3B4F4EB5-402D-D0E7-01E9-17BDAEC0D364";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 4.3779997825622843 9.9475983006414026e-14 -1.8474111129762605e-13 ;
	setAttr ".r" -type "double3" 3.5306283254456092 -1.9322910017090325 23.246005868095999 ;
	setAttr ".s" -type "double3" 0.99999999999999201 1.0000000000000016 1.0000000000000071 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.045744984108696596 -0.75995313970017531 0.64836644882724115 0
		 0.47737462822411569 -0.58677030697461086 -0.65407522804700169 0 0.87750832517805977 0.27959303154900106 0.38962414590013206 0
		 45.190100324334146 100.91195752446218 22.224657334872393 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thumb_03_l" -p "cloth_thumb_02_l";
	rename -uid "8ED5168D-41C2-5604-45D1-7EBF66AA4054";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" 3.0859999656678099 4.9737991503207013e-14 1.1368683772161603e-13 ;
	setAttr ".r" -type "double3" 0 0 9.9999999709526808 ;
	setAttr ".s" -type "double3" 0.99999999999998601 1.0000000000000056 1.0000000000000104 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.037845433683874767 -0.85029904860956507 0.52493727641814725 0
		 0.47806582022221661 -0.44589163415051347 -0.75672559425824226 0 0.8775079406372267 0.27959282493030296 0.38962398036976076 0
		 45.048930681525547 98.566746165169036 24.225515112486022 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_metacarpal_l" -p "cloth_hand_l";
	rename -uid "D7C70F75-4B47-7545-44BD-CEBD42813B26";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 3.3143785008620945 -0.30591727493282406 2.3911108936045178 ;
	setAttr ".r" -type "double3" -27.769049086156421 -19.527703069489291 11.850627254935693 ;
	setAttr ".s" -type "double3" 0.99999999999999512 1.0000000000000018 1.0000000000000024 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.50165929300020462 -0.81946999135791332 0.27714124041169974 0
		 -0.86150484532853877 -0.50229897377609023 0.074197529701931553 0 0.078405071797343129 -0.27598040174078031 -0.95796031621622768 0
		 50.945127022704234 101.90432442210121 16.074230044259064 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_01_l" -p "cloth_pinky_metacarpal_l";
	rename -uid "0779359B-4443-14B7-4736-5E8D9B6A62C8";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 4.9575676918030496 -0.14312039315690583 -0.19884027540683746 ;
	setAttr ".r" -type "double3" 10.491640067554425 0.60504264039476185 14.83368089511613 ;
	setAttr ".s" -type "double3" 0.99999999999999589 1.0000000000000047 0.99999999999999889 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.26354049382800654 -0.91778951936305331 0.29700034899850314 0
		 -0.93037058005902762 -0.32317419004185122 -0.17311581262104125 0 0.25486661584744924 -0.23069736022788864 -0.93905385313800027 0
		 53.53984574660192 97.968506999292288 17.62803418662552 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_02_l" -p "cloth_pinky_01_l";
	rename -uid "305123C4-4798-2BD7-F2DE-AE8F9028189E";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" 3.8159999847412394 2.9842794901924208e-13 7.460698725481052e-14 ;
	setAttr ".r" -type "double3" -2.5384009317319838e-14 -4.9689291348179729e-14 21.286999049243761 ;
	setAttr ".s" -type "double3" 0.99999999999999023 1.0000000000000093 1.0000000000000002 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.092201161514231245 -0.97249687863080403 0.21388924523279784 0
		 -0.9625701591025877 0.032069125854169489 -0.26912764401488071 0 0.2548666824390427 -0.23069755404975101 -0.93905341555138366 0
		 54.54551445585296 94.46622372674544 18.761389900691761 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_03_l" -p "cloth_pinky_02_l";
	rename -uid "E2DDCA06-458B-E632-22DC-F9B7EB9427E4";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" 2.0399999618530842 -1.4210854715202004e-13 6.7501559897209518e-14 ;
	setAttr ".r" -type "double3" -1.9300720835860689e-14 -4.954242793617548e-14 4.9170000470220474 ;
	setAttr ".s" -type "double3" 0.99999999999998146 1.0000000000000198 1.0000000000000004 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.17436619807034176 -0.96616941656402011 0.19003430520990994 0
		 -0.95112558510216438 0.11530657717603962 -0.28647013329253607 0 0.25486662913969543 -0.23069740030713909 -0.9390537142595996 0
		 54.357453977022615 92.482315221550678 19.197717262489395 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_metacarpal_l" -p "cloth_hand_l";
	rename -uid "37297A2E-4A50-3251-9F7C-D79027939C16";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 3.3743038186485741 -0.54251690297387256 1.0917565771567119 ;
	setAttr ".r" -type "double3" -13.299834844614882 -11.809318643867149 -1.5945633922234601 ;
	setAttr ".s" -type "double3" 0.99999999999999467 1.0000000000000022 1.0000000000000027 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.59060502487990219 -0.65963288919378749 0.46483382716129884 0
		 -0.73083334361545838 -0.68147063113585427 -0.038479077837752229 0 0.34215249306123674 -0.3169901233963206 -0.88456168902526722 0
		 50.330905037601468 102.40470292236149 17.13264653749372 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_01_l" -p "cloth_ring_metacarpal_l";
	rename -uid "54B1E557-4524-7609-037E-8D9C4C739920";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 5.6455168724061693 -0.041624534875111863 -0.020689174532869004 ;
	setAttr ".r" -type "double3" 6.3958444481096146 -0.11693801316947267 29.414482492693985 ;
	setAttr ".s" -type "double3" 0.99999999999999645 1.0000000000000027 1.0000000000000016 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.15623818596893879 -0.90993103246640938 0.38420771186611619 0
		 -0.88283473603848006 -0.30308702218270361 -0.35880521303802726 0 0.44293617834741306 -0.28313283828801472 -0.85067248939726692 0
		 53.68851741064038 98.715653538569171 19.776772031423288 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_02_l" -p "cloth_ring_01_l";
	rename -uid "B19ED30D-4DAA-632F-A897-9B9E3871D1B1";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" 4.9770002365112305 -9.9475983006414026e-14 -6.3948846218409017e-14 ;
	setAttr ".r" -type "double3" -4.541105972273713e-14 -4.1902535824773686e-14 18.963999541971461 ;
	setAttr ".s" -type "double3" 0.99999999999999256 1.0000000000000078 1.0000000000000007 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.13913996944665102 -0.95903775857154649 0.24675175378428485 0
		 -0.88569011802957565 0.0090676976266102494 -0.46418769740319749 0 0.44293619735123363 -0.28313304949806012 -0.85067206892073166 0
		 54.46611297550983 94.186928751006306 21.688975143639727 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_03_l" -p "cloth_ring_02_l";
	rename -uid "B6F2D01F-43E4-5E64-BCDB-0A9980661885";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" 2.2650001049045443 0 2.2737367544323206e-13 ;
	setAttr ".r" -type "double3" -4.1011632547801285e-14 -3.5175437823155051e-14 9.1679997480247817 ;
	setAttr ".s" -type "double3" 0.99999999999998634 1.000000000000014 0.99999999999999867 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.27847944599852603 -0.94534179776705241 0.16964047049477976 0
		 -0.85220720026495977 0.16175552005207328 -0.49757276398167483 0 0.44293626436244626 -0.28313296501722635 -0.85067238582427207 0
		 54.150991371487976 92.01469242270386 22.247861770125226 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_upperarm_twist_01_l" -p "cloth_upperarm_l";
	rename -uid "57AAB27E-48C0-BBAB-EFEA-99B596DE2F3A";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" 9.2570457426103445 2.9756606068076508e-09 -2.0278889678593259e-11 ;
	setAttr ".r" -type "double3" 5.2582642220268771e-07 -2.1533312359715504 -0.3266089060371174 ;
	setAttr ".s" -type "double3" 0.99999999999999645 1.0000000000000011 1.0000000000000007 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.60649254743332648 -0.79463146847798138 0.026965451144979398 0
		 -0.029307965712027623 -0.05623514600111712 -0.99798691728861222 0 0.79454882358081669 0.60448132525393472 -0.057395228785353275 0
		 24.342248212805544 136.01964430402896 -2.3404825895836536 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_upperarm_twist_02_l" -p "cloth_upperarm_l";
	rename -uid "4CD5253C-4FF1-4F5C-22DA-EEAB98D5AD1E";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" 18.514091488459925 2.975665935878169e-09 -2.0392576516314875e-11 ;
	setAttr ".r" -type "double3" 5.2546705714352743e-07 5.9633907289413738e-10 -3.6426607068277193e-10 ;
	setAttr ".s" -type "double3" 0.99999999999999645 1.0000000000000011 1.0000000000000007 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.57603356952398699 -0.81709033696008193 0.023413603183081 0
		 -0.032592099667534742 -0.051578266839375927 -0.99813660045296926 0 0.81677602916633074 0.57419709034294053 -0.056341502856928814 0
		 29.674617317034041 128.45580167629774 -2.1237417938427017 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_clavicle_r" -p "cloth_spine_05";
	rename -uid "D40C4FA0-4849-97F4-4000-CB98334B88FB";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "blendParent1" -ln "blendParent1" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 7;
	setAttr ".t" -type "double3" 5.5162200927734943 1.3148112297058177 1.4278726577604703 ;
	setAttr ".r" -type "double3" -16.736414910351485 99.16877411729206 153.12438363641243 ;
	setAttr ".s" -type "double3" 1.0000000000000004 1.0000000000000004 0.99999999999999967 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.9872232528307775 0.15258975029080923 0.045897899477120176 0
		 -0.045885930607882361 -0.0036018072503485811 0.9989401925825081 0 0.15259334992873069 -0.98828305413515882 0.0034459348235592194 0
		 -1.4278726577399969 146.30099472621765 -1.7398495510540903 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".blendParent1" -type "string" "1.000000";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_upperarm_r" -p "cloth_clavicle_r";
	rename -uid "F86D7DA6-49D1-DFD3-FC95-2A82165BBBA3";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "blendParent1" -ln "blendParent1" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".t" -type "double3" -17.809625627817255 2.8800139753037968e-06 0.00043809145563500351 ;
	setAttr ".r" -type "double3" -4.3373453218908491 46.029604187366942 -4.3585187592162153 ;
	setAttr ".s" -type "double3" 0.99999999999999833 0.99999999999999867 1.0000000000000051 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.57603356999186506 0.81709064430416578 -0.023413782971299479 0
		 -0.032592099840372916 0.051578495414514765 0.99813697148175295 0 0.81677602882946609 -0.5741972986712639 0.056341644706228142 0
		 -19.009882484041452 143.58299543016119 -2.5572695712484719 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".blendParent1" -type "string" "1.000000";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_lowerarm_r" -p "cloth_upperarm_r";
	rename -uid "65577BAF-4DA2-7B70-217A-6A95086C1365";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" -27.770694729470364 -2.9770239606818905e-09 -1.9809931472991593e-11 ;
	setAttr ".r" -type "double3" 2.7668847737304411e-14 2.9988675980859289e-09 -38.978821941626634 ;
	setAttr ".s" -type "double3" 0.99999999999999734 0.99999999999999978 1.0000000000000069 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.46829763471056329 0.60274413691377671 -0.64606255946351587 0
		 0.33700778040583623 0.55407307064563793 0.76120219937362321 0 0.81677602882947176 -0.5741972986712679 0.05634164470622853 0
		 -35.006734910131691 120.89182058074178 -1.9070525548630362 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_lowerarm_twist_02_r" -p "cloth_lowerarm_r";
	rename -uid "2E2228D1-413D-E269-B672-589521763F2D";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" -9.083662144519181 -1.3713474800169934e-11 -2.1296102659107419e-09 ;
	setAttr ".r" -type "double3" 1.2856753627043855 -1.7275330716881596 1.9858281262685087 ;
	setAttr ".s" -type "double3" 0.99999999999999145 1.0000000000000004 1.0000000000000078 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.50409945421183022 0.60398964789860998 -0.61731736537074211 0
		 0.33849060600835101 0.51942179311399406 0.78461817793148092 0 0.79454883418670808 -0.60448172436377889 0.057395420474525213 0
		 -39.260592408663918 115.41669714364775 3.9615615905644805 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_lowerarm_twist_01_r" -p "cloth_lowerarm_r";
	rename -uid "4FE4D212-40C5-95F9-64AA-42B2A9013389";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" -18.167305215546236 -1.3699263945454732e-11 -4.2591210558384773e-09 ;
	setAttr ".r" -type "double3" 1.2856753860273884 -1.7275254950693766 1.9858282109465057 ;
	setAttr ".s" -type "double3" 0.99999999999999101 0.99999999999999933 1.0000000000000071 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.50409934863881767 0.60398972705929777 -0.61731737412974941 0
		 0.3384906071183838 0.51942179374105557 0.78461817703748371 0 0.79454890069433048 -0.60448164472869548 0.057395338488105525 0
		 -43.514440975120209 109.94158280861338 9.8301652270300188 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_hand_r" -p "cloth_lowerarm_r";
	rename -uid "645157A4-48BE-EA64-EF43-E19E2BF3D3D6";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" -27.251010894784748 4.5151438143875566e-10 7.1054273576010019e-14 ;
	setAttr ".r" -type "double3" -67.770758774103754 1.4734712621344073 1.8489163484349502 ;
	setAttr ".s" -type "double3" 0.99999999999999167 1.0000000000000016 1.0000000000000051 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.45776605882155008 0.63486684161597096 -0.62241009696784377 0
		 -0.64550904801161757 0.7187277091635309 0.25835740557549725 0 0.61136593323977484 0.28350409784886949 0.7388214413352997 0
		 -47.768318855478952 104.46643353918695 15.69880529213345 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_metacarpal_r" -p "cloth_hand_r";
	rename -uid "E164A5AA-47F3-CC4B-0B4B-0789BA8CABF9";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -3.3146772373322619 0.30593533749708968 -2.391286854523754 ;
	setAttr ".r" -type "double3" -27.769049175865383 -19.527703070553386 11.850627327283208 ;
	setAttr ".s" -type "double3" 0.99999999999999323 1.0000000000000031 1.0000000000000022 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.50165929286189059 0.81946999141620325 -0.27714124048213162 0
		 -0.86150484538099525 0.50229897373941623 -0.074197529360792269 0 0.07840507210601233 0.27598040163444448 0.95796031622227074 0
		 -50.945100940133408 101.90399442087478 16.074203278681807 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_01_r" -p "cloth_pinky_metacarpal_r";
	rename -uid "AF3BB704-443D-771F-6FE2-48BEA74200E2";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -4.9573006629944487 0.1432614624499422 0.19892024993894353 ;
	setAttr ".r" -type "double3" 10.491640067554444 0.60504264039483013 14.833680895116233 ;
	setAttr ".s" -type "double3" 0.99999999999999378 1.0000000000000064 1.0000000000000013 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.26354049383431455 0.91778951935150677 -0.29700034902855538 0
		 -0.93037057991364036 0.3231741901835285 0.17311581313797475 0 0.2548666163716824 0.23069736007534425 0.93905385303319722 0
		 -53.539800974929911 97.968488762008676 17.627999571969671 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_02_r" -p "cloth_pinky_01_r";
	rename -uid "664EB7BD-4F36-CBFF-A5FE-67885E946D3A";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" -3.8160362243652486 3.0366025427497334e-05 3.2629206586420878e-05 ;
	setAttr ".r" -type "double3" 2.6183092860785283e-14 -9.4707106608759794e-14 21.286999049243576 ;
	setAttr ".s" -type "double3" 0.99999999999998779 1.0000000000000113 1.0000000000000007 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.09220116208937737 0.97249687877768609 -0.21388924431700984 0
		 -0.9625701592672794 -0.032069126843100371 0.26912764330801653 0 0.25486668160900205 0.2306975532930835 0.9390534159625582 0
		 -54.545499738718554 94.466189331947803 18.76140176623932 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_pinky_03_r" -p "cloth_pinky_02_r";
	rename -uid "8B0E9968-4C11-93D5-95C6-0E9A171A2EF5";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" -2.039999723434434 -1.7523876479685896e-05 -3.1002964572479641e-05 ;
	setAttr ".r" -type "double3" 1.7075473133681139e-06 -9.5957751101362603e-14 4.9170000470217952 ;
	setAttr ".s" -type "double3" 0.99999999999997802 1.0000000000000213 0.99999999999999956 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.1743661987730932 0.96616941631306219 -0.19003430584096415 0
		 -0.95112557728211866 -0.1153065706781768 0.28647016187173319 0 0.25486665784221452 0.23069740460586502 0.93905370541345123 0
		 -54.357429331665401 92.482274200977656 19.19769472817476 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_metacarpal_r" -p "cloth_hand_r";
	rename -uid "533353FA-4A6A-339B-8E66-B7B1B6F6A78B";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -3.37420797296285 0.54299174756033608 -1.0917816194755261 ;
	setAttr ".r" -type "double3" -13.299834928372192 -11.809318664560722 -1.5945633327205033 ;
	setAttr ".s" -type "double3" 0.99999999999999367 1.000000000000004 1.0000000000000024 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.59060502468686882 0.65963288927839403 -0.4648338272794032 0
		 -0.73083334363961139 0.68147063109304251 0.038479078156593322 0 0.3421524933428684 0.31699012331229826 0.88456168894933063 0
		 -50.330900917148398 102.40499451543326 17.132603694198863 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_01_r" -p "cloth_ring_metacarpal_r";
	rename -uid "3FB32741-4140-3027-DB89-71B985599C65";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -5.6457118988036648 0.041443493217315108 0.020674973726247714 ;
	setAttr ".r" -type "double3" 6.3958444481098411 -0.11693801316962292 29.414482492694098 ;
	setAttr ".s" -type "double3" 0.99999999999999456 1.0000000000000047 1.0000000000000024 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.15623818592891039 0.90993103248356333 -0.38420771184174934 0
		 -0.88283473580084537 0.30308702229470585 0.35880521352814188 0 0.44293617883519015 0.28313283811298628 0.85067248920154415 0
		 -53.688501027323184 98.71568862106939 19.776800325680714 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_02_r" -p "cloth_ring_01_r";
	rename -uid "A4E58A07-4831-FDDB-D8A7-B2A00BE36B40";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" -4.9770674705506366 -2.084683357850281e-05 -2.3612021340824185e-05 ;
	setAttr ".r" -type "double3" -3.0902359337965415e-14 -7.4260495240840948e-14 18.963999541971067 ;
	setAttr ".s" -type "double3" 0.99999999999999134 1.0000000000000078 1.0000000000000011 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.13913996998873965 0.95903775871656582 -0.24675175291495613 0
		 -0.88569011834810185 -0.0090676987548741206 0.46418769677339922 0 0.44293619654403643 0.28313304897070268 0.85067206951655772 0
		 -54.466099722475249 94.186889410603044 21.689001522891221 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ring_03_r" -p "cloth_ring_02_r";
	rename -uid "E4260032-40F1-B60D-C34C-F2B6789316A1";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" -2.2649745941163104 5.0017570167426584e-05 -1.1221488446011563e-05 ;
	setAttr ".r" -type "double3" -4.2747414291988432e-14 -7.4716686139220406e-14 9.1679997480247266 ;
	setAttr ".s" -type "double3" 0.99999999999998535 1.0000000000000153 0.99999999999999956 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.27847944667745261 0.94534179746656388 -0.16964047105474672 0
		 -0.85220719989912064 -0.16175552020977166 0.49757276455698884 0 0.44293626463947655 0.28313296593040549 0.85067238537609347 0
		 -54.151029950911777 92.014673655369009 22.247895007487962 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_metacarpal_r" -p "cloth_hand_r";
	rename -uid "813AD67E-4261-4BCA-6DB4-12BB23BBE8EE";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -3.3758001320154492 0.75400392488306522 0.18280551726579297 ;
	setAttr ".r" -type "double3" -4.2725003486284159 -0.13075115677207733 -2.3183915582170682 ;
	setAttr ".s" -type "double3" 0.99999999999999345 1.0000000000000036 1.0000000000000029 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.48489773093713401 0.60591837989355413 -0.63066432908020664 0
		 -0.67018645325873494 0.72073634739536718 0.17717086453790937 0 0.56189350277616723 0.33675293968726416 0.75556170944575485 0
		 -49.68860086885234 102.91699479990878 18.129803793526911 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_01_r" -p "cloth_middle_metacarpal_r";
	rename -uid "03C375D4-4C2F-EB73-5666-31ACA6073A87";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -6.0983657836913494 -0.00012385072464837776 1.430381953326787e-06 ;
	setAttr ".r" -type "double3" 1.8071628643319774e-13 -1.789229145311095e-13 31.572682030173162 ;
	setAttr ".s" -type "double3" 0.99999999999999301 1.0000000000000051 1.000000000000004 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.062225495551872956 0.89359128713652014 -0.44454811726767435 0
		 -0.82486585524078104 0.29680390069669932 0.48114852501917393 0 0.56189350286441875 0.3367528575423076 0.75556171110216852 0
		 -52.645600794664759 99.221788952981569 21.975800423254821 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_02_r" -p "cloth_middle_01_r";
	rename -uid "3BC6E15E-4203-E7AC-6028-EF8908084FCD";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" -5.1689915657044168 -7.7438591745249141e-05 -3.7045669269986092e-05 ;
	setAttr ".r" -type "double3" 1.135948241019918e-13 -2.4529244123356143e-13 20.769210477738905 ;
	setAttr ".s" -type "double3" 0.99999999999998923 1.0000000000000082 1.0000000000000018 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.23431898667602188 0.94077017199490631 -0.24504236527050924 0
		 -0.79332824552105163 -0.039355106907066062 0.60752033231997216 0 0.56189349394565213 0.33675306720095904 0.755561314718035 0
		 -52.96719957522113 94.602790384239327 24.273600498401144 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_middle_03_r" -p "cloth_middle_02_r";
	rename -uid "D7F6FF89-4C48-9445-387D-EE848C98B85B";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" -2.4740469455720415 4.5777305821559366e-05 3.4385015165838695e-05 ;
	setAttr ".r" -type "double3" 6.8697176607115295e-14 -2.6585703505114068e-13 9.9999999709530645 ;
	setAttr ".s" -type "double3" 0.99999999999998479 1.0000000000000171 0.99999999999999944 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.36851928489998886 0.91964389709895067 -0.13582465527181725 0
		 -0.74058727657762902 -0.20212058526571941 0.64084188831429567 0 0.56189364718118984 0.33675304050994309 0.75556163871128434 0
		 -52.387529460953488 92.275274368316431 24.879894829249203 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_metacarpal_r" -p "cloth_hand_r";
	rename -uid "B8F6EB9B-4A45-F8CB-78A7-E2B01D3E09C2";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -3.4445140356856783 0.38516680848238138 2.3793086948369897 ;
	setAttr ".r" -type "double3" 3.2877464080434233 7.3255016575580303 -0.60616236133468626 ;
	setAttr ".s" -type "double3" 0.99999999999999367 1.0000000000000027 1.0000000000000022 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.38282470999277746 0.58595975186044291 -0.71421064409806023 0
		 -0.60140250574996534 0.74492322341142525 0.28879879077824322 0 0.70125620678763578 0.31896875765447374 0.63757268001220435 0
		 -48.139100850768926 103.23099487826747 19.700104266595805 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_01_r" -p "cloth_index_metacarpal_r";
	rename -uid "97B5D6BC-4D25-1B41-84DC-11AC90D06322";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -5.8772053718567427 -0.043412361294102197 -0.24095164239404632 ;
	setAttr ".r" -type "double3" 1.8098303048989938e-13 -1.661516457038313e-13 23.372999658581101 ;
	setAttr ".s" -type "double3" 0.99999999999999267 1.0000000000000042 1.0000000000000053 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.1128251453733253 0.83339937939284292 -0.54103270371663348 0
		 -0.70392486737798787 0.45133677241801362 0.54843879911453608 0 0.70125620685908929 0.31896868697241232 0.63757268457240879 0
		 -50.531900826252752 99.677988827144645 23.73150097907746 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_02_r" -p "cloth_index_01_r";
	rename -uid "F222CD9B-4EFA-F444-99FD-C9AF1767159B";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" -4.0799326896668759 5.0402058349163781e-06 3.210666176300947e-05 ;
	setAttr ".r" -type "double3" 1.212598354441596e-13 -2.2737503945399483e-13 14.892568419110425 ;
	setAttr ".s" -type "double3" 0.99999999999998723 1.0000000000000064 1.0000000000000036 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.071878368257376909 0.9214016195717547 -0.38190625430287661 0
		 -0.7092761916076521 0.22198616510205421 0.66906557882335527 0 0.7012561410726057 0.31896891255744136 0.6375723326933892 0
		 -50.992199590104335 96.277791119064332 25.938900006044509 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_index_03_r" -p "cloth_index_02_r";
	rename -uid "2C6EC7AA-4B4C-640C-06BB-DB9FC869D14F";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 6;
	setAttr ".t" -type "double3" -2.595076322555613 3.9602186120646365e-05 -3.5606819768219111e-06 ;
	setAttr ".r" -type "double3" 7.1554549857603245e-14 -2.5775484131777765e-13 12.516400997546619 ;
	setAttr ".s" -type "double3" 0.99999999999998446 1.0000000000000153 1.0000000000000007 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.22388381464131962 0.94761237225004924 -0.22783043085289764 0
		 -0.67684263949151935 0.0170248147996091 0.73593102377477382 0 0.7012563919296928 0.31896894267602743 0.6375726434793253 0
		 -50.805728911374032 93.886675058511443 26.929995405751654 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thumb_01_r" -p "cloth_hand_r";
	rename -uid "B60EBC7F-49E7-AC3B-1826-7595A453A0D7";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -1.9928325402862583 -1.3566571620229837 2.5813255269522255 ;
	setAttr ".r" -type "double3" 73.564463846441569 39.904178433577059 20.508675488871859 ;
	setAttr ".s" -type "double3" 0.99999999999999345 1.0000000000000031 1.0000000000000013 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.2367773360513197 0.46744583436389642 -0.85172258662605771 0
		 0.35804510189578509 0.85693298276798835 0.37076948485221134 0 0.903183369090935 -0.21716528939464572 -0.37026900022730203 0
		 -46.226700991800513 102.95799471674208 18.495803982269472 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thumb_02_r" -p "cloth_thumb_01_r";
	rename -uid "ABC4E82B-41CA-B6A5-17D8-7186B1348500";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -4.3778247833251953 0.00042712956192758611 -0.00013574546025552081 ;
	setAttr ".r" -type "double3" 3.5306281293993456 -1.9322909767099268 23.246005839159633 ;
	setAttr ".s" -type "double3" 0.99999999999999212 1.0000000000000011 1.0000000000000091 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.045744984919149453 0.75995313958456889 -0.6483664489055555 0
		 0.47737462562153676 0.58677030818096798 0.6540752288642635 0 0.87750832655165034 -0.27959302933149444 -0.38962414439783521 0
		 -45.190100974990457 100.91198902091951 22.224700730062267 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thumb_03_r" -p "cloth_thumb_02_r";
	rename -uid "43354F54-446D-3564-D575-F0AD00BDF822";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" -3.0859522819519398 -1.4851160791806706e-05 4.5825581736380627e-05 ;
	setAttr ".r" -type "double3" 0 0 9.9999999709527234 ;
	setAttr ".s" -type "double3" 0.99999999999998457 1.0000000000000038 1.0000000000000113 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.037845432290662798 0.85029904920866284 -0.52493727554815295 0
		 0.47806581646959068 0.44589163512245766 0.75672559605627843 0 0.87750794274174615 -0.2795928215582712 -0.38962397804975052 0
		 -45.048900966950129 98.566792138271936 24.225499857560763 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_upperarm_twist_01_r" -p "cloth_upperarm_r";
	rename -uid "084B1AD2-44E5-9081-59A6-5EBAFA414643";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" -9.2568981720736758 1.0199371363484033e-05 -0.00010078241042776881 ;
	setAttr ".r" -type "double3" 5.1761945650009702e-07 -2.1533312360273977 -0.32660890572304974 ;
	setAttr ".s" -type "double3" 0.999999999999996 0.99999999999999689 1.0000000000000036 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.60649254788980544 0.79463146815725005 -0.026965450329482346 0
		 -0.029307965885354333 0.05623514515020217 0.99798691733146394 0 0.79454882322599096 -0.60448132575472102 0.057395228423281756 0
		 -24.342249234228117 136.01931877285625 -2.3405178063960417 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_upperarm_twist_02_r" -p "cloth_upperarm_r";
	rename -uid "FD915775-44E4-DAEA-3C57-0489B4222C20";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".t" -type "double3" -18.513796347330157 2.0401726728458414e-05 -0.00020156480097455187 ;
	setAttr ".r" -type "double3" 5.1752872579777759e-07 5.8751058009128576e-10 -3.5875137585388795e-10 ;
	setAttr ".s" -type "double3" 0.999999999999996 0.99999999999999678 1.0000000000000042 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.57603356999186273 0.81709033665382458 -0.023413602359850755 0
		 -0.032592099840372812 0.051578265994670261 0.99813660049096931 0 0.81677602882946954 -0.57419709085462856 0.05634150252572602 0
		 -29.674615986329201 128.45565512164097 -2.1237759683219677 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_coatTail_01" -p "cloth_spine_01";
	rename -uid "343A642D-477B-BC05-94FF-FA8EB1F335DD";
	setAttr ".t" -type "double3" 0 -6 -10 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode joint -n "cloth_coatTail_02" -p "cloth_coatTail_01";
	rename -uid "2072E3D8-4C92-2EAC-2451-EEB3F554C853";
	setAttr ".t" -type "double3" 0 -28 -2 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode joint -n "cloth_thigh_r" -p "cloth_pelvis";
	rename -uid "92AFE268-42B4-40EF-162A-419D83743C76";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "blendParent1" -ln "blendParent1" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" -2.3657262325289707 -0.11948779225345163 9.9690914154052237 ;
	setAttr ".r" -type "double3" 8.4085386509694473 -3.1255390874215432 176.43986684730848 ;
	setAttr ".s" -type "double3" 1 0.99999999999999989 1 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.054523896494896425 -0.99851165611282844 0.0012717381138619629 0
		 -0.14601293301635634 0.0092329896063877218 0.98923959448401033 0 -0.9877790077253995 0.053751507046265815 -0.14629903412969061 0
		 -9.9690914154052237 93.543381742614869 2.5500232346622762 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".blendParent1" -type "string" "1.000000";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_calf_r" -p "cloth_thigh_r";
	rename -uid "21A524C9-4F11-3A4D-DDC1-76948DEC0173";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 43.341262817382805 5.4167897722834368e-08 6.2890173779805991e-07 ;
	setAttr ".r" -type "double3" -6.3367434381586739e-15 -5.5502215518781979e-16 -5.0048448502512386 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999989 1 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.041577849337829653 -0.99551014127010207 -0.085034352310236608 0
		 -0.15021289672150617 -0.07791234894826328 0.98557889158600487 0 -0.9877790077253995 0.053751507046265815 -0.14629903412969061 0
		 -12.332226572343455 50.26662566311316 2.6051419320673626 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_GM_foot_R" -p "cloth_calf_r";
	rename -uid "7A0C3B41-4A59-4BF6-4CD2-A3AD27AF069C";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 42.217948913574219 3.1899732289009108e-07 2.8053701583985458e-09 ;
	setAttr ".r" -type "double3" -0.0046626083854333948 3.0812019613372339 2.6641047060062419 ;
	setAttr ".s" -type "double3" 1 1.0000000000000002 0.99999999999999978 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.0046495405308430715 -0.99950197917735084 -0.031211782925841328 0
		 -0.14803750008632441 -0.03155618826953209 0.9884781765674393 0 -0.98897081875101012 2.4544971774453916e-05 -0.14811049610510657 0
		 -14.08755814231283 8.2382293513238949 -0.98483369567847312 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ball_r" -p "cloth_GM_foot_R";
	rename -uid "C88E6D61-447D-B617-ABC7-DE93DECB03A2";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" 7.0094366762781979 15.237594510952336 -0.53894490351609825 ;
	setAttr ".r" -type "double3" 8.3068925598965406e-07 3.7504786903060076e-08 -89.999999771134654 ;
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 1.0000000000000002 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.14803750010489675 0.031556184277067523 -0.98847817669211313 0
		 0.0046495399395141039 -0.99950197930340035 -0.031211778977410835 0 -0.98897081875101034 2.4544971774453923e-05 -0.1481104961051066 0
		 -15.777702098626579 0.75142989091567891 13.938242322842376 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_calf_twist_02_r" -p "cloth_calf_r";
	rename -uid "89F30247-43A1-6D95-CDF4-0AAA4B03B5A5";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 14.072649955204128 1.2177698627269251e-08 0.037729155166843498 ;
	setAttr ".r" -type "double3" -0.0046474169617998764 0.25816150024468143 2.6643343196876104 ;
	setAttr ".s" -type "double3" 1.0000000000000004 0.99999999999999778 0.99999999999999889 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.044064317019873983 -0.99828778720304934 -0.038468557118925779 0
		 -0.14803764665279109 -0.031556181464800541 0.98847815483442114 0 -0.98799959065734133 0.049251409447858253 -0.1463936731157601 0
		 -12.954605161247217 36.259187916164208 1.4029635308805437 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_calf_twist_01_r" -p "cloth_calf_r";
	rename -uid "F898EB59-4764-9528-5F76-2FBB2517AAE2";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" 28.145299910408248 2.4139938492595547e-08 0.075458308970311805 ;
	setAttr ".r" -type "double3" -0.0046474169618205309 0.25816150024468243 2.6643343196876095 ;
	setAttr ".s" -type "double3" 1 0.99999999999999789 0.99999999999999889 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.044064317019873948 -0.99828778720304889 -0.038468557118925766 0
		 -0.14803764665279076 -0.031556181464800576 0.98847815483442114 0 -0.98799959065734133 0.049251409447858226 -0.14639367311575974 0
		 -13.576983748771902 22.251750169158772 0.20078512968083428 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thigh_twist_01_r" -p "cloth_thigh_r";
	rename -uid "DAA0C70A-4CB7-9D49-B0EB-B59F6229E0F8";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 14.447087287902747 1.7767383120315117e-08 2.0779022591455032e-07 ;
	setAttr ".r" -type "double3" -1.1339964774904531e-05 0.25820444407632642 -1.3073006647516867 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999845 0.99999999999999845 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.046726511937084853 -0.99869449454677006 -0.020638305263837975 0
		 -0.14721867931861013 -0.013550188470859609 0.9890111490029253 0 -0.98799964248064109 0.049251385304111737 -0.14639333148660902 0
		 -10.756803115188658 79.117796700097585 2.5683961333772825 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thigh_twist_02_r" -p "cloth_thigh_r";
	rename -uid "78980AE4-4421-BC4B-83FC-05AC30BB0CD1";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 28.894174575805636 3.597016640100037e-08 4.183619140007977e-07 ;
	setAttr ".r" -type "double3" -5.5722098187068765e-06 0.25820457569897026 -1.3073006387592785 ;
	setAttr ".s" -type "double3" 0.99999999999999989 0.99999999999999845 0.99999999999999845 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.04672650973418984 -0.99869449466605986 -0.020638304478872257 0
		 -0.14721877875367478 -0.013550183059948312 0.98901113427570508 0 -0.98799962776831751 0.049251384373881928 -0.14639343109210498 0
		 -11.544514817783144 64.692211657733694 2.5867690321160786 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thigh_l" -p "cloth_pelvis";
	rename -uid "E8F826A3-4657-EB6C-3DFB-178E6DFC3C38";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "blendParent1" -ln "blendParent1" -dt "string";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" -2.3657112121585016 -0.11004376411435146 -9.9692029953002965 ;
	setAttr ".r" -type "double3" 8.4085386509700015 -3.125539087421795 -3.5601331526916606 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.054523896494900803 0.99851165611282811 -0.0012717381138594233 0
		 -0.14601293301636586 -0.0092329896063863826 -0.98923959448400911 0 -0.98777900772539784 -0.053751507046270429 0.14629903412970005 0
		 9.9692029953002965 93.542798291234519 2.540597234577914 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".blendParent1" -type "string" "1.000000";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_calf_l" -p "cloth_thigh_l";
	rename -uid "B9FC891A-4486-C02C-D173-3B84FF7D8879";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -43.341308593749915 5.0636829840300379e-08 -6.2890234708845583e-07 ;
	setAttr ".r" -type "double3" -6.3368649820769636e-15 -5.5501987678695476e-16 -5.0048448502512644 ;
	setAttr ".s" -type "double3" 0.99999999999999967 0.99999999999999967 0.99999999999999989 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.041577849337833116 0.99551014127010151 0.08503435231023948 0
		 -0.15021289672151603 0.077912348948265014 -0.98557889158600309 0 -0.98777900772539773 -0.053751507046270422 0.14629903412970002 0
		 12.332340632842376 50.265996502529056 2.5957158865213659 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_GM_foot_L" -p "cloth_calf_l";
	rename -uid "9F8CB194-4517-0FA1-D62C-EA9A2222F20C";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -42.217914581298878 -1.6758482701551003e-07 -6.1026572417688385e-07 ;
	setAttr ".r" -type "double3" -0.0046625743810312491 3.0812011306429072 2.6641050022109756 ;
	setAttr ".s" -type "double3" 1.0000000000000004 1.0000000000000011 1.0000000000000004 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.0046495254279420029 0.99950197933985951 0.03121177997163475 0
		 -0.14803750042245864 0.031556183111002029 -0.9884781766817804 0 -0.98897081877169979 -2.455947328891539e-05 0.148110495964556 0
		 14.087671352642202 8.2376344133169113 -0.99425705990161717 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ball_l" -p "cloth_GM_foot_L";
	rename -uid "558DFCD9-41BA-688C-1336-3B92114F13B3";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 5;
	setAttr ".t" -type "double3" -7.0094366386041802 -15.23758886698478 0.53888747195568598 ;
	setAttr ".r" -type "double3" -5.4361247199227896e-12 3.5981153934171149e-09 -90.000000066843469 ;
	setAttr ".s" -type "double3" 0.99999999999999933 0.99999999999999989 0.99999999999999989 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.1480375004170342 -0.031556184277059564 0.98847817664536686 0
		 0.0046495256006482584 0.99950197930304474 0.031211781124831507 0 -0.98897081877169968 -2.4559473288915387e-05 0.14811049596455597 0
		 15.777871382723148 0.75083523972549049 13.928804897013308 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_calf_twist_02_l" -p "cloth_calf_l";
	rename -uid "B234C95B-4FE9-6B99-8108-C5A8DF854A66";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -14.072638993100817 -8.9261931179862586e-14 -3.8250090916847057e-07 ;
	setAttr ".r" -type "double3" -0.0046476056612195704 0.2581615090257971 2.6643343188373629 ;
	setAttr ".s" -type "double3" 1.0000000000000002 0.99999999999999944 1.0000000000000016 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.044064316866261513 0.99828778721012834 0.03846855711114848 0
		 -0.14803764339961659 0.031556181641806597 -0.98847815531597671 0 -0.98799959115163538 -0.049251409190938927 0.14639366986625171 0
		 12.91745107450962 36.256541691024118 1.3990580884877917 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_calf_twist_01_l" -p "cloth_calf_l";
	rename -uid "35E9553A-484A-744C-FE88-5A80492B76D6";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 4;
	setAttr ".t" -type "double3" -28.145277984155889 5.0851437033427871e-06 -0.075448875700660167 ;
	setAttr ".r" -type "double3" -0.0046478377901148253 0.25816151982779489 2.6643343177914209 ;
	setAttr ".s" -type "double3" 1.0000000000000002 0.99999999999999944 1.0000000000000013 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.044064316677291909 0.99828778721883815 0.03846855710157808 0
		 -0.14803763939770673 0.031556181859548768 -0.98847815590836452 0 -0.98799959175969243 -0.049251408874885272 0.14639366586885177 0
		 13.57708681215847 22.251142727405103 0.19135729309555405 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thigh_twist_01_l" -p "cloth_thigh_l";
	rename -uid "60FD3FF7-4450-15A7-95BB-07958D23B035";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -14.447102546691895 1.6878916042628589e-08 -2.0963423885689281e-07 ;
	setAttr ".r" -type "double3" -1.1082331004718504e-05 0.2582044499556449 -1.3073006635906215 ;
	setAttr ".s" -type "double3" 0.99999999999999978 1 1.0000000000000004 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.046726511838690213 0.99869449455209791 0.020638305228776972 0
		 -0.14721868376017999 0.013550188229166005 -0.98901114834508996 0 -0.98799964182347155 -0.049251385262564867 0.14639333593579165 0
		 10.756915523815104 79.117198012417646 2.5589701181547988 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_thigh_twist_02_l" -p "cloth_thigh_l";
	rename -uid "A837B523-426F-AD00-17CA-F6A643BF3F90";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -28.894205093383562 -2.2351409532106459e-06 -8.4941322384679552e-06 ;
	setAttr ".r" -type "double3" -5.4704030106144969e-06 0.25820457802225105 -1.3073006383004471 ;
	setAttr ".s" -type "double3" 0.99999999999999956 0.99999999999999933 0.99999999999999989 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" -0.046726509695310628 0.99869449466816473 0.020638304465018586 0
		 -0.14721878050881559 0.013550182964440834 -0.98901113401575336 0 -0.98799962750862924 -0.049251384357466968 0.14639343285025402 0
		 11.544636359799378 64.691598188585829 2.5773440648714288 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr ".fbxID" 5;
createNode joint -n "cloth_ik_foot_root" -p "cloth_root";
	rename -uid "1F34EA35-43D2-C928-FBE6-819689BF6F08";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "filmboxTypeID" -ln "filmboxTypeID" -dt "string";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 0 -1 0 0 1 0 0 0 0 0 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".filmboxTypeID" -type "string" "5";
createNode joint -n "cloth_ik_foot_l" -p "cloth_ik_foot_root";
	rename -uid "FA8636BA-4B52-847E-431A-EEBD7CDBAF21";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "filmboxTypeID" -ln "filmboxTypeID" -dt "string";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" 14.087671279907227 0.99425750970840454 8.2376375198364258 ;
	setAttr ".r" -type "double3" 90.044595639783211 -88.191663071784689 -81.527131053351226 ;
	setAttr ".s" -type "double3" 1 0.99999999999999978 0.99999999999999978 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.0046495233472996222 0.99950197930433926 0.031211781419062105 0
		 -0.14803749178976766 0.031556184234514777 -0.98847817793877035 0 -0.98897082007369519 -2.4561468946027169e-05 0.14811048727047271 0
		 14.087671279907227 8.2376375198364258 -0.99425750970840454 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".filmboxTypeID" -type "string" "5";
createNode joint -n "cloth_ik_foot_r" -p "cloth_ik_foot_root";
	rename -uid "99598E95-4DAA-69B8-FA31-E59D647258D7";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "filmboxTypeID" -ln "filmboxTypeID" -dt "string";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" -14.087558779746487 0.9848343479286823 8.2382316520997634 ;
	setAttr ".r" -type "double3" -89.955404360215582 88.191663071784689 81.527131053351084 ;
	setAttr ".s" -type "double3" 1 0.99999999999999956 0.99999999999999978 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.0046495233472998443 -0.99950197930433915 -0.031211781419062286 0
		 -0.14803749178979106 -0.031556184234514978 0.9884781779387668 0 -0.98897082007369153 2.4561468946249214e-05 -0.14811048727049611 0
		 -14.087558779746487 8.2382316520997634 -0.9848343479286823 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".filmboxTypeID" -type "string" "5";
createNode joint -n "cloth_ik_hand_root" -p "cloth_root";
	rename -uid "A6F34401-42D0-123F-7258-4EA49CFCE5FB";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "filmboxTypeID" -ln "filmboxTypeID" -dt "string";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 0 -1 0 0 1 0 0 0 0 0 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".filmboxTypeID" -type "string" "5";
createNode joint -n "cloth_ik_hand_gun" -p "cloth_ik_hand_root";
	rename -uid "2FB76E93-4110-54F6-60C8-19B72C45F0E3";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "filmboxTypeID" -ln "filmboxTypeID" -dt "string";
	setAttr ".uoc" 1;
	setAttr ".oc" 2;
	setAttr ".t" -type "double3" -47.768318701942526 -15.698805157589947 104.46642994530568 ;
	setAttr ".r" -type "double3" 68.473107352748798 -39.41011191123917 53.666512015145315 ;
	setAttr ".s" -type "double3" 0.99999999999999978 0.99999999999999978 1 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.45776599577967636 0.6348668800858086 -0.62241010409371778 0
		 -0.64550907895177212 0.71872766671258748 0.25835744636591057 0 0.61136594777487885 0.28350411932102693 0.73882142106826676 0
		 -47.768318701942526 104.46642994530568 15.698805157589947 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".filmboxTypeID" -type "string" "5";
createNode joint -n "cloth_ik_hand_l" -p "cloth_ik_hand_gun";
	rename -uid "1FAA56A9-4B45-DCEE-FE33-9A91CF806766";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "filmboxTypeID" -ln "filmboxTypeID" -dt "string";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" 43.73357009887696 -61.669849395751982 58.408111572265597 ;
	setAttr ".r" -type "double3" -107.73758596138391 -34.036790747396616 -134.50699481505316 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.45776611850929994 -0.63486684401641602 0.62241005062062216 0
		 -0.6455090524996141 -0.71872771757507337 -0.25835737096196021 0 0.61136588380934331 -0.28350407114883097 -0.73882149248384688 0
		 47.768600735035555 104.46653841876764 15.698888426036399 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".filmboxTypeID" -type "string" "5";
createNode joint -n "cloth_ik_hand_r" -p "cloth_ik_hand_gun";
	rename -uid "C955BE9C-45E6-94C2-9B6C-97AA91E64A38";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -is true -ci true -k true -sn "filmboxTypeID" -ln "filmboxTypeID" -dt "string";
	setAttr ".uoc" 1;
	setAttr ".oc" 3;
	setAttr ".t" -type "double3" -7.1054273576010019e-15 0 7.1054273576010019e-15 ;
	setAttr ".r" -type "double3" 3.3395824155366921e-14 -2.2263882770244611e-14 0 ;
	setAttr ".s" -type "double3" 1.0000000000000002 1.0000000000000002 1 ;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 0.45776599577967647 0.63486688008580872 -0.62241010409371789 0
		 -0.64550907895177223 0.71872766671258759 0.25835744636591063 0 0.61136594777487885 0.28350411932102693 0.73882142106826676 0
		 -47.768318701942526 104.46642994530568 15.698805157589955 1;
	setAttr ".radi" 3;
	setAttr -k on ".liw";
	setAttr -k on ".filmboxTypeID" -type "string" "5";
createNode joint -n "cloth_interaction" -p "cloth_root";
	rename -uid "A1496504-4336-D106-FCCD-A881C6D70EDD";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 0 -1 0 0 1 0 0 0 0 0 1;
	setAttr ".radi" 3;
	setAttr ".fbxID" 5;
createNode joint -n "cloth_center_of_mass" -p "cloth_root";
	rename -uid "90D2EF59-4597-B6BB-4DBC-E08C8054C47A";
	addAttr -is true -ci true -k true -sn "liw" -ln "lockInfluenceWeights" -min 0 -max 
		1 -at "bool";
	addAttr -ci true -h true -sn "fbxID" -ln "filmboxTypeID" -at "short";
	setAttr ".uoc" 1;
	setAttr ".oc" 1;
	setAttr ".ssc" no;
	setAttr ".bps" -type "matrix" 1 0 0 0 0 0 -1 0 0 1 0 0 0 0 0 1;
	setAttr ".radi" 3;
	setAttr ".fbxID" 5;
createNode transform -n "Ctrl_GRP" -p "cloth_trench_coat_A";
	rename -uid "B2979476-4ED9-8D08-EAFA-DCAC2D114028";
createNode transform -n "cloth_fit_ctrl" -p "Ctrl_GRP";
	rename -uid "B6F23EB9-4794-4460-9EC9-189A040802DF";
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
	rename -uid "56DC34FE-4883-1768-EF2A-0A9413111316";
	addAttr -ci true -k true -sn "swing" -ln "swing" -min -10 -max 10 -at "double";
createNode transform -n "cloth_fit_ffdLattice" -p "Ctrl_GRP";
	rename -uid "6341BAE4-4A57-150D-DD92-49BF9BD43899";
	setAttr ".t" -type "double3" 0 99.5 0 ;
createNode lattice -n "cloth_fit_ffdLatticeShape" -p "cloth_fit_ffdLattice";
	rename -uid "98C6DB4F-48DD-8043-0510-EDA093CF519A";
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
	rename -uid "894BFEC8-48F1-75E9-FC3A-558545B808E2";
	setAttr ".t" -type "double3" 0 99.5 0 ;
	setAttr ".s" -type "double3" 52 103 32 ;
createNode baseLattice -n "cloth_fit_ffdBaseShape" -p "cloth_fit_ffdBase";
	rename -uid "06D69420-4E90-1F56-615E-4A834553EC2E";
	setAttr ".ihi" 0;
	setAttr -k off ".v";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "47E1647B-4922-057E-1618-8D988F271B68";
	setAttr -s 3 ".lnk";
	setAttr -s 3 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "23851381-4CD3-0DD7-4A12-97BFB71E36A5";
	setAttr ".bsdt[0].bscd" -type "Int32Array" 0 ;
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "55138471-40E2-FDEE-5B14-3DBD8F0693DB";
createNode displayLayerManager -n "layerManager";
	rename -uid "C20C72F1-4ACC-5DFF-48C8-05839C4F9CBB";
	setAttr -s 4 ".dli[1:3]"  5 6 4;
createNode displayLayer -n "defaultLayer";
	rename -uid "0CF7200D-4548-13E8-3DD4-2CADCE928439";
	setAttr ".ufem" -type "stringArray" 0  ;
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "D4ACC4C3-43D1-4110-C34D-3DBD3E54F799";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "C21E545A-414A-16BE-C539-ABB437960D19";
	setAttr ".g" yes;
createNode skinCluster -n "cloth_jacket_mesh_skinCluster";
	rename -uid "2E550914-4CF7-0A75-920D-E4828300BCC4";
	setAttr -s 8 ".wl";
	setAttr ".wl[0:7].w"
		2 20 0.49601822308083882 21 0.50398177691916124
		2 17 0.4960275912850548 18 0.5039724087149452
		2 13 0.42830795389875626 14 0.57169204610124369
		2 9 0.42829987730925861 10 0.57170012269074133
		2 13 0.40097049618319647 14 0.59902950381680364
		2 9 0.40095924484092255 10 0.59904075515907751
		2 20 0.48126157264973146 21 0.51873842735026854
		2 17 0.48126126472156544 18 0.5187387352784345;
	setAttr -s 23 ".pm";
	setAttr ".pm[0]" -type "matrix" 1 -0 0 -0 -0 0 1 0 0 -1 0 -0 -0 0 -0 1;
	setAttr ".pm[1]" -type "matrix" 0 -0 -1 -0 0.99799027986901856 -0.063367194090933832 -0 0
		 -0.063367194090933832 -0.99799027986901845 -0 0 -95.559524140488392 8.3529922361862461 -3.4314998759166191e-17 1;
	setAttr ".pm[2]" -type "matrix" 0 -0 -1 -0 0.98220797016103423 0.18779644126591274 -0 -0
		 0.18779644126591269 -0.98220797016103434 0 -0 -98.179537472967283 -16.686798167121527 4.3202194641745911e-16 1;
	setAttr ".pm[3]" -type "matrix" 0 -0 -1 -0 0.99176140629857157 0.12809884065314286 -0 -0
		 0.12809884065314273 -0.99176140629857212 0 -0 -105.79112581470949 -10.312733827340098 2.464277070461987e-16 1;
	setAttr ".pm[4]" -type "matrix" 0 -0 -1 -0 0.99804167658749499 -0.06255247232861065 -0 0
		 -0.062552472328610872 -0.99804167658749565 0 0 -112.93116808215228 11.337483986926687 1.2350709678254855e-16 1;
	setAttr ".pm[5]" -type "matrix" 6.3527471044072554e-22 -7.8457562567302111e-06 -0.9999999999692214 -0
		 0.98641974755132833 -0.16424396987138817 1.288618154288311e-06 0 -0.16424396987644352 -0.98641974752096928 7.7392089061130639e-06 0
		 -119.65995581271686 23.693152323860154 -0.00018589069809243761 1;
	setAttr ".pm[6]" -type "matrix" -1.8296475371099055e-13 1.5895229578183344e-11 -0.99999999999999822 -0
		 0.98439676970875822 -0.17596306370077866 -2.977083210447581e-12 0 -0.17596306370077908 -0.98439676970875833 -1.5615017627392218e-11 0
		 -138.80815577827536 25.345680206388355 4.2885887825513599e-10 1;
	setAttr ".pm[7]" -type "matrix" -6.6142615155427607e-12 1.4454872674924001e-11 -0.99999999999999645 -0
		 0.9711605157890687 0.2384266188417577 -2.977083210447575e-12 -0 0.23842661884175784 -0.97116051578906704 -1.5615017627392192e-11 -0
		 -148.02413413726174 -37.954183218738685 1.6566657969204642e-10 1;
	setAttr ".pm[8]" -type "matrix" -6.1279080694971842e-12 1.7098227286056741e-06 -0.99999999999853484 -0
		 0.97858030038111343 0.20586547963631172 3.5198747946786747e-07 -0 0.20586547963661278 -0.97858030037968147 -1.6732001008821478e-06 -0
		 -154.316334197456 -32.819682332318578 -5.6115191701459429e-05 1;
	setAttr ".pm[9]" -type "matrix" 0.98722325287427792 -0.045885930423861 0.1525933497026038 -0
		 -0.15258975006428868 0.0036018072398129259 0.98828305417017459 0 -0.045897899294439652 -0.99894019259100097 -0.0034459347953304364 -0
		 20.834526670557953 -2.1993972347445525 -144.81073304722486 1;
	setAttr ".pm[10]" -type "matrix" 0.57603356952398499 -0.032592099667534534 0.8167760291663273 -0
		 -0.81709064461042369 -0.051578496259220265 0.57419729815958043 0 0.023413783794530463 -0.99813697144374924 -0.056341645037431574 -0
		 106.43028050739402 5.4729237755595985 -98.116150031117613 1;
	setAttr ".pm[11]" -type "matrix" 0.46829763423518361 0.3370077802499718 0.81677602916632508 -0
		 -0.60274413661567516 -0.55407307150020058 0.57419729815957887 0 0.64606256008621854 -0.7612021988206028 -0.056341645037431422 -0
		 57.705276887976943 53.733736463206327 -98.116150031097064 1;
	setAttr ".pm[12]" -type "matrix" 0.45776605878179005 -0.64550904927599539 0.61136593193453126 -0
		 -0.63486684214115996 -0.71872770835154531 -0.28350409873130683 0 0.62241009646141454 -0.25835740467525004 -0.73882144207674649 -0
		 34.684346968063174 109.97398405992759 12.011274705912221 1;
	setAttr ".pm[13]" -type "matrix" 0.98722325283077272 -0.045885930607882118 0.15259334992873019 -0
		 0.15258975029080937 -0.003601807250348919 -0.98828305413516127 0 0.045897899477120203 0.99894019258250955 0.0034459348235595629 -0
		 -20.834547722968775 2.1994343634427658 144.81067317131041 1;
	setAttr ".pm[14]" -type "matrix" 0.57603356999186395 -0.032592099840372868 0.81677602882945388 -0
		 0.81709064430417044 0.051578495414514702 -0.57419729867125979 0 -0.023413782971299882 0.99813697148175728 0.05634164470622785 -0
		 -106.4298671294853 -5.4728615541620877 98.115865208557693 1;
	setAttr ".pm[15]" -type "matrix" 0.46829763471056507 0.33700778040583573 0.81677602882944833 -0
		 0.6027441369137837 0.55407307064564126 -0.57419729867125591 0 -0.64606255946352253 0.76120219937362676 0.056341644706227365 -0
		 -57.705340153147034 -53.733707614711726 98.115865208576835 1;
	setAttr ".pm[16]" -type "matrix" 0.45776605882155996 -0.64550904801159392 0.61136593323975885 -0
		 0.63486684161598816 0.71872770916351825 0.28350409784887387 0 -0.62241009696786076 0.25835740557549908 0.73882144133529504 -0
		 -34.684464732749603 -109.97370509752776 -12.011353112818471 1;
	setAttr ".pm[17]" -type "matrix" -0.054523896494900817 -0.14601293301636586 -0.98777900772539795 -0
		 0.99851165611282855 -0.0092329896063863565 -0.053751507046270457 0 -0.0012717381138594513 -0.989239594484009 0.14629903412970005 0
		 -92.856783672621262 4.8325716316356502 14.503748902458604 1;
	setAttr ".pm[18]" -type "matrix" -0.04157784933783315 -0.15021289672151608 -0.98777900772539795 0
		 0.99551014127010251 0.077912348948265125 -0.053751507046270457 0 0.08503435231023948 -0.98557889158600354 0.14629903412970008 -0
		 -49.748282097691757 0.49441753638829899 14.503749531360951 1;
	setAttr ".pm[19]" -type "matrix" 0.14803750041703412 0.0046495256006482168 -0.98897081877169912 -0
		 -0.031556184277059605 0.99950197930304507 -2.4559473288879821e-05 0 0.98847817664536664 0.031211781124831476 0.14811049596455594 -0
		 -16.080342813662071 -1.2585637349298706 13.540870618474111 1;
	setAttr ".pm[20]" -type "matrix" -0.054523896494896425 -0.14601293301635637 -0.98777900772539962 0
		 -0.99851165611282866 0.0092329896063877131 0.053751507046265828 0 0.0012717381138619736 0.98923959448401055 -0.14629903412969064 -0
		 92.85736035199244 -4.8418852990295322 -14.502291032863109 1;
	setAttr ".pm[21]" -type "matrix" -0.041577849337829674 -0.15021289672150617 -0.98777900772539939 0
		 -0.99551014127010273 -0.077912348948263307 0.053751507046265815 0 -0.085034352310236649 0.98557889158600509 -0.14629903412969061 -0
		 49.749714713501866 -0.50364149517261692 -14.502291661764847 1;
	setAttr ".pm[22]" -type "matrix" 0.14803750010489677 0.0046495399395140675 -0.98897081875101034 -0
		 0.03155618427706753 -0.99950197930340179 2.4544971774410565e-05 0 -0.98847817669211324 -0.031211778977410884 -0.14811049610510663 0
		 16.089627673547508 1.2594520580534296 -13.539305421044347 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr -s 23 ".ma";
	setAttr -s 23 ".dpf[0:22]"  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 
		4 4 4;
	setAttr -s 23 ".lw";
	setAttr -s 23 ".lw";
	setAttr ".ucm" yes;
	setAttr -s 23 ".ifcl";
	setAttr -s 23 ".ifcl";
createNode dagPose -n "bindPose1";
	rename -uid "205BF171-4401-9925-577D-248D20814FD3";
	setAttr -s 26 ".wm";
	setAttr ".wm[0]" -type "matrix" 1 0 0 0 0 0 -1 0 0 1 0 0 0 0 0 1;
	setAttr -s 26 ".xm";
	setAttr ".xm[0]" -type "matrix" "xform" 1 1 1 -1.5707963267948966 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xm[1]" -type "matrix" "xform" 1 1 1 0 -0 0 0 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 no;
	setAttr ".xm[2]" -type "matrix" "xform" 1 1 1 1.5707963267948966 -1.6342060051489202
		 -1.5707963267948966 0 -3.4314998759166197e-17 -2.280866146087646 95.896781921386719 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 no;
	setAttr ".xm[3]" -type "matrix" "xform" 0.99999999999999989 0.99999999999999967 0.99999999999999989 0
		 0 -0.25232786692436682 0 3.6770534515378444 3.1974423109204508e-14 -4.6633694517662523e-16 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 no;
	setAttr ".xm[4]" -type "matrix" "xform" 1.0000000000000004 1 1 0 0 0.060466399756961678 0 6.7950572967531286
		 9.5923269327613525e-14 1.8559423937126041e-16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 
		0 0 0 1 1.0000000000000002 1.0000000000000004 1.0000000000000002 no;
	setAttr ".xm[5]" -type "matrix" "xform" 1 0.99999999999999978 1.0000000000000002 0
		 0 0.19104512581130348 0 7.2382278442387076 -7.1054273576010019e-15 1.2292061026365013e-16 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0.99999999999999956 1 1 no;
	setAttr ".xm[6]" -type "matrix" "xform" 0.99999999999999967 0.99999999999999933 1.0000000000000007 7.8457562568107029e-06
		 5.2939559203393771e-23 0.10239818677280682 0 8.5238933563226595 5.8619775700208265e-14
		 2.5231056665821328e-16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1.0000000000000002
		 0.99999999999999978 no;
	setAttr ".xm[7]" -type "matrix" "xform" 0.99999999999999911 1 1.0000000000000013 -7.8452173409580532e-06
		 9.3303178305776931e-08 0.011892487809487262 0 19.439800262451271 -1.7817315622892238e-07
		 8.1130227861346549e-13 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000004
		 1.0000000000000007 0.99999999999999933 no;
	setAttr ".xm[8]" -type "matrix" "xform" 0.99999999999999933 1.0000000000000013 1.0000000000000016 0
		 0 -0.4176294354607929 0 11.887765884399784 0 2.6319229856308895e-10 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000009 1 0.99999999999999867 no;
	setAttr ".xm[9]" -type "matrix" "xform" 1 0.99999999999999989 1 -1.7098080609365503e-06
		 3.3087224502121107e-24 0.033397375038361002 0 5.1102595329284384 -5.6843418860808015e-14
		 -4.1190754661076901e-14 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000007
		 0.99999999999999867 0.99999999999999845 no;
	setAttr ".xm[10]" -type "matrix" "xform" 1.0000000000000004 1.0000000000000002 0.99999999999999944 -0.29210554464513727
		 1.7308216232549485 -0.46906799353374229 0 5.5162687301644269 1.314766049384982
		 -1.4279042482530175 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000009
		 1 0.99999999999999867 no;
	setAttr ".xm[11]" -type "matrix" "xform" 1.0000000000000007 1.0000000000000004 0.99999999999999922 -0.075700957924171086
		 0.80336814723004535 -0.076070503912366 0 17.809522630964835 2.0104402587151071e-09
		 -9.8569330475584138e-09 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0.99999999999999956
		 0.99999999999999978 1.0000000000000007 no;
	setAttr ".xm[12]" -type "matrix" "xform" 0.99999999999999778 0.99999999999999978
		 1.0000000000000027 2.6841645307943638e-15 5.068314048460434e-11 -0.68030878143872042 0 27.771139141657912
		 2.975206747635184e-09 -2.0293100533308461e-11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 
		0 0 0 1 0.99999999999999933 0.99999999999999956 1.0000000000000009 no;
	setAttr ".xm[13]" -type "matrix" "xform" 0.99999999999999745 1.0000000000000007 1.0000000000000029 -1.1828228781933166
		 0.025716924990360508 0.032269679353906622 0 27.251073837279947 1.9184653865522705e-13
		 -9.9475983006414026e-14 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000022
		 1.0000000000000002 0.99999999999999734 no;
	setAttr ".xm[14]" -type "matrix" "xform" 1.0000000000000004 1.0000000000000004 0.99999999999999967 -0.29210554516550502
		 1.7308216235132798 2.6725246595423244 0 5.5162200927734943 1.3148112297058177
		 1.4278726577604703 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000009
		 1 0.99999999999999867 no;
	setAttr ".xm[15]" -type "matrix" "xform" 0.99999999999999833 0.99999999999999867
		 1.0000000000000051 -0.075700956662968596 0.80336814645932197 -0.076070502858260905 0 -17.809625627817226
		 2.8800139744156183e-06 0.00043809145546447326 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 
		0 0 0 1 0.99999999999999956 0.99999999999999956 1.0000000000000004 no;
	setAttr ".xm[16]" -type "matrix" "xform" 0.99999999999999734 0.99999999999999978
		 1.0000000000000069 4.8291249324894507e-16 5.2340113417973463e-11 -0.68030878142999374 0 -27.77069472947035
		 -2.9770230725034708e-09 -1.9809931472991593e-11 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 
		0 0 0 1 1.0000000000000018 1.0000000000000013 0.99999999999999489 no;
	setAttr ".xm[17]" -type "matrix" "xform" 0.99999999999999167 1.0000000000000016 1.0000000000000051 -1.1828228771829465
		 0.025716924957761858 0.03226967787414059 0 -27.251010894784763 4.5150017058404046e-10
		 8.5265128291212022e-14 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000027
		 1.0000000000000002 0.99999999999999312 no;
	setAttr ".xm[18]" -type "matrix" "xform" 1 1 1 0.14675668474062881 -0.054550947975289206
		 -0.062136045323875504 0 -2.3657112121585016 -0.11004376411435146 -9.9692029953002965 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 no;
	setAttr ".xm[19]" -type "matrix" "xform" 0.99999999999999967 0.99999999999999967
		 0.99999999999999989 -1.1059915819157448e-16 -9.6869242639456061e-18 -0.087351021188367114 0 -43.341308593749915
		 5.0636828952121959e-08 -6.2890234886481267e-07 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 
		0 0 0 1 1 1 1 no;
	setAttr ".xm[20]" -type "matrix" "xform" 1.0000000000000004 1.0000000000000011 1.0000000000000004 -8.1377274568131947e-05
		 0.05377710464589068 0.046497403907432337 0 -42.217914581298857 -1.6758482623835391e-07
		 -6.1026572595324069e-07 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000004
		 1.0000000000000004 1.0000000000000002 no;
	setAttr ".xm[21]" -type "matrix" "xform" 0.99999999999999933 0.99999999999999989
		 0.99999999999999989 -9.4878274911707264e-14 6.2798960481819756e-11 -1.5707963279615351 0 -7.0094366386041802
		 -15.23758886698478 0.53888747195568421 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 0.99999999999999956
		 0.99999999999999889 0.99999999999999956 no;
	setAttr ".xm[22]" -type "matrix" "xform" 1 0.99999999999999989 1 0.14675668474061915
		 -0.054550947975284814 3.0794566082659203 0 -2.3657262325289707 -0.11948779225345163
		 9.9690914154052237 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 no;
	setAttr ".xm[23]" -type "matrix" "xform" 0.99999999999999967 0.99999999999999989
		 1 -1.1059703685001454e-16 -9.6869640295423818e-18 -0.08735102118836667 0 43.341262817382805
		 5.4167897722834368e-08 6.2890173602170307e-07 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 
		0 0 0 1 1 1.0000000000000002 1 no;
	setAttr ".xm[24]" -type "matrix" "xform" 1 1.0000000000000002 0.99999999999999978 -8.137786805690956e-05
		 0.053777119144241756 0.046497398737684471 0 42.217948913574233 3.1899732444440332e-07
		 2.805366605684867e-09 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1.0000000000000004
		 1.0000000000000002 1 no;
	setAttr ".xm[25]" -type "matrix" "xform" 0.99999999999999978 0.99999999999999978
		 1.0000000000000002 1.4498262577961491e-08 6.5458201671724568e-10 -1.5707963228004427 0 7.0094366762781988
		 15.237594510952334 -0.5389449035161018 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1
		 0.99999999999999978 1.0000000000000002 no;
	setAttr -s 26 ".m";
	setAttr -s 26 ".p";
	setAttr -s 26 ".g[0:25]" yes no no no no no no no no no no no no no 
		no no no no no no yes no no no yes no;
	setAttr ".bp" yes;
createNode skinCluster -n "cloth_collar_mesh_skinCluster";
	rename -uid "A6DD3322-426C-3BAB-7603-9895B218EBAE";
	setAttr -s 8 ".wl";
	setAttr ".wl[0:7].w"
		2 13 0.56591076207833391 14 0.43408923792166609
		2 9 0.56591032715603917 10 0.43408967284396077
		2 13 0.59215817169649243 14 0.40784182830350751
		2 9 0.59215426268584626 10 0.40784573731415374
		2 13 0.58960023766272152 14 0.41039976233727854
		2 9 0.58959522291620237 10 0.41040477708379769
		2 13 0.56232358495464285 14 0.43767641504535709
		2 9 0.56232193487827387 10 0.43767806512172619;
	setAttr -s 23 ".pm";
	setAttr ".pm[0]" -type "matrix" 1 -0 0 -0 -0 0 1 0 0 -1 0 -0 -0 0 -0 1;
	setAttr ".pm[1]" -type "matrix" 0 -0 -1 -0 0.99799027986901856 -0.063367194090933832 -0 0
		 -0.063367194090933832 -0.99799027986901845 -0 0 -95.559524140488392 8.3529922361862461 -3.4314998759166191e-17 1;
	setAttr ".pm[2]" -type "matrix" 0 -0 -1 -0 0.98220797016103423 0.18779644126591274 -0 -0
		 0.18779644126591269 -0.98220797016103434 0 -0 -98.179537472967283 -16.686798167121527 4.3202194641745911e-16 1;
	setAttr ".pm[3]" -type "matrix" 0 -0 -1 -0 0.99176140629857157 0.12809884065314286 -0 -0
		 0.12809884065314273 -0.99176140629857212 0 -0 -105.79112581470949 -10.312733827340098 2.464277070461987e-16 1;
	setAttr ".pm[4]" -type "matrix" 0 -0 -1 -0 0.99804167658749499 -0.06255247232861065 -0 0
		 -0.062552472328610872 -0.99804167658749565 0 0 -112.93116808215228 11.337483986926687 1.2350709678254855e-16 1;
	setAttr ".pm[5]" -type "matrix" 6.3527471044072554e-22 -7.8457562567302111e-06 -0.9999999999692214 -0
		 0.98641974755132833 -0.16424396987138817 1.288618154288311e-06 0 -0.16424396987644352 -0.98641974752096928 7.7392089061130639e-06 0
		 -119.65995581271686 23.693152323860154 -0.00018589069809243761 1;
	setAttr ".pm[6]" -type "matrix" -1.8296475371099055e-13 1.5895229578183344e-11 -0.99999999999999822 -0
		 0.98439676970875822 -0.17596306370077866 -2.977083210447581e-12 0 -0.17596306370077908 -0.98439676970875833 -1.5615017627392218e-11 0
		 -138.80815577827536 25.345680206388355 4.2885887825513599e-10 1;
	setAttr ".pm[7]" -type "matrix" -6.6142615155427607e-12 1.4454872674924001e-11 -0.99999999999999645 -0
		 0.9711605157890687 0.2384266188417577 -2.977083210447575e-12 -0 0.23842661884175784 -0.97116051578906704 -1.5615017627392192e-11 -0
		 -148.02413413726174 -37.954183218738685 1.6566657969204642e-10 1;
	setAttr ".pm[8]" -type "matrix" -6.1279080694971842e-12 1.7098227286056741e-06 -0.99999999999853484 -0
		 0.97858030038111343 0.20586547963631172 3.5198747946786747e-07 -0 0.20586547963661278 -0.97858030037968147 -1.6732001008821478e-06 -0
		 -154.316334197456 -32.819682332318578 -5.6115191701459429e-05 1;
	setAttr ".pm[9]" -type "matrix" 0.98722325287427792 -0.045885930423861 0.1525933497026038 -0
		 -0.15258975006428868 0.0036018072398129259 0.98828305417017459 0 -0.045897899294439652 -0.99894019259100097 -0.0034459347953304364 -0
		 20.834526670557953 -2.1993972347445525 -144.81073304722486 1;
	setAttr ".pm[10]" -type "matrix" 0.57603356952398499 -0.032592099667534534 0.8167760291663273 -0
		 -0.81709064461042369 -0.051578496259220265 0.57419729815958043 0 0.023413783794530463 -0.99813697144374924 -0.056341645037431574 -0
		 106.43028050739402 5.4729237755595985 -98.116150031117613 1;
	setAttr ".pm[11]" -type "matrix" 0.46829763423518361 0.3370077802499718 0.81677602916632508 -0
		 -0.60274413661567516 -0.55407307150020058 0.57419729815957887 0 0.64606256008621854 -0.7612021988206028 -0.056341645037431422 -0
		 57.705276887976943 53.733736463206327 -98.116150031097064 1;
	setAttr ".pm[12]" -type "matrix" 0.45776605878179005 -0.64550904927599539 0.61136593193453126 -0
		 -0.63486684214115996 -0.71872770835154531 -0.28350409873130683 0 0.62241009646141454 -0.25835740467525004 -0.73882144207674649 -0
		 34.684346968063174 109.97398405992759 12.011274705912221 1;
	setAttr ".pm[13]" -type "matrix" 0.98722325283077272 -0.045885930607882118 0.15259334992873019 -0
		 0.15258975029080937 -0.003601807250348919 -0.98828305413516127 0 0.045897899477120203 0.99894019258250955 0.0034459348235595629 -0
		 -20.834547722968775 2.1994343634427658 144.81067317131041 1;
	setAttr ".pm[14]" -type "matrix" 0.57603356999186395 -0.032592099840372868 0.81677602882945388 -0
		 0.81709064430417044 0.051578495414514702 -0.57419729867125979 0 -0.023413782971299882 0.99813697148175728 0.05634164470622785 -0
		 -106.4298671294853 -5.4728615541620877 98.115865208557693 1;
	setAttr ".pm[15]" -type "matrix" 0.46829763471056507 0.33700778040583573 0.81677602882944833 -0
		 0.6027441369137837 0.55407307064564126 -0.57419729867125591 0 -0.64606255946352253 0.76120219937362676 0.056341644706227365 -0
		 -57.705340153147034 -53.733707614711726 98.115865208576835 1;
	setAttr ".pm[16]" -type "matrix" 0.45776605882155996 -0.64550904801159392 0.61136593323975885 -0
		 0.63486684161598816 0.71872770916351825 0.28350409784887387 0 -0.62241009696786076 0.25835740557549908 0.73882144133529504 -0
		 -34.684464732749603 -109.97370509752776 -12.011353112818471 1;
	setAttr ".pm[17]" -type "matrix" -0.054523896494900817 -0.14601293301636586 -0.98777900772539795 -0
		 0.99851165611282855 -0.0092329896063863565 -0.053751507046270457 0 -0.0012717381138594513 -0.989239594484009 0.14629903412970005 0
		 -92.856783672621262 4.8325716316356502 14.503748902458604 1;
	setAttr ".pm[18]" -type "matrix" -0.04157784933783315 -0.15021289672151608 -0.98777900772539795 0
		 0.99551014127010251 0.077912348948265125 -0.053751507046270457 0 0.08503435231023948 -0.98557889158600354 0.14629903412970008 -0
		 -49.748282097691757 0.49441753638829899 14.503749531360951 1;
	setAttr ".pm[19]" -type "matrix" 0.14803750041703412 0.0046495256006482168 -0.98897081877169912 -0
		 -0.031556184277059605 0.99950197930304507 -2.4559473288879821e-05 0 0.98847817664536664 0.031211781124831476 0.14811049596455594 -0
		 -16.080342813662071 -1.2585637349298706 13.540870618474111 1;
	setAttr ".pm[20]" -type "matrix" -0.054523896494896425 -0.14601293301635637 -0.98777900772539962 0
		 -0.99851165611282866 0.0092329896063877131 0.053751507046265828 0 0.0012717381138619736 0.98923959448401055 -0.14629903412969064 -0
		 92.85736035199244 -4.8418852990295322 -14.502291032863109 1;
	setAttr ".pm[21]" -type "matrix" -0.041577849337829674 -0.15021289672150617 -0.98777900772539939 0
		 -0.99551014127010273 -0.077912348948263307 0.053751507046265815 0 -0.085034352310236649 0.98557889158600509 -0.14629903412969061 -0
		 49.749714713501866 -0.50364149517261692 -14.502291661764847 1;
	setAttr ".pm[22]" -type "matrix" 0.14803750010489677 0.0046495399395140675 -0.98897081875101034 -0
		 0.03155618427706753 -0.99950197930340179 2.4544971774410565e-05 0 -0.98847817669211324 -0.031211778977410884 -0.14811049610510663 0
		 16.089627673547508 1.2594520580534296 -13.539305421044347 1;
	setAttr ".gm" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr -s 23 ".ma";
	setAttr -s 23 ".dpf[0:22]"  4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 
		4 4 4;
	setAttr -s 23 ".lw";
	setAttr -s 23 ".lw";
	setAttr ".ucm" yes;
	setAttr -s 23 ".ifcl";
	setAttr -s 23 ".ifcl";
createNode ffd -n "cloth_fit_ffd";
	rename -uid "C8D86120-4011-1C45-8B78-CEB40862C221";
	setAttr -s 2 ".ip";
	setAttr -s 2 ".og";
	setAttr -s 2 ".orggeom";
createNode animCurveUU -n "cloth_fit_ffdLattice_scaleX";
	rename -uid "06C5296B-4B1A-9D31-1F8F-9EB87C3FC3C3";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -1 56.160000000000004 0 52 1 47.84;
createNode animCurveUU -n "cloth_fit_ffdLattice_scaleZ";
	rename -uid "54020480-4209-F675-EBFF-A6A31DE83B76";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -1 34.56 0 32 1 29.44;
createNode animCurveUU -n "cloth_fit_ffdLattice_scaleY";
	rename -uid "DC07A89B-4A78-EC87-5971-1A87D36CBAF9";
	setAttr ".tan" 18;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -1 92.7 0 103 1 113.30000000000001;
createNode network -n "cloth_info";
	rename -uid "69AF078F-45FC-23C9-7660-988A1766CAFC";
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
	rename -uid "D2AF64EF-47A1-D6D6-78B6-CA9D214B0597";
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
		+ "            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -bluePencil 1\n            -greasePencils 0\n            -excludeObjectPreset \"All\" \n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1371\n            -height 804\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n"
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
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -bluePencil 1\\n    -greasePencils 0\\n    -excludeObjectPreset \\\"All\\\" \\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1371\\n    -height 804\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"smoothShaded\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 0\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 1\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -bluePencil 1\\n    -greasePencils 0\\n    -excludeObjectPreset \\\"All\\\" \\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 1371\\n    -height 804\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "F62FA64C-46D8-4F32-101C-E8B825342023";
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
connectAttr "cloth_jacket_mesh_skinCluster.og[0]" "cloth_jacket_meshShape.i";
connectAttr "cloth_collar_mesh_skinCluster.og[0]" "cloth_collar_meshShape.i";
connectAttr "cloth_root.s" "cloth_pelvis.is";
connectAttr "cloth_pelvis.s" "cloth_spine_01.is";
connectAttr "cloth_spine_01.s" "cloth_spine_02.is";
connectAttr "cloth_spine_02.s" "cloth_spine_03.is";
connectAttr "cloth_spine_03.s" "cloth_spine_04.is";
connectAttr "cloth_spine_04.s" "cloth_spine_05.is";
connectAttr "cloth_spine_05.s" "cloth_neck_01.is";
connectAttr "cloth_neck_01.s" "cloth_neck_02.is";
connectAttr "cloth_neck_02.s" "cloth_head.is";
connectAttr "cloth_spine_05.s" "cloth_clavicle_l.is";
connectAttr "cloth_clavicle_l.s" "cloth_upperarm_l.is";
connectAttr "cloth_upperarm_l.s" "cloth_lowerarm_l.is";
connectAttr "cloth_lowerarm_l.s" "cloth_lowerarm_twist_02_l.is";
connectAttr "cloth_lowerarm_l.s" "cloth_lowerarm_twist_01_l.is";
connectAttr "cloth_lowerarm_l.s" "cloth_hand_l.is";
connectAttr "cloth_hand_l.s" "cloth_index_metacarpal_l.is";
connectAttr "cloth_index_metacarpal_l.s" "cloth_index_01_l.is";
connectAttr "cloth_index_01_l.s" "cloth_index_02_l.is";
connectAttr "cloth_index_02_l.s" "cloth_index_03_l.is";
connectAttr "cloth_hand_l.s" "cloth_middle_metacarpal_l.is";
connectAttr "cloth_middle_metacarpal_l.s" "cloth_middle_01_l.is";
connectAttr "cloth_middle_01_l.s" "cloth_middle_02_l.is";
connectAttr "cloth_middle_02_l.s" "cloth_middle_03_l.is";
connectAttr "cloth_hand_l.s" "cloth_thumb_01_l.is";
connectAttr "cloth_thumb_01_l.s" "cloth_thumb_02_l.is";
connectAttr "cloth_thumb_02_l.s" "cloth_thumb_03_l.is";
connectAttr "cloth_hand_l.s" "cloth_pinky_metacarpal_l.is";
connectAttr "cloth_pinky_metacarpal_l.s" "cloth_pinky_01_l.is";
connectAttr "cloth_pinky_01_l.s" "cloth_pinky_02_l.is";
connectAttr "cloth_pinky_02_l.s" "cloth_pinky_03_l.is";
connectAttr "cloth_hand_l.s" "cloth_ring_metacarpal_l.is";
connectAttr "cloth_ring_metacarpal_l.s" "cloth_ring_01_l.is";
connectAttr "cloth_ring_01_l.s" "cloth_ring_02_l.is";
connectAttr "cloth_ring_02_l.s" "cloth_ring_03_l.is";
connectAttr "cloth_upperarm_l.s" "cloth_upperarm_twist_01_l.is";
connectAttr "cloth_upperarm_l.s" "cloth_upperarm_twist_02_l.is";
connectAttr "cloth_spine_05.s" "cloth_clavicle_r.is";
connectAttr "cloth_clavicle_r.s" "cloth_upperarm_r.is";
connectAttr "cloth_upperarm_r.s" "cloth_lowerarm_r.is";
connectAttr "cloth_lowerarm_r.s" "cloth_lowerarm_twist_02_r.is";
connectAttr "cloth_lowerarm_r.s" "cloth_lowerarm_twist_01_r.is";
connectAttr "cloth_lowerarm_r.s" "cloth_hand_r.is";
connectAttr "cloth_hand_r.s" "cloth_pinky_metacarpal_r.is";
connectAttr "cloth_pinky_metacarpal_r.s" "cloth_pinky_01_r.is";
connectAttr "cloth_pinky_01_r.s" "cloth_pinky_02_r.is";
connectAttr "cloth_pinky_02_r.s" "cloth_pinky_03_r.is";
connectAttr "cloth_hand_r.s" "cloth_ring_metacarpal_r.is";
connectAttr "cloth_ring_metacarpal_r.s" "cloth_ring_01_r.is";
connectAttr "cloth_ring_01_r.s" "cloth_ring_02_r.is";
connectAttr "cloth_ring_02_r.s" "cloth_ring_03_r.is";
connectAttr "cloth_hand_r.s" "cloth_middle_metacarpal_r.is";
connectAttr "cloth_middle_metacarpal_r.s" "cloth_middle_01_r.is";
connectAttr "cloth_middle_01_r.s" "cloth_middle_02_r.is";
connectAttr "cloth_middle_02_r.s" "cloth_middle_03_r.is";
connectAttr "cloth_hand_r.s" "cloth_index_metacarpal_r.is";
connectAttr "cloth_index_metacarpal_r.s" "cloth_index_01_r.is";
connectAttr "cloth_index_01_r.s" "cloth_index_02_r.is";
connectAttr "cloth_index_02_r.s" "cloth_index_03_r.is";
connectAttr "cloth_hand_r.s" "cloth_thumb_01_r.is";
connectAttr "cloth_thumb_01_r.s" "cloth_thumb_02_r.is";
connectAttr "cloth_thumb_02_r.s" "cloth_thumb_03_r.is";
connectAttr "cloth_upperarm_r.s" "cloth_upperarm_twist_01_r.is";
connectAttr "cloth_upperarm_r.s" "cloth_upperarm_twist_02_r.is";
connectAttr "cloth_spine_01.s" "cloth_coatTail_01.is";
connectAttr "cloth_coatTail_01.s" "cloth_coatTail_02.is";
connectAttr "cloth_pelvis.s" "cloth_thigh_r.is";
connectAttr "cloth_thigh_r.s" "cloth_calf_r.is";
connectAttr "cloth_calf_r.s" "cloth_GM_foot_R.is";
connectAttr "cloth_GM_foot_R.s" "cloth_ball_r.is";
connectAttr "cloth_calf_r.s" "cloth_calf_twist_02_r.is";
connectAttr "cloth_calf_r.s" "cloth_calf_twist_01_r.is";
connectAttr "cloth_thigh_r.s" "cloth_thigh_twist_01_r.is";
connectAttr "cloth_thigh_r.s" "cloth_thigh_twist_02_r.is";
connectAttr "cloth_pelvis.s" "cloth_thigh_l.is";
connectAttr "cloth_thigh_l.s" "cloth_calf_l.is";
connectAttr "cloth_calf_l.s" "cloth_GM_foot_L.is";
connectAttr "cloth_GM_foot_L.s" "cloth_ball_l.is";
connectAttr "cloth_calf_l.s" "cloth_calf_twist_02_l.is";
connectAttr "cloth_calf_l.s" "cloth_calf_twist_01_l.is";
connectAttr "cloth_thigh_l.s" "cloth_thigh_twist_01_l.is";
connectAttr "cloth_thigh_l.s" "cloth_thigh_twist_02_l.is";
connectAttr "cloth_root.s" "cloth_ik_foot_root.is";
connectAttr "cloth_ik_foot_root.s" "cloth_ik_foot_l.is";
connectAttr "cloth_ik_foot_root.s" "cloth_ik_foot_r.is";
connectAttr "cloth_root.s" "cloth_ik_hand_root.is";
connectAttr "cloth_ik_hand_root.s" "cloth_ik_hand_gun.is";
connectAttr "cloth_ik_hand_gun.s" "cloth_ik_hand_l.is";
connectAttr "cloth_ik_hand_gun.s" "cloth_ik_hand_r.is";
connectAttr "cloth_root.s" "cloth_interaction.is";
connectAttr "cloth_root.s" "cloth_center_of_mass.is";
connectAttr "cloth_fit_ffdLattice_scaleX.o" "cloth_fit_ffdLattice.sx";
connectAttr "cloth_fit_ffdLattice_scaleZ.o" "cloth_fit_ffdLattice.sz";
connectAttr "cloth_fit_ffdLattice_scaleY.o" "cloth_fit_ffdLattice.sy";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "cloth_fit_ffd.og[0]" "cloth_jacket_mesh_skinCluster.ip[0].ig";
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
connectAttr "cloth_ball_l.wm" "cloth_jacket_mesh_skinCluster.ma[19]";
connectAttr "cloth_thigh_r.wm" "cloth_jacket_mesh_skinCluster.ma[20]";
connectAttr "cloth_calf_r.wm" "cloth_jacket_mesh_skinCluster.ma[21]";
connectAttr "cloth_ball_r.wm" "cloth_jacket_mesh_skinCluster.ma[22]";
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
connectAttr "cloth_ball_l.liw" "cloth_jacket_mesh_skinCluster.lw[19]";
connectAttr "cloth_thigh_r.liw" "cloth_jacket_mesh_skinCluster.lw[20]";
connectAttr "cloth_calf_r.liw" "cloth_jacket_mesh_skinCluster.lw[21]";
connectAttr "cloth_ball_r.liw" "cloth_jacket_mesh_skinCluster.lw[22]";
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
connectAttr "cloth_ball_l.obcc" "cloth_jacket_mesh_skinCluster.ifcl[19]";
connectAttr "cloth_thigh_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[20]";
connectAttr "cloth_calf_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[21]";
connectAttr "cloth_ball_r.obcc" "cloth_jacket_mesh_skinCluster.ifcl[22]";
connectAttr "Rig_GRP.msg" "bindPose1.m[0]";
connectAttr "cloth_root.msg" "bindPose1.m[1]";
connectAttr "cloth_pelvis.msg" "bindPose1.m[2]";
connectAttr "cloth_spine_01.msg" "bindPose1.m[3]";
connectAttr "cloth_spine_02.msg" "bindPose1.m[4]";
connectAttr "cloth_spine_03.msg" "bindPose1.m[5]";
connectAttr "cloth_spine_04.msg" "bindPose1.m[6]";
connectAttr "cloth_spine_05.msg" "bindPose1.m[7]";
connectAttr "cloth_neck_01.msg" "bindPose1.m[8]";
connectAttr "cloth_neck_02.msg" "bindPose1.m[9]";
connectAttr "cloth_clavicle_l.msg" "bindPose1.m[10]";
connectAttr "cloth_upperarm_l.msg" "bindPose1.m[11]";
connectAttr "cloth_lowerarm_l.msg" "bindPose1.m[12]";
connectAttr "cloth_hand_l.msg" "bindPose1.m[13]";
connectAttr "cloth_clavicle_r.msg" "bindPose1.m[14]";
connectAttr "cloth_upperarm_r.msg" "bindPose1.m[15]";
connectAttr "cloth_lowerarm_r.msg" "bindPose1.m[16]";
connectAttr "cloth_hand_r.msg" "bindPose1.m[17]";
connectAttr "cloth_thigh_l.msg" "bindPose1.m[18]";
connectAttr "cloth_calf_l.msg" "bindPose1.m[19]";
connectAttr "cloth_GM_foot_L.msg" "bindPose1.m[20]";
connectAttr "cloth_ball_l.msg" "bindPose1.m[21]";
connectAttr "cloth_thigh_r.msg" "bindPose1.m[22]";
connectAttr "cloth_calf_r.msg" "bindPose1.m[23]";
connectAttr "cloth_GM_foot_R.msg" "bindPose1.m[24]";
connectAttr "cloth_ball_r.msg" "bindPose1.m[25]";
connectAttr "bindPose1.w" "bindPose1.p[0]";
connectAttr "bindPose1.m[0]" "bindPose1.p[1]";
connectAttr "bindPose1.m[1]" "bindPose1.p[2]";
connectAttr "bindPose1.m[2]" "bindPose1.p[3]";
connectAttr "bindPose1.m[3]" "bindPose1.p[4]";
connectAttr "bindPose1.m[4]" "bindPose1.p[5]";
connectAttr "bindPose1.m[5]" "bindPose1.p[6]";
connectAttr "bindPose1.m[6]" "bindPose1.p[7]";
connectAttr "bindPose1.m[7]" "bindPose1.p[8]";
connectAttr "bindPose1.m[8]" "bindPose1.p[9]";
connectAttr "bindPose1.m[7]" "bindPose1.p[10]";
connectAttr "bindPose1.m[10]" "bindPose1.p[11]";
connectAttr "bindPose1.m[11]" "bindPose1.p[12]";
connectAttr "bindPose1.m[12]" "bindPose1.p[13]";
connectAttr "bindPose1.m[7]" "bindPose1.p[14]";
connectAttr "bindPose1.m[14]" "bindPose1.p[15]";
connectAttr "bindPose1.m[15]" "bindPose1.p[16]";
connectAttr "bindPose1.m[16]" "bindPose1.p[17]";
connectAttr "bindPose1.m[2]" "bindPose1.p[18]";
connectAttr "bindPose1.m[18]" "bindPose1.p[19]";
connectAttr "bindPose1.m[19]" "bindPose1.p[20]";
connectAttr "bindPose1.m[20]" "bindPose1.p[21]";
connectAttr "bindPose1.m[2]" "bindPose1.p[22]";
connectAttr "bindPose1.m[22]" "bindPose1.p[23]";
connectAttr "bindPose1.m[23]" "bindPose1.p[24]";
connectAttr "bindPose1.m[24]" "bindPose1.p[25]";
connectAttr "cloth_root.bps" "bindPose1.wm[1]";
connectAttr "cloth_pelvis.bps" "bindPose1.wm[2]";
connectAttr "cloth_spine_01.bps" "bindPose1.wm[3]";
connectAttr "cloth_spine_02.bps" "bindPose1.wm[4]";
connectAttr "cloth_spine_03.bps" "bindPose1.wm[5]";
connectAttr "cloth_spine_04.bps" "bindPose1.wm[6]";
connectAttr "cloth_spine_05.bps" "bindPose1.wm[7]";
connectAttr "cloth_neck_01.bps" "bindPose1.wm[8]";
connectAttr "cloth_neck_02.bps" "bindPose1.wm[9]";
connectAttr "cloth_clavicle_l.bps" "bindPose1.wm[10]";
connectAttr "cloth_upperarm_l.bps" "bindPose1.wm[11]";
connectAttr "cloth_lowerarm_l.bps" "bindPose1.wm[12]";
connectAttr "cloth_hand_l.bps" "bindPose1.wm[13]";
connectAttr "cloth_clavicle_r.bps" "bindPose1.wm[14]";
connectAttr "cloth_upperarm_r.bps" "bindPose1.wm[15]";
connectAttr "cloth_lowerarm_r.bps" "bindPose1.wm[16]";
connectAttr "cloth_hand_r.bps" "bindPose1.wm[17]";
connectAttr "cloth_thigh_l.bps" "bindPose1.wm[18]";
connectAttr "cloth_calf_l.bps" "bindPose1.wm[19]";
connectAttr "cloth_GM_foot_L.bps" "bindPose1.wm[20]";
connectAttr "cloth_ball_l.bps" "bindPose1.wm[21]";
connectAttr "cloth_thigh_r.bps" "bindPose1.wm[22]";
connectAttr "cloth_calf_r.bps" "bindPose1.wm[23]";
connectAttr "cloth_GM_foot_R.bps" "bindPose1.wm[24]";
connectAttr "cloth_ball_r.bps" "bindPose1.wm[25]";
connectAttr "cloth_fit_ffd.og[1]" "cloth_collar_mesh_skinCluster.ip[0].ig";
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
connectAttr "cloth_ball_l.wm" "cloth_collar_mesh_skinCluster.ma[19]";
connectAttr "cloth_thigh_r.wm" "cloth_collar_mesh_skinCluster.ma[20]";
connectAttr "cloth_calf_r.wm" "cloth_collar_mesh_skinCluster.ma[21]";
connectAttr "cloth_ball_r.wm" "cloth_collar_mesh_skinCluster.ma[22]";
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
connectAttr "cloth_ball_l.liw" "cloth_collar_mesh_skinCluster.lw[19]";
connectAttr "cloth_thigh_r.liw" "cloth_collar_mesh_skinCluster.lw[20]";
connectAttr "cloth_calf_r.liw" "cloth_collar_mesh_skinCluster.lw[21]";
connectAttr "cloth_ball_r.liw" "cloth_collar_mesh_skinCluster.lw[22]";
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
connectAttr "cloth_ball_l.obcc" "cloth_collar_mesh_skinCluster.ifcl[19]";
connectAttr "cloth_thigh_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[20]";
connectAttr "cloth_calf_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[21]";
connectAttr "cloth_ball_r.obcc" "cloth_collar_mesh_skinCluster.ifcl[22]";
connectAttr "bindPose1.msg" "cloth_collar_mesh_skinCluster.bp";
connectAttr "cloth_jacket_meshShapeOrig.w" "cloth_fit_ffd.ip[0].ig";
connectAttr "cloth_collar_meshShapeOrig.w" "cloth_fit_ffd.ip[1].ig";
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
