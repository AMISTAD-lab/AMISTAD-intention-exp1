import pybullet as p
import pybullet_data
import helpScript as hsc
import helpUnity as hu
import magicVariables as mv
from classPrey import *
from classPredator import *
from classTerrain import *
from classFood import *
import copy

frameCount = 0

oldLineList = []

sightLineList = []

preyList = []

predatorList = []

foodList = []

terrainWallIDs = []
objIDToObject = {} #maps object IDs to objects

targetCounts = []

data = {} # data dictionary for a single run


def printProgressBar (iteration, total, prefix = 'Progress:', suffix = 'Complete', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


def createExpInputFile(inputToVary, startValue, endValue, stepValue):
    """Inputs:
        inputToVary: String, the input to vary. 
            eg. "predSightDistance"
        startValue: the starting value of input, inclusive
        endingValue: the ending value of input, inclusive
        stepValue: the stepValue for input
    """
    filename = "experimentInput.txt"
    file = open(filename, "w")
    for targetedAware in [True, False]:
        toWrite = "targetedAware " + str(targetedAware) + "\n"
        for proximityAware in [True, False]:
            saveToWrite = toWrite
            toWrite += "proximityAware " + str(proximityAware) + "\n"
            if not (targetedAware and not proximityAware):
                if (inputToVary == "preySightDistance"):
                    for preySightDistance in range(startValue, endValue+1, stepValue):
                        file.write(toWrite)
                        file.write("preySightDistance " + str(preySightDistance) + "\n\n")
                elif (inputToVary == "predSightDistance"):
                    for predSightDistance in range(startValue, endValue+1, stepValue):
                        file.write(toWrite)
                        file.write("predSightDistance " + str(predSightDistance) + "\n\n")
                elif (inputToVary == "predSightAngle"):
                    for predSightAngle in range(startValue, endValue+1, stepValue):
                        file.write(toWrite)
                        file.write("predSightAngle " + str(predSightAngle) + "\n\n")
                elif (inputToVary == "preyPredRatio"):
                    for preyPredRatio in range(startValue, endValue+1, stepValue):
                        file.write(toWrite)
                        file.write("preyPredRatio " + str(preyPredRatio) + "\n\n")
                elif (inputToVary == "speedFrac"):
                    for speedFrac in range(startValue, endValue+1, stepValue):
                        speedFrac /= 10
                        file.write(toWrite)
                        file.write("speedFrac " + str(speedFrac) + "\n\n")
                else:
                    print("ERROR: Invalid inputToVary.")

            toWrite = saveToWrite
    file.close() 
    return filename   

def createCautiousFile(inputToVary, startValue, endValue, stepValue):
    """Inputs:
        inputToVary: String, the input to vary. 
            eg. "predSightDistance"
        startValue: the starting value of input, inclusive
        endingValue: the ending value of input, inclusive
        stepValue: the stepValue for input
    """
    filename = "cautiousInput.txt"
    file = open(filename, "w")
    for targetedAware in [True]:
        toWrite = "targetedAware " + str(True) + "\n"
        toWrite += "proximityAware " + str(True) + "\n"
        toWrite += "cautious " + str(True) + "\n"
        if (inputToVary == "preySightDistance"):
            for preySightDistance in range(startValue, endValue+1, stepValue):
                file.write(toWrite)
                file.write("preySightDistance " + str(preySightDistance) + "\n\n")
        elif (inputToVary == "predSightDistance"):
            for predSightDistance in range(startValue, endValue+1, stepValue):
                file.write(toWrite)
                file.write("predSightDistance " + str(predSightDistance) + "\n\n")
        elif (inputToVary == "predSightAngle"):
            for predSightAngle in range(startValue, endValue+1, stepValue):
                file.write(toWrite)
                file.write("predSightAngle " + str(predSightAngle) + "\n\n")
        elif (inputToVary == "preyPredRatio"):
            for preyPredRatio in range(startValue, endValue+1, stepValue):
                file.write(toWrite)
                file.write("preyPredRatio " + str(preyPredRatio) + "\n\n")
        elif (inputToVary == "speedFrac"):
            for speedFrac in range(startValue, endValue+1, stepValue):
                speedFrac /= 10
                file.write(toWrite)
                file.write("speedFrac " + str(speedFrac) + "\n\n")
        else:
            print("ERROR: Invalid inputToVary.")
    file.close() 
    return filename                     


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
    if not variableTupleListIn:
        file.write(toWrite + "\n")
    else:
        variableTuple = variableTupleListIn.pop(0) 
        key = variableTuple[0]
        values = variableTuple[1]
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
    lineList = lineList[:-1]

    standardSeed = {
        "targetedAware" : True,
        "proximityAware" : True,
        "cautious" : False,
        "preyPredRatio" : 4,
        "preySightDistance" : 10,
        "predSightDistance" : 20,
        "predSightAngle" : 90,
        "speedFrac": 0.8
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
                if value == "True":
                    preferences[key] = True
                elif value == "False":  
                    preferences[key] = False
                else:
                    preferences[key] = float(value)
            else:
                raise Exception(key + " is not a value in preferences!")
    seedList.append(preferences)
    return seedList

def simulateManySetups(numSimulations, maxSteps, shouldMakeScript, seedList):
    allData = []
    numSeeds = len(seedList)
    for i in range(numSeeds):
        allData.append(batchSimulate(numSimulations, maxSteps, shouldMakeScript, seedList[i], [True, i, numSeeds]))
    return allData

def batchSimulate(numSimulations, maxSteps, shouldMakeScript, preferences, manySetups=[False,0,0]):
    """runs simulate many times"""
    batchData = copy.deepcopy(preferences) # holds runData, as well as averages for each set of parameters
    runsData = [] # holds data dictionaries for runs with a given set of parameters. (greater number of runs = greater precision)
    for i in range(numSimulations):
        runsData.append(simulate(maxSteps, shouldMakeScript, preferences))
        if manySetups[0]:
            printProgressBar((i+1) + (manySetups[1] * numSimulations), numSimulations * manySetups[2])
    batchData["runsData"] = runsData 
    addAverages(batchData) 
    return batchData
    
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
        #won't store pref details either, so best use a seed
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
    data["scriptList"] = "no script generated"

def startSimulation():
    """connect to pybullet and do initial spawns"""
    #reset variables
    global frameCount, preyList, predatorList, foodList, terrainWallIDs, targetCounts, objIDToObject
    frameCount = 0
    preyList = []
    predatorList = []
    foodList = []
    targetCounts = []
    objIDToObject = {}
    hsc.script.clear()
    hsc.script.append([])
    hsc.maxID[0] = 0
    #start simulation
    p.connect(p.DIRECT)
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
    collectTargetInfo()
    nextStep()
    global frameCount
    frameCount += 1

def endSimulation(shouldMakeScript):
    """disconnect from pybullet and make c# script if desired"""
    p.disconnect()
    for prey in preyList:
        data["foodPerPrey"].append(prey.foodTimeStamps)
        targetCounts.append(prey.targetList)
    for predator in predatorList:
        data["preyPerPred"].append(predator.preyTimeStamps)
    data["stepCount"] = frameCount
    data["survivingPrey"] = len(preyList)
    data["targetInfo"] = calcTargetInfo()
    if shouldMakeScript:
        data["scriptList"] = copy.deepcopy(hsc.script)
        hsc.makeScript()

def nextStep():
    """carries out the next step in the simulation and info to unity code
    """
    p.stepSimulation()
    if mv.FRAME_RATIO != 0:
        if frameCount % mv.FRAME_RATIO == 0:
            hsc.script.append([])
            for obj in preyList + predatorList + foodList:
                hu.unityUpdateObj(obj.objID, obj.pos, obj.yaw)
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
    sightLineList.append(line)

def collectTargetInfo():
    for i in range(len(predatorList)):
        predator = predatorList[i]
        if predator.lastTargetedPrey:
            prey = objIDToObject[predator.lastTargetedPrey]
            predTargetInfo = prey.targetList[i]
            lastTargeted = len(predTargetInfo) - 1
            predTargetInfo += [0]*(frameCount - 1 - lastTargeted) + [1]

def calcTargetInfo():
    durationInfo = []
    probTargetInfo = []
    for preyTargetList in targetCounts:
        preyTargetInfo = []
        for predTargetInfo in preyTargetList:
            targetDuration = 0
            infoLength = len(predTargetInfo)
            for i in range(infoLength):
                timestep = predTargetInfo[i]
                if timestep == 1:
                    targetDuration += 1
                    if i == infoLength - 1:
                        preyTargetInfo.append(targetDuration)
                else:
                    if targetDuration > 0:
                        preyTargetInfo.append(targetDuration)
                        targetDuration = 0
        p = len(preyTargetInfo)/frameCount
        probTargetInfo.append(p)
        durationInfo += preyTargetInfo
    return [probTargetInfo, durationInfo]