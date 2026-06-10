# Snap-On Clothing Rig System

## **GenHuman Snap-On Clothing Rig System** 

##  **Development Specification**

### **Project Goal**

* Develop a Maya-based clothing attachment system for the GenHuman rig.  
* System must allow arbitrary clothing rig assets to “snap on” to the main GenHuman rig.  
* Clothing rigs will connect directly to matching GenHuman body joints using Maya `connectAttr` commands.  
* System must support:  
  * swappable clothing assets  
  * multiple simultaneous clothing rigs  
  * lightweight scene performance  
  * compatibility with Genie scene export system  
  * artist-friendly Maya UI workflow

### **Supported Clothing Types**

* System should support a range of clothing assets, including:  
  * shoes  
  * pants  
  * shirts  
  * dresses  
  * coats  
  * hats  
* Clothing complexity may vary:  
  * simple assets such as shoes may only require matching foot joints  
  * complex assets such as long coats may duplicate spine and arm joints  
  * complex clothing may also include additional secondary joints and its own control rig

### **Rig Connection Model**

* Clothing rigs connect to the GenHuman rig using direct `connectAttr` only.  
* No constraints, utility nodes, matrix nodes, expressions, driven keys, or intermediate connection networks should be created.  
* Connections are made only between matching joint attributes.  
* Matching is determined by a strict naming convention.  
* Clothing rig joint names must correspond directly to approved GenHuman joint names.  
* The system should connect compatible transform attributes between the GenHuman source joints and clothing target joints.

### **Naming Convention Requirements**

* GenHuman body joints must follow a defined naming convention.  
* Clothing rig joints must use matching names or approved prefixes/suffixes.  
* The system should identify valid clothing joints by comparing them against the GenHuman joint naming schema.  
* If required joints are missing or incorrectly named, the connection process must stop with an error.  
* Specific node names must be preserved for Genie export compatibility.

### **Multiple Clothing Rig Support**

* The system must allow multiple clothing assets to be connected to a single GenHuman rig.  
* Example supported combinations:  
  * shirt \+ pants \+ shoes  
  * dress \+ shoes \+ hat  
  * long coat \+ pants \+ shoes  
* Multiple clothing rigs may connect to the same GenHuman source joints.  
* Clothing rigs should remain independent from one another.  
* Detaching one clothing item must not affect other connected clothing items.

### **Artist Workflow**

* Tool will be accessed through a Maya UI window.  
* Tool will be launched from a Maya shelf button.  
* Installation should support drag-and-drop setup into Maya.  
* Artists should be able to browse to a clothing asset file from the UI.  
* Artist workflow:  
  * open GenHuman scene  
  * launch clothing tool  
  * browse to clothing asset  
  * import/load clothing asset  
  * validate clothing compatibility  
  * connect clothing rig to GenHuman  
  * optionally detach clothing from GenHuman

### **Validation Requirements**

Before connecting, the tool must validate:

* GenHuman rig exists in scene  
* GenHuman version is compatible  
* clothing rig exists and has valid structure  
* required joint names match convention  
* required attributes exist  
* attribute types are compatible  
* target attributes are not locked  
* target attributes are not already connected in an invalid way  
* duplicate clothing node names are not present  
* namespace conflicts are not present  
* Genie-required node names are present  
* multiple clothing rigs can coexist without name collision

### **Error Handling**

* Validation failures should produce a hard stop.  
* The system should not create partial clothing connections after a failed validation.  
* Error messages should clearly describe:  
  * what failed  
  * which node or attribute caused the issue  
  * what the artist needs to fix  
* Failed operations should leave the scene unchanged whenever possible.

### **Detach / Removal Behavior**

* Detach operation should remove only connections between the clothing rig and the GenHuman rig.  
* Detach should not delete clothing geometry, joints, controls, or rig components.  
* Detach should not modify the GenHuman rig.  
* Detach should not affect other connected clothing assets.

### **Genie Export Compatibility**

* System must be compatible with the Genie scene export system.  
* Genie export targets include:  
  * `.ma`  
  * USD  
  * FBX  
  * Alembic  
* Clothing system must preserve specific required node names for export.  
* Connection graph should remain lightweight and export-friendly.  
* Because only direct `connectAttr` links are allowed, the exported scene should avoid unsupported dependency graph complexity.  
* Clothing rigs should remain discoverable by Genie through their required node names and hierarchy.

