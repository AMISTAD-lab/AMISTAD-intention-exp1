import pybullet as p
import pybullet_data
import helpScript as hsc
import helpUnity as hu
import magicVariables as mv
from classPrey import *
from classPredator import *
from classTerrain import *
from classFood import *
import math as m
import copy
#import matplotlib.pyplot as plt 
#import seaborn as sb #maybe need to pip install seaborn
#import pandas as pd
#import csv

#inputFileName = "input.txt"

frameCount = 0

oldLineList = []

sightLineList = []

preyList = []

predatorList = []

foodList = []

terrainWallIDs = []
objIDToObject = {} #maps object IDs to objects

data = {} # data dictionary for a single run

def createSimInput(variableTupleList, fileName="inputFile.txt"):
    """ Called from command line, gives our program the parameters to run the simulation on
    Inputs:
        variableTupleList = [(var, [value range]), (var, [value range])]
        [min, max, step] 
    """
    # create a file to write to with specified name
    file = open(fileName, "w")
    # recurse!
    createSimInputHelper(file, variableTupleList, "")
    file.close()
    return fileName

def createSimInputHelper(file, variableTupleListIn, toWrite):
    """Recursive method, called by createSimInput
    file: the file object corresponding to the file we are writing to
    variableTupleListIn: the current list of variable Tuples to recurse over
        tuples: key, value.
            value: list, one element list if a single value. [min, max, step] if a range. 
            key: string, the key 
    toWrite: the string to write to the file at this stage in the recursion
    """
    # Base Case: if no more variables left, simply print blank line
    if not variableTupleListIn:
        file.write(toWrite + "\n")
        
    # Recursive Case: loop through all values in range for this variable.
    # for each possible value, return value plus recursive call.
    else:
        # remove first variableTuple in list and return it
        variableTuple = variableTupleListIn.pop(0) 
        key = variableTuple[0]
        values = variableTuple[1]
        #if only one element, just write it and move on. Otherwise, loop through and write
            # it should be [min, max, step]
        if len(values) == 1:
            toWrite += (str(key) + " " + str(values[0]) + "\n")
            createSimInputHelper(file, variableTupleListIn, toWrite)
        else: 
            num = values[0] 
            while num <= values[1]:
                copyTupleList = copy.deepcopy(variableTupleListIn)
                createSimInputHelper(file, copyTupleList, toWrite + (str(key) + " " + str(num) + "\n"))
                num += values[2]

def createSeedListFromFile(filename):
    seedFile = open(filename, "r")
    lineList = seedFile.readlines()
    seedFile.close()
    lineList = [x.strip("\n") for x in lineList]
    lineList = lineList[:-1] # crop out extra line in file (hacky ik)

    standardSeed = {
        "targetedAware" : True,
        "proximityAware" : True,
        "preyStartCount" : 1,
        "predStartCount" : 1,
        "foodStartCount" : 0,
        "foodMaxCount" : 0,
        "foodSpawnRate" : 0,
        "terrainSize" : 20,
        "preySightDistance" : 10,
        "predSightDistance" : 10,
        "predSightAngle" : 360,
        "preySpeed" : 70,
        "predSpeed" : 10,
        "currentYawFactor" : 20.0,
        "regPredFactor" : 1.0,
        "targetPredFactor" : 1.75,
        "updateFrameRate" : 1.0,
        "preyDecisionCenterFactor" : 0.1,
        "predatorDecisionCenterFactor" : 0.1,
        "predatorDecisionCurrentYawFactor" : 3.5,
        "predatorDecisionCurrentSpeedFactor" : 0.5
    }

    seedList = []
    preferences = copy.deepcopy(standardSeed)
    for line in lineList:
        if line == "":
            seedList.append(preferences)
            preferences = copy.deepcopy(standardSeed)
        else:
            key, value = line.split()
            if key in preferences:
                if value in ["True","False"]:
                    preferences[key] = bool(value)
                else:
                    preferences[key] = float(value)
            else:
                raise Exception(key + " is not a value in preferences!")
    seedList.append(preferences)
    return seedList

def simulateManySetups(numSimulations, maxSteps, shouldMakeScript, seedList):
    allData = []
    for i in range(len(seedList)):
        print("STARTED SEED", i)
        allData.append(batchSimulate(numSimulations, maxSteps, shouldMakeScript, seedList[i]))
    return allData

def batchSimulate(numSimulations, maxSteps, shouldMakeScript, preferences):
    """runs simulate many times"""
    batchData = copy.deepcopy(preferences) # holds runData, as well as averages for each set of parameters
    runsData = [] # holds data dictionaries for runs with a given set of parameters. (greater number of runs = greater precision)
    for i in range(numSimulations):
        print("STARTED TRIAL", i)
        runsData.append(simulate(maxSteps, shouldMakeScript, preferences))
    batchData["runsData"] = runsData 
    addAverages(batchData) 
    return batchData

    #runsData = [run1Data, run2Data, run3Data]
    #batchData = {runsData, avg, avg} 
    
def addAverages(batchData):
    """computes averages form 'runsData' and adds them to batchData dict"""
    runsData = batchData["runsData"]
    numRuns = len(runsData) + 0.0
    batchData["avgStepCount"] = 0
    batchData["avgSurvivingPrey"] = 0
    for run in runsData:
        batchData["avgStepCount"] += run["stepCount"]/numRuns
        batchData["avgSurvivingPrey"] += run["survivingPrey"]/numRuns

