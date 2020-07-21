import pybullet as p
import helpSimulate as hsm
import magicVariables as mv
from scipy.stats import norm
import random as rng
import math as m
import numpy as np

def randSpawnPos(characterRadius):
    """randomly chooses a spawn location within a circle in the terrain bounds. if overlapping with another item, tries again
    input:
        characterRadius: the radius of the character, for overlap checking purposes
    """
    r = mv.SPAWN_RADIUS * m.sqrt(rng.random()) 
    theta = rng.random() * 2 * m.pi
    x1 = mv.TERRAIN_CENTER[0] + r * m.cos(theta)
    y1 = mv.TERRAIN_CENTER[1] + r * m.sin(theta)
    for predator in hsm.predatorList:
        x2, y2 = predator.pos[:2]
        if m.sqrt(m.pow(x2 - x1, 2) + m.pow(y2 - y1, 2)) <= characterRadius + mv.PREDATOR_SIZE/2:
            return randSpawnPos(characterRadius)
    for prey in hsm.preyList:
        x2, y2 = prey.pos[:2]
        if m.sqrt(m.pow(x2 - x1, 2) + m.pow(y2 - y1, 2)) <= characterRadius + mv.PREY_SIZE/2:
            return randSpawnPos(characterRadius)
    for food in hsm.foodList:
        x2, y2 = food.pos[:2]
        if m.sqrt(m.pow(x2 - x1, 2) + m.pow(y2 - y1, 2)) <= characterRadius + mv.FOOD_SIZE/2:
            return randSpawnPos(characterRadius)
    z = characterRadius
    pos = [x1, y1, z]
    return pos


def genRandFromNormalDist(mean, rangeVal):
    """Generates a random number within the range, centered around the mean.
    Inputs:
        mean: double, the number to center the distribution around
        range: double, the width of the range of possible values
    """
    # find standard deviation (want it to be about 1/6 of the range.)
    stdDev = rangeVal / 6.0
    return np.random.normal(mean, stdDev)

def calcDistance(pos1, pos2):
    """Calculates translational (pythagorean) distance between two positions. Uses x, y, z right now (but we only really need x, y)
    Inputs:
        pos1: list [x, y, z] the first position, Euler
        pos2: list [x, y, z], the second position, Euler
    Output:
        double, distance between pos1 and pos2 (will always be positive)
    """
    difference = [pos1[0] - pos2[0], pos1[1] - pos2[1], pos1[2] - pos2[2]] 
    differenceSquared = []
    differenceSquared = np.square(difference)
    dist = m.sqrt(differenceSquared[0] + differenceSquared[1] + differenceSquared[2] + 0.0)
    return dist

def calcAngleTo(pos1, pos2):
    """(Tested!)Calculates angle from from pos1 to pos2. 
    Note: uses only x, y coordinates, NOT z coordinates
    Inputs:
        pos1: list, [x, y, z] the first position
        pos2: list, [x, y, z] the second position
    Output:
        double, angle from pos1 to pos2 in degrees. Range: 0 to 360, inclusive.
        0 is angle defined by the ray going from [0, 0, 0] to [1, 0, 0].
    """
    # if x coords are same, make sure we dont divide by 0!!!!!!
    if pos2[0] - pos1[0] == 0:
        if pos2[1] - pos1[1] > 0:
            return 90.0
        else:
            return 270.0

    # use arctan, convert to degrees.        
    angle = m.degrees(m.atan((pos2[1] - pos1[1])/(pos2[0] - pos1[0])))
    # correct for position so all outputs are positive, and for issues with arctan.
    if pos2[0] < pos1[0]:
        angle += 180.0
    if pos2[0] > pos1[0] and pos2[1] < pos1[1]:
        angle += 360.0

    return angle


def probPreyDirection(direction, charID, predatorList, foodList):
    #initialize probability
    probability = 0.0
    #get prey information
    prey = hsm.objIDToObject[charID]
    hunger = prey.hunger
    currentAngle = m.degrees(prey.yaw)
    # make prey attracted to center if not running from predators
    probability += addDistFromCenterProb(direction, prey.pos, predatorList, mv.PREY_DECISION_CENTER_FACTOR, mv.PREY_DECISION_ACTIVATION_RADIUS)
    probability += addPredProb(direction, charID, prey.pos, predatorList)
    probability += addFoodProb(direction, prey.pos, hunger, foodList)
    probability += addCurrentProb(direction, currentAngle, mv.PREY_DECISION_CURRENT_YAW_FACTOR)
    if mv.IS_CAUTIOUS:
        probability += addHallucinatedPredProb(direction, charID)
    # check if prob is less than or equal to 0
    if probability < 0:
        probability = 0.0
    return probability