### **Version Compatibility**

* Clothing assets must declare or conform to supported GenHuman rig versions.  
* Tool must validate clothing compatibility against the current GenHuman version.  
* Incompatible versions should hard stop before connection.  
* Version compatibility may be handled through:  
  * file naming  
  * required version node  
  * required custom attribute  
  * external version table  
* Final implementation method still needs to be defined.

### **Performance Requirements**

* System must remain lightweight.  
* Direct attribute connections only.  
* Must support multiple clothing rigs without significantly degrading scene playback.  
* No simulation, constraints, expressions, or evaluation-heavy networks should be introduced by the snap-on system.

### **Deliverables**

* Maya Python clothing attachment tool.  
* Maya UI window for browsing, validating, connecting, and detaching clothing rigs.  
* Shelf button launcher.  
* Drag-and-drop installer.  
* Documentation covering:  
  * artist workflow  
  * required naming convention  
  * clothing rig preparation rules  
  * supported GenHuman versions  
  * validation errors  
  * Genie export considerations  
* Example clothing asset for testing.  
* Basic test scene with GenHuman rig and multiple clothing assets.

### **Open Items To Define**

* Exact GenHuman joint naming convention.  
* Required Genie node names.  
* GenHuman version identification method.  
* Clothing version compatibility method.  
* Whether clothing files are imported or referenced.  
* Whether clothing rig controls should remain artist-accessible after connection.  
* Exact transform attributes to connect:  
  * translate  
  * rotate  
  * scale  
  * jointOrient  
  * visibility  
* Whether clothing assets need a required top-level group name.  
* How the system identifies multiple clothing assets without metadata.

See Addendum for specifications of Snap-On compatible Cloth Rigging System

5/15/2026 Tony Hudson

# Addendum — Clothing Rig Specification

# **Addendum — Snap-On Clothing Rig Preparation Specification**

## **Purpose**

This document defines the preparation, rigging, hierarchy, validation, and export requirements for clothing assets intended for use with the GenHuman Snap-On Clothing System.

All clothing assets must conform to these requirements in order to:

* connect successfully to GenHuman rigs  
* validate within the Snap-On Clothing System  
* remain compatible with Genie export workflows  
* support lightweight realtime playback

---

# **Clothing Asset Preparation Requirements**

## **Base Pose Alignment**

* All clothing assets must be authored against the GenHuman bind pose male/female version.  
* Clothing geometry and joints must align spatially with the GenHuman bind pose skeleton.  
* Clothing assets must not be authored in arbitrary poses.

---

# **Scale Requirements**

* Clothing assets must match GenHuman world scale exactly.  
* Scale transforms must be frozen before export.  
* Exported clothing assets should maintain:  
  * scale \= 1  
  * clean transform values  
* Unit scale must match GenHuman pipeline conventions.

---

# **Skeleton Construction Rules**

## **Connection Joints**

* Clothing connection joints must be duplicated directly from the GenHuman skeleton.  
* Connection joints must preserve:  
  * hierarchy structure  
  * orientation  
  * transform alignment  
  * naming relationships

## **Additional Clothing Joints**

* Additional helper/control joints may be created manually.  
* Additional joints must attach to the duplicated GenHuman-derived clothing joints.  
* Additional joints may support:  
  * coat tails  
  * hanging cloth sections  
  * skirts  
  * straps  
  * secondary articulation

---

# **Joint Naming Convention**

* Naming convention is strict.  
* All clothing joints must use approved naming conventions.  
* Clothing joints must include a clothing prefix.

Example:

cloth\_spine\_01\_jnt  
cloth\_l\_arm\_01\_jnt  
cloth\_r\_foot\_jnt

* Naming convention must match GenHuman naming schema.  
* Left/right naming conventions must remain consistent with GenHuman standards.  
* Validation failure should occur for:  
  * incorrect prefixes  
  * duplicate names  
  * invalid suffixes  
  * hierarchy mismatches

---

# **Required Joint Set**

* Clothing rigs should contain only the joints required for the clothing asset.

Examples:

* shoes require only foot joints  
* hats require only head/neck joints  
* coats may require spine, shoulder, arm, and helper joints  
* Full duplicated body skeletons are not required unless needed by the asset.

