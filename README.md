# Repository of FEM axial impact simulations of the crash box

This repository contains the database developed to be used in machine learning (ML) methods in the GAMM 23 [article](https://onlinelibrary.wiley.com/doi/full/10.1002/pamm.202300145).

The content of this repository can be used as per *License?*.

The crash box is one of the energy-absorbing structures in automobiles. Its deformation mechanism under frontal impact is comprehensively studied. In the above-mentioned article, data from the impact simulations performed in Simulia ABAQUS (version 2021) is needed. For ML framework simulation data is generated and published here. The database **_name_** has differnt configurations of the crash box and their respective crashworthiness metrics values. The configurations have differnt thicknesses and velocities of the impact.

---
### Eigenmode analysis

Every structure contains some form of manufacturing or material impurities and this is often unknown. These impurities affect the structural behaviour. Therefore, to simulate the realistic deformations of the crash box numerical imperfection is manually added. To ensure the imperfection is not arbitrary, linear combinations of eigenmodes are used *(ref)*. Therefore, initially, eigenmodes are investigated and used to define the numerical imperfection in the impact simulations. 

---
### Numerical imperfection + Impact sim
### FEM settings
---
### Data parsing 
---
### Model database
---
### Acknowledgement
---
### references
---
