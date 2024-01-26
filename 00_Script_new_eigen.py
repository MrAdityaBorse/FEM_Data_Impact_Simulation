###
### Create the Crashbox_shell, rigid wall at the back and rigid impactor model and simulte the eigen mode, to add numerical imperfection 
###

### MODELLING LIBRARIES ###
from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *

# Libraries of data collection and visulization in Python
import numpy as np
#import pandas as pd ###  Error with pandas in the abaqus command line??? Possibly due to different versions ###
import csv
import matplotlib.pyplot as plt
import random
random.seed(1)

### SET UP THE WORKING DIRECTORY ###
import os
print("Current working directory: {0}".format(os.getcwd()))
if os.path.isdir('CB_Impact_thickness_V_variation') == True:
  print("Directory alredy exist.")
else:
    os.mkdir('CB_Impact_thickness_V_variation') #  disired directory name
    print("Created a directory- CB_Impact")

print("Current working directory: {0}".format(os.getcwd()))
os.chdir(r"C:\temp\CB_Impact_thickness_V_variation")
print("Current working directory: {0}".format(os.getcwd()))

### START THE LOOP FOR MODELLING DATABASE myModel ###
Iterations = 100             ### NUMBER OF MODELS ###

# Dictionaries/ list to store the model name and parameters like lenght, width, ... 
models = {"Model":[],"Width":[],"Height":[],"Thickness":[],"Length":[],"Velocity":[],"Eigen_Job":[], "Mass_Im":[]}
eigen_jobs=[] # Add job id in the list jobs