def addDistFromCenterProb(direction, pos, predatorList, factor, activationRadius):
    """Calculates change in probabability due distance from center. FOR PREY ONLY
    Inputs: 
        direciton: direction we are finding the probability of
        pos: prey position
        predatorList: if method called for a prey, the list of predators the prey sees.
                     If method called for a predator, [].
    Outputs: 
        probChange: amount to change probability by
    """
    # if it's a prey, don't change prob if there's any predators nearby... we want to run away!
    if predatorList:
        return 0
    # Otherwise, calculate if we are inside the activation radius.
    distToCenter = calcDistance(pos, mv.TERRAIN_CENTER)
    # weight depends on distance to center. Increases according to a power function as we move away from center.
    distanceFactor = (distToCenter/(mv.SPAWN_RADIUS + 0.0))**4
    angleToCenter = calcAngleTo(pos, mv.TERRAIN_CENTER)
    return factor * distanceFactor * angleWeight(angleToCenter, direction) 


def addPredProb(direction, charID, pos, predList):
    """Computes change in probability according to locations of predators
    Inputs: 
        direction: direction whose prob. we are calculating
        charID: objID of the prey
        pos: Position of the prey
        predList: list of predator tuples, each tuple is [obj, pos]"""
    probChange = 0
    for predator in predList:
        # get predator info
        predObj = hsm.objIDToObject[predator[0]]
        predPos = predator[1]
        angleToPred = calcAngleTo(pos, predPos) 
        distToPred = calcDistance(pos, predPos)   
        distanceFactor = mv.PREY_SIGHT_DISTANCE/distToPred
        if predObj.lastTargetedPrey == charID and mv.IS_TARGETED_AWARE and not mv.IS_CAUTIOUS: # account for knowledge if being targeted or not
            targetFactor = mv.PREY_DECISION_TARGETED_BY_PRED_FACTOR
        else:
            targetFactor = mv.PREY_DECISION_PREDATOR_FACTOR
        # change prob accordingly
        probChange += distanceFactor * targetFactor * angleWeight(angleToPred + 180.0, direction)
    return probChange

def addHallucinatedPredProb(direction, charID):
    probChange = 0
    prey = hsm.objIDToObject[charID]
    pred = prey.hallucinatedPred
    if pred:
        angleToPred = calcAngleTo(prey.pos, pred.pos)
        distToPred = calcDistance(prey.pos, pred.pos)   
        distanceFactor = mv.PREY_SIGHT_DISTANCE/distToPred
        targetFactor = mv.PREY_DECISION_TARGETED_BY_PRED_FACTOR
        probChange += distanceFactor * targetFactor * angleWeight(angleToPred + 180.0, direction)
    return probChange



def addFoodProb(direction, pos, hunger, foodList):
    probChange = 0
    # influence of food on direction depends on hunger.
    if hunger <= 0: # don't divide by 0!
        preyHungerFactor = 1.0/mv.PREY_DECREMENT_HUNGER
    else:
        preyHungerFactor = 1.0/hunger 
    for food in foodList:
        foodPos = food[1]
        angleToFood = calcAngleTo(pos, foodPos) 
        distToFood = calcDistance(pos, foodPos) 
        distanceFactor = mv.PREY_SIGHT_DISTANCE/distToFood
        probChange += distanceFactor * preyHungerFactor * mv.PREY_DECISION_FOOD_FACTOR * angleWeight(angleToFood, direction)
    return probChange

def addCurrentProb(direction, currentAngle, factor):
    probChange = factor * angleWeight(currentAngle, direction)
    return probChange

def angleWeight(angle1, angle2, hshift=0.5, vshift=0, power=3.0):
    diff = angleDiff(angle1, angle2)
    if diff < m.sqrt(2):
        prob = 1.0/(m.pow(diff + hshift, power)) + vshift
    else:
        prob = 0
    return prob
    
def angleDiff(angle1, angle2):
    """angle1, angle2: angles in degrees. Return: distance measurement"""
    a = m.radians(angle1)
    b = m.radians(angle2)
    vDiff = m.sin(a) - m.sin(b)
    hDiff = m.cos(a) - m.cos(b)
    diff = m.sqrt(m.pow(vDiff,2) + m.pow(hDiff,2))
    return diff

