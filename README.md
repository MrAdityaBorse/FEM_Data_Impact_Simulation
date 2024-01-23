# Repository of FEM axial impact simulations of the crash box

This repository contains the database developed to be used in machine learning (ML) methods in the GAMM 23 [article](https://onlinelibrary.wiley.com/doi/full/10.1002/pamm.202300145).

The content of this repository can be used according to *License*.

The crash box is one of the energy-absorbing structures in automobiles. Its deformation mechanism under frontal impact is comprehensively studied. In the above-mentioned article, data from the impact simulations performed in Simulia ABAQUS (version 2021) is needed. For ML framework simulation data is generated and published here. The database **_name_** has differnt configurations of the crash box and their respective crashworthiness metrics values. The configurations have different thicknesses and velocities of the impact.

---
### Eigenmode analysis

Every structure contains some form of manufacturing or material impurities and this is often unknown. These impurities affect the structural behaviour. Therefore, numerical imperfection is manually added to simulate the realistic deformations of the crash box. To ensure the imperfection is not arbitrary, linear combinations of eigenmodes are used *(ref)*. Therefore, initially, eigenmodes are investigated and used to define the numerical imperfection in the impact simulations.

**_script for eigenmode analysis?_**

The script '00_Script_new_eigen' generates the model database and 'random seed' controls the randomness of the model variables, namely random variation of thickness and impact velocity in their respective limit.

```
    imperfection_scale = str(thickness*0.01)
    
    myModel.keywordBlock.synchVersions(storeNodesAndElements=False)
    myModel.keywordBlock.replace(80, 
    '\n** ----------------------------------------------------------------\n** \n*IMPERFECTION,FILE='+eigen_jobs[ii-1]+',STEP=1\n1,'+imperfection_scale+'\n** STEP: Impact_loading\n**')

```

The imperfection is defined as nodal displacement in the script to generate an impact simulation model and is 1% of the thickness of the crash box. These eigenmodes are saved in the file 'Eigen_Job-(ii-1)', where ii job ID.

At the end of Simulations 'model_database_eigen_sims' CSV file is generated which contains all the design variables of the crash box and impactor.

---
### Impact simulations

**_script for impact analysis?_**

The script '00_Script_new_impact_sim_w_imperfection' generates the model database similar to eigenmode analysis and following the command inserts the imperfection in the crash box structure. Then axial impact simulations are performed on the imperfect crash box. 

The complete FEM model properties are illustrated in the following table.

### FEM settings

| Property  | Value |
| ------------- | ------------- |
| Material | Density=2.7E-09 Young's Modulus=69000/ Poisson's ratio=0.33/ Plasticity table= 80 MPa - 0 and 173 MPa - 0.174 |
| Mesh | Size=0.2/ Elements=S4R |
| Simulation time  | 0.05 s  |
| Contact | Frictional coefficient=0.25/ normal "Hard" contact |
| Impact initial velocity  | As per configuration (listed in the database) |

At the end of Simulations 'model_database_dynamic_impact_sims' CSV file is generated which contains all the design variables of the crash box and impactor.

---
### Data parsing 

**_Data parsing script_**

---
### Model database

**_Model database excel_**

---
### Acknowledgement
---
### references
---