for ii in range(1,Iterations+1):

    # add model id in the dictiobary 'models' 
    models["Model"].append('E_Model-%d' %(ii))
    
    # ### changable variables for modelling the crash box 
    width = 80                                                                                              ### CHANGE
    height = width                                                                                          ### CHANGE
    length = 250                                                                                            ### CHANGE
    thickness = random.choice(np.linspace(1.0, 2.0, num= 11, endpoint=True))                                  ### CHANGING like 1.1, 1.2, 1.3, ...
    velocity = random.choice(np.linspace(5000, 10000, num= 51, endpoint=True))                                ### CHANGING like 5000, 5100, 5200, ...
    Impactor_mass = 0.1                                                                                       ### In tonnes; Can change but keeping contstant for now
    
    # Insert the model name and parameter in the dictionary 'models'
    models["Width"].append('%f' %(width))
    models["Height"].append('%f' %(height))
    models["Thickness"].append('%f' %(thickness))
    models["Length"].append('%f' %(length))
    models["Velocity"].append('%f' %(velocity))
    models["Mass_Im"].append('%f' %(Impactor_mass))
    
    ### MODEL CREATION ###
    myModel = mdb.Model(name=models["Model"][ii-1])
    
    ### PART CREATION ###
    
    ## Crash box CAD design  ##
    # Shell crash box design
    myModel.ConstrainedSketch(name='__profile__', sheetSize=200.0)
    myModel.sketches['__profile__'].rectangle(point1=(-width/2, -height/2), point2=(width/2, height/2))
    myModel.sketches['__profile__'].ObliqueDimension(textPoint=(-10.201717376709, -56.8018226623535), value=width, vertex1=
    myModel.sketches['__profile__'].vertices[3], vertex2=myModel.sketches['__profile__'].vertices[0])
    myModel.sketches['__profile__'].ObliqueDimension(textPoint=(56.059871673584, -25.8473930358887), value=height, vertex1=
    myModel.sketches['__profile__'].vertices[2], vertex2=myModel.sketches['__profile__'].vertices[3])
    myModel.Part(dimensionality=THREE_D, name='Crashbox_Shell', type=DEFORMABLE_BODY)
    myModel.parts['Crashbox_Shell'].BaseShellExtrude(depth=length, sketch=myModel.sketches['__profile__'])
    del myModel.sketches['__profile__']
    myModel.parts['Crashbox_Shell'].ReferencePoint(point=(0.0, 0.0,0.0))
    myModel.parts['Crashbox_Shell'].features.changeKey(fromName='RP', toName='RP_CB_Shell')
    myModel.parts['Crashbox_Shell'].Set(faces= myModel.parts['Crashbox_Shell'].faces.getSequenceFromMask(('[#f ]', ), ), name='CB_Shell_Body', referencePoints=(myModel.parts['Crashbox_Shell'].referencePoints[2], ))
    myModel.parts['Crashbox_Shell'].Set(name='RP_CB_Shell', referencePoints=(    myModel.parts['Crashbox_Shell'].referencePoints[2], ))
    
    # Impactor plate CAD design
    myModel.ConstrainedSketch(name='__profile__', sheetSize=250.0)
    myModel.sketches['__profile__'].rectangle(point1=(-100.0, -100.0), point2=(100.0, 100.0))
    myModel.sketches['__profile__'].ObliqueDimension(textPoint=(-41.8057098388672, -116.068862915039), value=200.0, vertex1=
    myModel.sketches['__profile__'].vertices[3], vertex2=myModel.sketches['__profile__'].vertices[0])
    myModel.sketches['__profile__'].ObliqueDimension(textPoint=(123.72932434082, -65.8705978393555), value=200.0, vertex1=
    myModel.sketches['__profile__'].vertices[2], vertex2=myModel.sketches['__profile__'].vertices[3])
    myModel.Part(dimensionality=THREE_D, name='Impactor_Plate', type=DISCRETE_RIGID_SURFACE)
    myModel.parts['Impactor_Plate'].BaseShell(sketch= myModel.sketches['__profile__'])
    del myModel.sketches['__profile__']
    myModel.parts['Impactor_Plate'].ReferencePoint(point=(0.0, 0.0, 0.0))
    myModel.parts['Impactor_Plate'].features.changeKey(fromName='RP', toName='RP_Im')
    # myModel.parts['Impactor_Plate'].Set(faces=myModel.parts['Impactor_Plate'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Im_Body', referencePoints=(myModel.parts['Impactor_Plate'].referencePoints[2], ))
    myModel.parts['Impactor_Plate'].Set(name='RP_Im', referencePoints=(myModel.parts['Impactor_Plate'].referencePoints[2], ))
    myModel.parts['Impactor_Plate'].engineeringFeatures.PointMassInertia(alpha=0.0, composite=0.0, mass=Impactor_mass, name='Mass_Impactor', region=
    myModel.parts['Impactor_Plate'].sets['RP_Im'])
    
    # Back wall
    myModel.ConstrainedSketch(name='__profile__', sheetSize=250.0)
    myModel.sketches['__profile__'].rectangle(point1=(-100.0, -100.0), point2=(100.0, 100.0))
    myModel.sketches['__profile__'].ObliqueDimension(textPoint=(-63.8809013366699, -111.226493835449), value=200.0, vertex1=
    myModel.sketches['__profile__'].vertices[3], vertex2=myModel.sketches['__profile__'].vertices[0])
    myModel.sketches['__profile__'].ObliqueDimension(textPoint=(110.933296203613, -26.7671852111816), value=200.0, vertex1=
    myModel.sketches['__profile__'].vertices[2], vertex2=myModel.sketches['__profile__'].vertices[3])
    myModel.Part(dimensionality=THREE_D, name='Rigid_Wall', type=DISCRETE_RIGID_SURFACE)
    myModel.parts['Rigid_Wall'].BaseShell(sketch=myModel.sketches['__profile__'])
    del myModel.sketches['__profile__']
    myModel.parts['Rigid_Wall'].ReferencePoint(point=(0.0, 0.0, 0.0))
    myModel.parts['Rigid_Wall'].features.changeKey(fromName='RP', toName='RP_Wall')
    # myModel.parts['Rigid_Wall'].Set(cells=myModel.parts['Rigid_Wall'].cells.getSequenceFromMask(('[#1 ]', ), ), name='Wall_Body', referencePoints=(myModel.parts['Rigid_Wall'].referencePoints[2], ))
    myModel.parts['Rigid_Wall'].Set(name='RP_Wall', referencePoints=(myModel.parts['Rigid_Wall'].referencePoints[2], ))
    
    ### MATERIAL & SECTION CREATION & ASSIGNMENT ###
    myModel.Material(name='Al_alloy')
    myModel.materials['Al_alloy'].Density(table=((2.7e-09, ), ))
    myModel.materials['Al_alloy'].Elastic(table=((69000.0, 0.33), ))
    myModel.materials['Al_alloy'].Plastic(scaleStress=None, table= ((80.0, 0.0), (115.0, 0.024), (139.0, 0.049), (150.0, 0.079), (158.0, 0.099), 
    (167.0, 0.124), (171.0, 0.149), (173.0, 0.174)))
    myModel.HomogeneousShellSection(idealization=NO_IDEALIZATION, integrationRule=SIMPSON, material='Al_alloy', name=
    'CB_Shell_Section', nodalThicknessField='', numIntPts=5, poissonDefinition=DEFAULT, preIntegrate=OFF, temperature=GRADIENT, thickness=thickness, 
    thicknessField='', thicknessModulus=None, thicknessType=UNIFORM,useDensity=OFF)
    myModel.parts['Crashbox_Shell'].SectionAssignment(offset=0.0, offsetField='', offsetType=MIDDLE_SURFACE, region=
    myModel.parts['Crashbox_Shell'].sets['CB_Shell_Body'], sectionName='CB_Shell_Section', thicknessAssignment=FROM_SECTION)
    
    ### SETs & SURFACEs ###
    myModel.parts['Crashbox_Shell'].Surface(name='CB_Shell_Back_Surf', side1Edges= myModel.parts['Crashbox_Shell'].edges.getSequenceFromMask(('[#491 ]', ), ))
    myModel.parts['Crashbox_Shell'].Surface(name='CB_Shell_Front_Surf', side1Edges=myModel.parts['Crashbox_Shell'].edges.getSequenceFromMask(('[#a44 ]', ), ))
    myModel.parts['Crashbox_Shell'].Set(edges=myModel.parts['Crashbox_Shell'].edges.getSequenceFromMask(('[#a44 ]', ), ), name='CB_Shell_Front')
    
    myModel.parts['Impactor_Plate'].Surface(name='Im_back_surf', side2Faces=myModel.parts['Impactor_Plate'].faces.getSequenceFromMask(('[#1 ]', ), ))
    
    myModel.parts['Rigid_Wall'].Surface(name='Wall_front_surf', side1Faces=myModel.parts['Rigid_Wall'].faces.getSequenceFromMask(('[#1 ]', ), )) 
    
    ### MESH DEFINATION ###
    myModel.parts['Crashbox_Shell'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=2.0) ############ CHANGE ############
    myModel.parts['Crashbox_Shell'].setMeshControls(algorithm= MEDIAL_AXIS, regions=myModel.parts['Crashbox_Shell'].faces.getSequenceFromMask(('[#f ]', ), ))
    myModel.parts['Crashbox_Shell'].generateMesh()
    myModel.parts['Crashbox_Shell'].setElementType(elemTypes=( ElemType(elemCode=S4R, elemLibrary=STANDARD, secondOrderAccuracy=OFF, 
        hourglassControl=DEFAULT), ElemType(elemCode=S3, elemLibrary=STANDARD)), regions=(myModel.parts['Crashbox_Shell'].faces.getSequenceFromMask(('[#f ]', ), ), ))
    
    myModel.parts['Impactor_Plate'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=10.0) ############ CHANGE ############
    myModel.parts['Impactor_Plate'].generateMesh()
    
    myModel.parts['Rigid_Wall'].seedPart(deviationFactor=0.1, minSizeFactor=0.1, size=10.0) ############ CHANGE ############
    myModel.parts['Rigid_Wall'].generateMesh()
    
    ### ASSEMBLY ### 10 mm distnace between CB and impactor
    myModel.rootAssembly.DatumCsysByDefault(CARTESIAN)
    
    myModel.rootAssembly.Instance(dependent=ON, name='Crashbox_Shell-1', part=myModel.parts['Crashbox_Shell'])
    myModel.rootAssembly.Instance(dependent=ON, name='Impactor_Plate-1', part=myModel.parts['Impactor_Plate'])
    myModel.rootAssembly.Instance(dependent=ON, name='Rigid_Wall-1', part=myModel.parts['Rigid_Wall'])
    myModel.rootAssembly.translate(instanceList=('Rigid_Wall-1', ), vector=(0.0, 0.0, length))
    
    ### STEP ### Dynamic explicit for 0.05 second
    myModel.BuckleStep(maxIterations=300, name='Loading', numEigen=1, previous='Initial', vectors=2)
    
    ### Tie constraints ###
    myModel.Tie(adjust=OFF, main=myModel.rootAssembly.instances['Rigid_Wall-1'].surfaces['Wall_front_surf']
    , name='tie_back', positionTolerance=5.0, positionToleranceMethod=SPECIFIED
    , secondary=myModel.rootAssembly.instances['Crashbox_Shell-1'].surfaces['CB_Shell_Back_Surf']
    , thickness=ON, tieRotations=ON)
    myModel.Tie(adjust=OFF, main=myModel.rootAssembly.instances['Impactor_Plate-1'].surfaces['Im_back_surf']
    , name='tie_front', positionTolerance=5.0, positionToleranceMethod=
    SPECIFIED, secondary=myModel.rootAssembly.instances['Crashbox_Shell-1'].surfaces['CB_Shell_Front_Surf']
    , thickness=ON, tieRotations=ON)
    
    ### BC & LOAD ###     
    # BC CB Shell
    myModel.EncastreBC(createStepName='Initial', localCsys=None, name='Fixed_CB_Shell_Back', region=myModel.rootAssembly.instances['Rigid_Wall-1'].sets['RP_Wall'])
    myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='Disp_CB_Shell_Front', 
    region=myModel.rootAssembly.instances['Impactor_Plate-1'].sets['RP_Im'], u1=SET, u2=SET, u3=UNSET, ur1=SET, ur2=SET, ur3=SET)
    
    ### LOAD ### Unit load in Z
    myModel.ConcentratedForce(cf3=1.0, createStepName='Loading', distributionType=UNIFORM, field='', localCsys=None, name='Load-1', region=
    myModel.rootAssembly.instances['Impactor_Plate-1'].sets['RP_Im'])
    
    ### JOB & CALCULATE ###
    
    # add job id in the list jobs
    models["Eigen_Job"].append('Eigen_Job-%d' %(ii))
    eigen_jobs.append('Eigen_Job-%d' %(ii))
    
    ### JOB DEFINATION ###
    mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, 
        memoryUnits=PERCENTAGE, model=models["Model"][ii-1], modelPrint=OFF, multiprocessingMode=DEFAULT, name=eigen_jobs[ii-1], nodalOutputPrecision=SINGLE, numCpus=8, numDomains=8, 
        numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
    mdb.jobs[eigen_jobs[ii-1]].submit(consistencyChecking=OFF, datacheckJob=True)
    mdb.jobs[eigen_jobs[ii-1]].waitForCompletion()
    
    myModel.keywordBlock.synchVersions(storeNodesAndElements=False)
    myModel.keywordBlock.replace(84, """
    *Output, field, variable=PRESELECT
    *NODE FIL
    U,""")
        
    ### SAVE MODEL database as CAE file ###
    mdb.saveAs('Rect_Crashbox_eigen.cae')
    
    mdb.jobs[eigen_jobs[ii-1]].submit(consistencyChecking=OFF)
    mdb.jobs[eigen_jobs[ii-1]].waitForCompletion()
    
    ### OUTPUT DATA PARSING ### Create seperate output file with energies and reaction forces for every job

with open('model_database_eigen_sims.csv','wb') as testfile:
        
        # pass the csv file to csv.writer.
        writer = csv.writer(testfile)
        
        # convert the dictionary keys to a list
        key_list = ["Model", "Width", "Height", "Thickness", "Length", "Velocity", "Mass_Im", "Eigen_Job"]
        
        # find the length of the key_list
        limit = Iterations 

        writer.writerow(key_list)
        
        # iterate each column and assign the corresponding values to the column
        for i in range(limit):
            writer.writerow([models[x][i] for x in key_list])
        testfile.close() 