def simulate(maxSteps, shouldMakeScript, preferences):
    """runs the entire simulation
    Input:
        steps: int, number of steps to run the simulation for
        makeScript: bool, whether to generate a c# script
    """
    global data
    initializeData(preferences)
    if preferences != {}:
        mv.redefineMagicVariables(preferences)
        #if it is empty, will use defaults
    startSimulation()
    for step in range(maxSteps):
        updateSimulation()
        if len(preyList) == 0:
            break
    endSimulation(shouldMakeScript)
    return data

def initializeData(preferences):
    global data
    data = copy.deepcopy(preferences)
    data["stepCount"] = 0
    data["preyCountOverTime"] = []
    data["foodPerPrey"] = []
    data["preyPerPred"] = []
    data["survivingPrey"] = 0

def startSimulation():
    """connect to pybullet and do initial spawns"""
    #reset variables
    global frameCount, preyList, predatorList, foodList, terrainWallIDs, objIDToObject
    frameCount = 0
    preyList = []
    predatorList = []
    foodList = []
    objIDToObject = {}
    hsc.script.clear()
    hsc.script.append([])
    hsc.maxID[0] = 0
    #start simulation
    p.connect(p.GUI)
    p.setGravity(0,0,-10)
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    terrain = Terrain(mv.TERRAIN_SIZE)
    spawnPrey(mv.PREY_START_COUNT)
    spawnPredators(mv.PREDATOR_START_COUNT)
    spawnFood(mv.FOOD_START_COUNT)

def updateSimulation():
    """update the items of the game and proceed to next frame"""
    updateFood()
    updatePrey()
    updatePredators()
    nextStep()
    global frameCount
    frameCount += 1

def endSimulation(shouldMakeScript):
    """disconnect from pybullet and make c# script if desired"""
    p.disconnect()
    for prey in preyList:
        data["foodPerPrey"].append(prey.foodTimeStamps)
    for predator in predatorList:
        data["preyPerPred"].append(predator.preyTimeStamps)
    print("SIMULATION COMPLETE (" + str(frameCount) + " steps)")
    data["stepCount"] = frameCount
    data["survivingPrey"] = len(preyList)
    if shouldMakeScript:
        hsc.makeScript()
        print("SCRIPT GENERATED")

def nextStep():
    """carries out the next step in the simulation and info to unity code
    """
    p.stepSimulation()
    if mv.FRAME_RATIO != 0:
        if frameCount % mv.FRAME_RATIO == 0:
            hsc.script.append([])
            for obj in preyList + predatorList + foodList:
                hu.unityUpdateObj(obj.objID, obj.pos, obj.yaw)
            #global sightLineList
            global oldLineList
            for i in range(len(oldLineList)):
                hu.destroyLine(i)
            oldLineList = [line for line in sightLineList]
            for i in range(len(sightLineList)):
                hu.drawLine(i, sightLineList[i])
            sightLineList.clear()

def spawnPrey(count):
    """spawns 'count' number of prey"""
    for i in range(count):
        pos = mv.PREY_SPAWN_ALG(mv.PREY_SIZE/2)
        preyList.append(Prey(pos))

def spawnPredators(count):
    """spawns 'count' number of predators"""
    for i in range(count):
        pos = mv.PREDATOR_SPAWN_ALG(mv.PREDATOR_SIZE/2)
        predatorList.append(Predator(pos))

def spawnFood(count):
    """spawns 'count' number of food"""
    for i in range(count):
        pos = mv.FOOD_SPAWN_ALG(mv.FOOD_SIZE/2)
        foodList.append(Food(pos))

def updatePrey():
    """updates all prey in simulation"""
    data["preyCountOverTime"].append(len(preyList))
    for prey in preyList:
        prey.updateCharacter()

def updatePredators():
    """updates all predators in simulation"""
    for predator in predatorList:
        predator.updateCharacter()

def updateFood():
    """spawns food if it should"""
    if mv.FOOD_SPAWN_RATE != 0 and len(foodList) < mv.FOOD_MAX_COUNT:
        if frameCount % mv.FOOD_SPAWN_RATE == 0:
            spawnFood(1)

def create(prefab, filename, objPos, objYaw, scale=1):
    """creates an object in both pybullet and unity
    input:
        prefab: string
        filename: string
        objPos: vector (list)
        objRot: quaternion (list)
        scale: int, defaulted to 1
    output:
        objID: the ID of the created pybullet object
    """
    objRot = alg.quatFromYawRad(objYaw)
    if prefab == "food":
        objID = p.loadURDF(filename, objPos, objRot, useFixedBase=1, globalScaling=scale)
    else:
        objID = p.loadURDF(filename, objPos, objRot, globalScaling=scale)
    hu.unitySpawn(objID, prefab, objPos, objYaw, scale)
    return objID

def destroy(objID):
    """destroys an object in both pybullet and unity
    input:
        objID: int
    """
    p.removeBody(objID)
    hu.unityDestroy(objID)

def addToLineList(line):
    sightLineList.append(line) #please