---

# **Secondary / Helper Joint Rules**

* Secondary joints are permitted.  
* Secondary joints may:  
  * be parented under duplicated clothing joints  
  * contain controls  
  * use custom articulation  
* Secondary joints must follow approved naming conventions.  
* No export restrictions exist on helper joints beyond naming and validation requirements.

---

# **Control Rig Requirements**

## **Controls**

* Controls are optional.  
* Clothing assets may include animator controls where appropriate.  
* Controls should follow naming conventions.

Example:

cloth\_coatTail\_ctrl  
cloth\_skirtFront\_ctrl

## **Control Hierarchy**

* Controls must live in a separate hierarchy from skeleton and geometry hierarchies.  
* Control hierarchy structure should follow GenHuman organizational conventions.

## **Allowed Node Types**

* Any Maya node types are permitted within the control rig.  
* However, realtime playback performance must remain acceptable.

---

# **Geometry Organization**

## **Mesh Support**

* Multiple meshes are supported.  
* Clothing geometry must be grouped under “Mesh\_GRP”

## **Geometry Naming**

* Mesh geometry should use the suffix \*\_mesh”

## **UV Requirements**

* All mesh geometry must contain valid UVs before export.

## **Simulation**

* Simulation geometry and simulation workflows are not part of this system.  
* Clothing assets should not rely on simulation systems.

---

# **Skinning Requirements**

* Smooth bind only.  
* Geometry must be skinned to clothing joints.  
* SkinClusters must validate successfully.  
* Realtime playback performance must remain acceptable.

---

# **Deformer Support**

* Any Maya deformers are permitted.  
* Deformers must remain compatible with:  
  * Maya ASCII export  
  * Snap-On Clothing import  
  * realtime playback requirements

---

# **Blendshape Policy**

* Blendshapes are not supported.  
* Clothing assets should not rely on corrective shapes or morph targets.

---

# **Hierarchy Requirements**

* Clothing hierarchy organization should match GenHuman hierarchy conventions.  
* Clothing assets should maintain clear separation between:  
  * geometry  
  * skeleton  
  * controls

Example:

ClothingAssetName  
    Mesh\_GRP  
    Rig\_GRP  
    Ctrl\_GRP

# **Required Root Nodes**

Each clothing asset must contain:

* a valid root joint  
* a version “info” node

Both must follow GenHuman naming and hierarchy conventions.

---

# **File Format Requirements**

* Clothing assets must be delivered as:  
  * Maya ASCII (`.ma`) files only  
* Scene files must be clean prior to export.

---

# **Scene Cleanliness Requirements**

Clothing asset scenes must not contain:

* unknown nodes  
* references  
* namespaces  
* construction history  
* unused materials  
* animation curves  
* display layers

Validation must fail if unsupported scene content is detected.

---

# **Material / Shader Requirements**

* Clothing assets should use only generic shaders.  
* Specialized render shaders are not supported in authoring assets.

---

# **Validation Requirements**

Validation must check:

* naming compliance  
* hierarchy compliance  
* valid root joint  
* valid version info node  
* transform cleanliness  
* frozen scale transforms  
* valid UVs  
* duplicate names  
* unsupported scene nodes  
* unsupported references/namespaces  
* mesh grouping  
* valid skinClusters  
* realtime playback compatibility  
* joint hierarchy integrity

Validation failures should hard stop export.

---

# **Export Requirements**

* Clothing assets export as:  
  * Maya ASCII only  
* Exported assets are intended for import into the Snap-On Clothing System browser.  
* Export must preserve:  
  * hierarchy  
  * naming  
  * joints  
  * controls  
  * deformers  
  * generic shaders

---

# **Performance Requirements**

* Clothing assets must support realtime playback.  
* Rigs should remain lightweight enough for production scenes containing multiple simultaneous clothing assets.

---

# **Clothing Authoring Workflow**

Recommended workflow:

1. Build clothing geometry  
2. Duplicate required GenHuman joints  
3. Add optional helper joints  
4. Add optional control rig  
5. Skin geometry  
6. Validate clothing asset  
7. Export Maya ASCII asset  
8. Import through Snap-On Clothing System browser

---

# **Future-Proofing**

The system should remain architecturally compatible with future support for:

* body morph propagation

5/15/2026 Tony Hudson