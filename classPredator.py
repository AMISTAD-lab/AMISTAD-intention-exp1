import pybullet as p
import pybullet_data
import numpy as np
import math as m
import helpSimulate as hsm
import magicVariables as mv
import numpy.random as npr
from classCharacter import *
import algorithms as alg
from classLine import *

class Predator(Character):
    """A class for the predator"""
    
    def __init__(self, objPos):
        super().__init__("predator", mv.prefabToURDF["predator"], objPos, mv.PREDATOR_MAX_STAMINA, mv.PREDATOR_SIZE)
        self.lastTargetedPrey = None
        self.preyTimeStamps = []
        p.setCollisionFilterGroupMask(self.objID, -1, mv.PREDATOR_GROUP, mv.PREDATOR_MASK)


    def updateCharacter(self):
        """Overrides Character's updateCharacter method, called each step of simulation."""
        super().updateCharacter(mv.PREDATOR_TIRED_SPEED, mv.PREDATOR_MAX_SPEED, mv.FOOD_MAX_COUNT)

    def eatFood(self):
        objIDList = super().getContactObjects()
        preyEaten = 0
        if objIDList:
            for objID in objIDList:
                obj = hsm.objIDToObject[objID]
                if obj in hsm.preyList:
                    preyEaten += 1
                    hsm.preyList.remove(obj)
                    hsm.data["foodPerPrey"].append(obj.foodTimeStamps)
                    hsm.destroy(objID)
                    self.hunger += mv.PREDATOR_INCREMENT_HUNGER
                    if self.hunger > mv.PREDATOR_MAX_HUNGER:
                        self.hunger = mv.PREDATOR_MAX_HUNGER
        if preyEaten > 0:
            self.preyTimeStamps.append([hsm.frameCount, preyEaten])

    def getObservations(self):
        observationList = super().getObservations(mv.PREDATOR_SIGHT_DISTANCE, mv.PREDATOR_SIGHT_ANGLE)
        return observationList

    def updateStamina(self):
        """Updates the stamina of the predator each frame according to its current speed."""
        if self.lastTargetedPrey == None:
            return super().updateStamina(mv.PREDATOR_MAX_SPEED * 0.5, mv.STAMINA_FACTOR, mv.PREDATOR_MAX_STAMINA)
        else:
            return super().updateStamina(mv.PREDATOR_TARGET_SPEED * 0.5, mv.STAMINA_FACTOR, mv.PREDATOR_MAX_STAMINA)

    def takeAction(self, observationList):
        # decrement hunger
        self.hunger -= mv.PREDATOR_DECREMENT_HUNGER

        if hsm.frameCount % mv.UPDATE_FRAME_RATE == 0:
            # get preyList:
            preyList = observationList[0] # list of prey, objID AND position.
            # reset previously targeted prey
            self.resetTarget()
            # if there are prey within sight and not out of chase distance, target one of them
            dist = alg.calcDistance(self.pos, mv.TERRAIN_CENTER)
            
            #adding prob of turning back as we approach chase radius
            probTurnBack = (dist/mv.CHASE_RADIUS) ** 15
            turnBack = npr.choice([True, False], size=1, p=[probTurnBack, 1 - probTurnBack])[0]

            if preyList and not turnBack:
                self.targetPrey(preyList)
            # otherwise, pick weighted random speed and direction 
            else:
                self.lastTargetedPrey = None
                yawAndAngleArray = alg.genRandFromContinuousDist(alg.probPredDirection, 0, mv.FULL_CIRCLE, mv.PREDATOR_DECISION_BIN_NUM, self.objID)
                self.speed = alg.genCharSpeed(yawAndAngleArray, self.objID, mv.PREDATOR_MAX_SPEED, mv.PREDATOR_TIRED_SPEED, self.stamina, mv.PREDATOR_TIRED_STAMINA, mv.PREDATOR_DECISION_CURRENT_SPEED_FACTOR) # pass in this array so method knows 
                self.yaw = m.radians(yawAndAngleArray[0])
    
    def resetTarget(self):
        """Each frame, reset Predator's target by making its previously targeted prey no longer targeted
        (can be retargeted in the next line of takeAction)"""
        if self.lastTargetedPrey:
            lastPrey = hsm.objIDToObject[self.lastTargetedPrey]
            lastPrey.isTargeted = False

    def targetPrey(self, preyList):
        """Inputs:
            preyList: list of prey, [objID, pos]"""
        # extract info about prey
        preyIDList = [prey[0] for prey in preyList]

        # decide whether or not to keep the target
        targetPresent = self.lastTargetedPrey in preyIDList # can only keep old target if can still see target
        keepTarget = targetPresent and npr.choice([True, False], size=1, p=[mv.PROB_KEEP_TARGET, 1 - mv.PROB_KEEP_TARGET])[0] # if can see old target, compute weighted prob.
        if keepTarget:
            pickedPreyID = self.lastTargetedPrey
        else:
            pickedPreyID = self.pickNewTarget(preyList)
        
        # target the target, then set speed/direction to lock onto prey
        pickedPrey = hsm.objIDToObject[pickedPreyID]
        pickedPrey.isTargeted = True
        self.lockOntoPrey(pickedPrey.pos)

        # set variable
        self.lastTargetedPrey = pickedPreyID

    def pickNewTarget(self, preyList):
        """Returns a new prey ID for the predator to target. Weighted probabilities are 
        dependent upon distance to each prey."""
        probList = []
        preyIDList = [prey[0] for prey in preyList]
        for prey in preyList:
            # get distance, generate probability of choosing that pre based on distance
            preyPos = prey[1]
            dist = alg.calcDistance(preyPos, self.pos)
            probList.append(1/dist)
        # normalize probabilities and generate weighted random sample
        probList = alg.normalize(probList)
        return npr.choice(preyIDList, size=1, p=probList)[0]

    def lockOntoPrey(self, preyPos):   
        # change the yaw to face the prey     
        yawInDegrees = alg.calcAngleTo(self.pos, preyPos)
        self.yaw = m.radians(yawInDegrees)

        #go at max possible speed after chosen prey
        if self.stamina < mv.PREDATOR_TIRED_STAMINA:
            self.speed = mv.PREDATOR_TARGET_SPEED/3.0
        else:
            self.speed = mv.PREDATOR_TARGET_SPEED
                
        # make a vision line going towards prey
        newLine = Line(self.pos, preyPos)
        hsm.addToLineList(newLine)

