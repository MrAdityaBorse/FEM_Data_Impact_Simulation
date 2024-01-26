###
### Create the Crashbox_Solid, crashbox_shell, rigid wall at the back and rigid impactor model and simulte the impact simulation with explicit dynamic solver
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
import time
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
models = {"Model":[],"Width":[],"Height":[],"Thickness":[],"Length":[],"Velocity":[],"Dynamic_Job":[], "Mass_Im":[], "Time_req_s":[]}
dynamic_jobs=[] # Add job id in the list jobs
eigen_jobs = []

for ii in range(1,Iterations+1):

    start_time = time.time()

    # add model id in the dictiobary 'models' 
    models["Model"].append('Dy_Model-%d' %(ii))
    
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
    
    ## Crash box CAD design ##   
      
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
    myModel.rootAssembly.translate(instanceList=('Impactor_Plate-1', ), vector=(0.0, 0.0, -10.0))
    
    ### STEP ### Dynamic explicit for 0.05 second
    myModel.ExplicitDynamicsStep(name='Impact_loading', previous='Initial', timePeriod=0.05, improvedDtMethod=ON)
    
    ### FIELD and HISTORY OUTPUT DATA ###
    myModel.fieldOutputRequests['F-Output-1'].setValues(variables=('S', 'SVAVG', 'PE', 'PEVAVG', 'PEEQ', 'PEEQVAVG', 'LE', 'U', 'V', 'A', 
    'RF', 'CSTRESS', 'CDISP', 'CSLIPR', 'CTANDIR', 'CFORCE', 'CTHICK', 'FSLIPR', 'FSLIP', 'CSTATUS', 'PPRESS'))
    myModel.fieldOutputRequests['F-Output-1'].setValues(numIntervals=20)
    
    ### HO CB Shell ### Do not need coupling anymore, as it increase simualtion time and displacement of CB cannot be calculated as the node number changes in every simulation
    myModel.HistoryOutputRequest(createStepName='Impact_loading', name='Contact_CB_Shell_Front', rebar=EXCLUDE, region=
    myModel.rootAssembly.allInstances['Crashbox_Shell-1'].surfaces['CB_Shell_Front_Surf'], sectionPoints=DEFAULT, variables=('CFNM', 'CFN1', 'CFN2', 'CFN3'))
    myModel.HistoryOutputRequest(createStepName='Impact_loading', name='Energies_CB_Shell', rebar=EXCLUDE, region=
    myModel.rootAssembly.allInstances['Crashbox_Shell-1'].sets['CB_Shell_Body'], sectionPoints=DEFAULT, variables=('ALLAE', 'ALLCD', 'ALLDC', 'ALLDMD', 
    'ALLFD', 'ALLIE', 'ALLKE', 'ALLPD', 'ALLSE', 'ALLVD', 'ALLWK', 'ALLCW', 'ALLMW', 'ALLPW', 'ETOTAL'))
    # myModel.HistoryOutputRequest(createStepName='Impact_loading', name='Disp_CB_Shell', rebar=EXCLUDE, region=
    # myModel.rootAssembly.allInstances['Crashbox_Shell-1'].sets['RP_CB_Shell'], sectionPoints=DEFAULT, variables=('U3', 'V3', 'A3'))
    myModel.HistoryOutputRequest(createStepName='Impact_loading', name='Mass_CB_Shell', rebar=EXCLUDE, region=
    myModel.rootAssembly.allInstances['Crashbox_Shell-1'].sets['CB_Shell_Body'], sectionPoints=DEFAULT, variables=('MASS', ))
    
    myModel.HistoryOutputRequest(createStepName='Impact_loading', name='Impactor_Disp_V_Acc', rebar=EXCLUDE, region=
    myModel.rootAssembly.allInstances['Impactor_Plate-1'].sets['RP_Im'], sectionPoints=DEFAULT, variables=('A3', 'U3', 'V3'))
    
    ### CONTACT ###
    # Frictional contact between parts with coefficient of friction 0.25
    myModel.ContactProperty('Frictional')
    myModel.interactionProperties['Frictional'].TangentialBehavior(formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
    pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((0.25, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
    fraction=0.005, elasticSlipStiffness=None)
    myModel.interactionProperties['Frictional'].NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON, constraintEnforcementMethod=DEFAULT)
    
    # Assign the contact property
    myModel.ContactExp(createStepName='Initial', name='Gen_Self')
    myModel.interactions['Gen_Self'].includedPairs.setValuesInStep(stepName='Initial', useAllstar=ON)
    # myModel.interactions['Gen_Self'].contactPropertyAssignments.appendInStep(assignments=((GLOBAL, SELF, 'Frictionless'), ), stepName='Initial')
    myModel.interactions['Gen_Self'].contactPropertyAssignments.appendInStep(assignments=((GLOBAL, SELF, 'Frictional'), ), stepName='Initial')
    
    ### Tie constraints ###
    myModel.Tie(adjust=OFF, main=myModel.rootAssembly.instances['Rigid_Wall-1'].surfaces['Wall_front_surf']
    , name='tie_back', positionTolerance=5.0, positionToleranceMethod=SPECIFIED
    , secondary=myModel.rootAssembly.instances['Crashbox_Shell-1'].surfaces['CB_Shell_Back_Surf']
    , thickness=ON, tieRotations=ON)
    
    ### BC & LOAD ###     
    # BC CB Shell
    myModel.EncastreBC(createStepName='Initial', localCsys=None, name='Fixed_CB_Shell_Back', region=myModel.rootAssembly.instances['Rigid_Wall-1'].sets['RP_Wall'])
    myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='Disp_CB_Shell_Front', 
    region=myModel.rootAssembly.instances['Impactor_Plate-1'].sets['RP_Im'], u1=SET, u2=SET, u3=UNSET, ur1=SET, ur2=SET, ur3=SET)
    myModel.DisplacementBC(amplitude=UNSET, createStepName='Initial', distributionType=UNIFORM, fieldName='', localCsys=None, name='Fixed_CB_Shell_Front', region=
    myModel.rootAssembly.instances['Crashbox_Shell-1'].sets['CB_Shell_Front'], u1=SET, u2=SET, u3=UNSET, ur1=SET, ur2=SET, ur3=SET)
    
    ### LOAD ### 
    myModel.Velocity(distributionType=MAGNITUDE, field='', name='Impact_Velocity', omega=0.0, region=
    myModel.rootAssembly.instances['Impactor_Plate-1'].sets['RP_Im'], velocity1=0.0, velocity2=0.0, velocity3=velocity)
    
    ### JOB & CALCULATE ###
    
    # add job id in the list jobs
    models["Dynamic_Job"].append('Dynamic_Job-%d' %(ii))
    dynamic_jobs.append('Dynamic_Job-%d' %(ii))
    eigen_jobs.append('Eigen_Job-%d' %(ii))
    
    ### JOB DEFINATION ###
    mdb.Job(atTime=None, contactPrint=OFF, description='', echoPrint=OFF, explicitPrecision=SINGLE, getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, 
        memoryUnits=PERCENTAGE, model=models['Model'][ii-1], modelPrint=OFF, multiprocessingMode=DEFAULT, name=dynamic_jobs[ii-1], nodalOutputPrecision=SINGLE, numCpus=8, numDomains=8, 
        numGPUs=0, numThreadsPerMpiProcess=1, queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine='', waitHours=0, waitMinutes=0)
    mdb.jobs[dynamic_jobs[ii-1]].submit(consistencyChecking=OFF, datacheckJob=True)
    mdb.jobs[dynamic_jobs[ii-1]].waitForCompletion()
    
    imperfection_scale = str(thickness*0.01)
    
    myModel.keywordBlock.synchVersions(storeNodesAndElements=False)
    myModel.keywordBlock.replace(80, 
    '\n** ----------------------------------------------------------------\n** \n*IMPERFECTION,FILE='+eigen_jobs[ii-1]+',STEP=1\n1,'+imperfection_scale+'\n** STEP: Impact_loading\n**')
    
    ### SAVE MODEL database as CAE file ###
    mdb.saveAs('Rect_Crashbox_dy_impact.cae')
    
    mdb.jobs[dynamic_jobs[ii-1]].submit(consistencyChecking=OFF)
    mdb.jobs[dynamic_jobs[ii-1]].waitForCompletion()
    
    end_time = time.time()
    time_req_s = (end_time - start_time)
    models['Time_req_s'].append('%f' %(time_req_s))
    ### OUTPUT DATA PARSING ### Create seperate output file with energies and reaction forces for every job
    
    ### Open ODB and viewport ###
    from abaqus import *
    from abaqusConstants import *
    import visualization
    import odbAccess
    from odbAccess import *
    
    # # Libraries of data collection and visulization in Python
    # import numpy as np
    # # import pandas as pd
    # import csv
    # import matplotlib.pyplot as plt
    
    # Open new viewport
    session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=120, height=80)
    session.viewports['Viewport: 1'].makeCurrent()
    session.viewports['Viewport: 1'].maximize()
    
    # Do I need the following commands
    # executeOnCaeStartup()
    
    # Change directory address in the job call as needed
    Job_id = ('Dynamic_Job-%d' %(ii))
    odb = session.openOdb(name='Dynamic_Job-%d.odb' %(ii))
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    
    #lines set the display render style
    session.viewports['Viewport: 1'].odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF, ))
    session.viewports['Viewport: 1'].view.setValues(session.views['Right'])
    session.viewports['Viewport: 1'].view.setProjection(projection=PARALLEL)
    session.viewports['Viewport: 1'].odbDisplay.commonOptions.setValues(deformationScaling=UNIFORM)
    
    # # Create the screenshot of the results of VM stress
    # session.printToFile(fileName='Job-%d' %(ii), format=PNG, canvasObjects=(session.viewports['Viewport: 1'], ))
    
    # New variables for storage and history outputs
    step = 'Impact_loading'
    region = 'Assembly ASSEMBLY' # Means whole model :)
    
    # Access history data and store them in a sigle array 
    HO = []
    ALLAE = np.array(odb.steps[step].historyRegions[region].historyOutputs['ALLAE'].data)
    ALLIE = np.array(odb.steps[step].historyRegions[region].historyOutputs['ALLIE'].data)
    ALLKE = np.array(odb.steps[step].historyRegions[region].historyOutputs['ALLKE'].data)
    ETOTAL = np.array(odb.steps[step].historyRegions[region].historyOutputs['ETOTAL'].data)
    U3_PI = np.array(odb.steps[step].historyRegions['Node IMPACTOR_PLATE-1.442'].historyOutputs['U3'].data)
    ContactForce = np.array(odb.steps[step].historyRegions['ElementSet  PIBATCH'].historyOutputs['CFNM on surface ASSEMBLY_CRASHBOX_SHELL-1_CB_SHELL_FRONT_SURF'].data)
    
    # # # Mass of crashbox
    CB_mass = np.array(odb.steps[step].historyRegions['ElementSet  PIBATCH'].historyOutputs['MASS  of element set ASSEMBLY_CRASHBOX_SHELL-1_CB_SHELL_BODY'].data)
    
    # HO = np.append((ALLAE,ALLIE,ALLKE,ETOTAL,U3_PI,CFNF), axis=1)
    HO = np.hstack((ALLAE,ALLIE,ALLKE,ETOTAL,U3_PI,ContactForce,CB_mass))
    
    # Save the history data in single file for every job
    np.savetxt(Job_id + '_Energies_RF_U' '.csv', HO, delimiter = ',', fmt = '%f', header = 'Time_steps,Artificial_Energy,Time_steps,Internal_Energy,Time_steps,Kinetic_Energy,Time_steps,Total_En,Time_steps,Disp_Im,Time_steps,Contact_Normal_Force,Time,CB_mass')

with open('model_database_dynamic_impact_sims.csv','wb') as testfile:
        
        # pass the csv file to csv.writer.
        writer = csv.writer(testfile)
        
        # convert the dictionary keys to a list
        key_list = ["Model", "Width", "Height", "Thickness", "Length", "Velocity", "Mass_Im", "Dynamic_Job", "Time_req_s"]
        
        # find the length of the key_list
        limit = Iterations 
        
        # the length of the keys corresponds to no. of. columns.
        writer.writerow(key_list)
        
        # iterate each column and assign the corresponding values to the column
        for i in range(limit):
            writer.writerow([models[x][i] for x in key_list])
        testfile.close() 