def genCharSpeed(yawArray, charID, maxSpeed, tiredSpeed, stamina, tiredStamina, currentSpeedWeight): # note: maxSpeed should be adjusted for stamina
    """Generates a random prey speed, weighted depending on the weighted probability of direction that was chosen.
    Must generate random direction FIRST before calling this method
    Inputs: 
        yawArray: list, [yawPicked, selectedBinStart, list of yaw bins, list of probabilities of yaw bins]
        charID: objectID of the character whose direction we are determining
        maxSpeed: float, maximum possible speed for the character
        tiredSpeed: float, max speed for character when character's stamina is less than tiredStamina
        stamina: float, current stamina of character (range: 0.0 --> 1.0)
        tiredStamina: float, stamina below which the character's max speed is tiredSpeed.
        currentSpeedWeight: float, the weight of the currentSpeed of the character. (range: 0.0 --> 1.0)
    """
    charObj = hsm.objIDToObject[charID]
    # 1. normalize the distribution
    yawProbs = yawArray[3]
    normalizedYaws = normalize(yawProbs)
    # 1.5. Make weighted average between normalizedProb and the current speed
    index = yawArray[2].index(yawArray[1])
    normalizedProb = normalizedYaws[index]
    
    speedAccordingToProb = maxSpeed * normalizedProb
    currentSpeed = charObj.speed
    weightedProbSpeed = currentSpeedWeight * currentSpeed + (1 - currentSpeedWeight) * speedAccordingToProb
    # 2. pick from a normal distribution with this angle's probability at the center
    # get the normalized probability
    speed = genRandFromNormalDist(weightedProbSpeed, maxSpeed) # speed goes from 0 to max
    # 3. Cap at max speed, factor in stamina
    speed = abs(speed) # make sure speed will be positive always
    

    if charObj.isTired: #stamina < tiredStamina:
        maxSpeed = tiredSpeed
    if speed > maxSpeed:
        speed = maxSpeed

    return speed

def probPredDirection(direction, predID):# ONLY CALLED when no prey in sight!!!!!
    """Inputs:
        direction: float, the angle which we are calculating the prob of
        predID: int, the objID of the predator"""
    prob = 0.0
    predObject = hsm.objIDToObject[predID]
    currentAngle = m.degrees(predObject.yaw)
    # adjust prob according to distance from center
    prob += addDistFromCenterProb(direction, predObject.pos, [], mv.PREDATOR_DECISION_CENTER_FACTOR, mv.CHASE_RADIUS)
    # adjust prob according to current direction
    prob += addCurrentProb(direction, currentAngle, mv.PREDATOR_DECISION_CURRENT_YAW_FACTOR)
    return prob


def genRandFromContinuousDist(funct, minVal, maxVal, numBins, *args):
    """Generates random number within the desired range. Uses weighted probabilities according to the function.
    Inputs:
        funct: function, the probability function
        minVal: double, the minimum value for the randomly generated number
        maxVal: double, the maximum value for the randomly generated number
        numBins: double, the number of bins we want. Larger = better estimate, longer runtime.
        *args: optional arguments for funct.
    Output:
        return: three element list with random outcome (direction, velocity, etc..), along with a list of outcomes and list of probabiliites
    """
    # 1. Pick a random range (bin), using weighted probabilities
    rangeVal = abs(maxVal - minVal)
    binWidth = rangeVal/(numBins + 0.0)
    # populate an array with weighted probabilites as computed according to function
        # and array of the values assosiated with those probabilities
    probs = []
    nums = []
    firstBin = minVal + binWidth/2.0 # center
    for binNum in range(numBins):
        # loop from 0 to numBins - 1
        nums.append(firstBin + binNum * binWidth)
        probs.append( funct(nums[binNum], *args))
    
    #normalize probs
    if max(probs) == 0.0:
        print("all probs are 0!!! ")
    probs = normalize(probs)
    
    # pick one
    selectedBinMid = np.random.choice(nums, size=1, p=probs)[0]

    # 2. Pick a random value within the selected range.
    randomVal = selectedBinMid - 0.5 * binWidth + rng.random() * binWidth

    return [randomVal, selectedBinMid, nums, probs] 

def normalize(myList):
    """Normalizes a discrete distribution. 
    Inputs:
        myList: list, the discrete distribution to normalize
    Return:
        list, the normalized discrete distribution"""
    myListSum = sum(myList) + 0.0
    if myListSum == 0:
        myList = [1/len(myList)]*len(myList)
    else:
        for i in range(len(myList)):
            myList[i] = myList[i]/myListSum
    
    return myList
    
def quatFromYawDeg(yawInDegrees):
    """Returns a quanternion depending on the updated yaw in degrees"""
    yawInRadians = m.radians(yawInDegrees)
    newRotInEuler = [0.0, 0.0, yawInRadians]
    return p.getQuaternionFromEuler(newRotInEuler)

def quatFromYawRad(yawInRadians):
    """Returns a quanternion depending on the updated yaw in radians"""
    newRotInEuler = [0.0, 0.0, yawInRadians]
    return p.getQuaternionFromEuler(newRotInEuler)