import abc
from abc import ABC, abstractmethod, ABCMeta

import pybullet as p
import pybullet_data
import math
import numpy as np
import random
import helpSimulate as hsm
import magicVariables as mv
from classLine import *
import algorithms as alg

class Character(metaclass = ABCMeta):

    """Creates a new character object using the create() method in helpSimulate."""
    @abstractmethod
    def __init__(self, prefab, filename, objPos, stamina, size=1):
        self.yaw = self.__generateRandYaw() # yaw rotation in radians
        self.pos = objPos
        self.speed = 0.0
        self.stamina = stamina
        self.isTired = False
        self.hunger = 1.0
        self.objID = hsm.create(prefab, filename, objPos, self.yaw, scale=size)
        hsm.objIDToObject[self.objID] = self # populate dictionary with this character

    def __repr__(self):
        return str(self.objID)

    @abstractmethod
    def updateCharacter(self, tiredSpeed, maxSpeed, tiredStamina):
        """Called each step of the simulation. Determines action of the character. 
        1. Check if character is next to food and should eat food :)
        2. Make character die if character is dead :'(
        3. Take in observations of environment
        4. Take appropriate action according to observations.
        inputs:
            tiredSpeed: float, speed of the character when their stamina is low
            maxSpeed: float, maximum speed of the character. See magicVariables.py
            tiredStamina: float, value of stamina of character when character is tired. See magicVariables.py.
        """
        self.updateStamina()
        self.eatFood()
        self.updateRotPosSpeed()
        observationList = self.getObservations()
        self.takeAction(observationList)

    def updateRotPosSpeed(self):
        # update pos, rot
        self.pos = p.getBasePositionAndOrientation(self.objID)[0]
        rot = alg.quatFromYawRad(self.yaw)
        p.resetBasePositionAndOrientation(self.objID, self.pos, rot)
        # update speed 
        yVel = self.speed * np.sin(self.yaw)
        xVel = self.speed * np.cos(self.yaw)
        p.resetBaseVelocity(self.objID, [xVel, yVel, -50.0])
    
    

    @abstractmethod
    def updateStamina(self, thresholdSpeed, maxStamina):
        """Updates the stamina of the character according to its current speed.
        Prey, Predator should override this with their specific threshholds and staminaFactors
        Inputs:
            threshold: the speed value at which the stamina will not change. 
            Stamina decreases when character moves at speeds above threshold, 
            increases otherwise
            staminaFactor: the number by which to multiply the difference between speed and 
            threshold by to get stamina change"""
        change =  (thresholdSpeed - self.speed) / thresholdSpeed
        if change < 0:
            change *= mv.DECREASE_STAMINA_FACTOR
        else:
            change *= mv.INCREASE_STAMINA_FACTOR
        self.stamina = self.stamina + change
        if self.stamina <= 0.2:
            self.isTired = True
            if self.stamina < 0:
                self.stamina = 0
        elif self.stamina >= maxStamina:
            self.isTired = False
            self.stamina = maxStamina

    @abstractmethod
    def eatFood(self):
        """If the character is next to food, then eat the food!"""
        # no implementation, only here to make sure this is implemented in subclasses.

    def getContactObjects(self):
        """use getContactPoints, return a list of anything the Character is in contact with.
        Included for use by eatFood methods of Predator and Prey
        Output:
            a list of object ID's that are in contact with this character."""
        # getContactPoints returns a list of inner lists, each of which contain info about one 
            # object that is in contact with this character.
        contactList = p.getContactPoints(self.objID)
        objIDList = []
        # the objectID of the object in contact is held in third position 
            # of every inner list (if list is not empty)
        if contactList:
            objIDList = [innerList[2] for innerList in contactList]
        return objIDList

    @abstractmethod
    def getObservations(self, dist, fieldOfViewAngle):
        """Take in observations of environment
        input: 
            dist: how far the character can see
            fieldOfViewAngle: the angle the character can see in degrees
        output (in a list):
            preyHit: a list of [objID, objPos] of the prey in view
            predatorsHit: a list of [objID, objPos] of the predators in view
            foodHit: a list of [objID, objPos] of the food in view
        """
        if self in hsm.preyList:
            maxGap = min(mv.PREDATOR_SIZE, mv.FOOD_SIZE)
        elif self in hsm.predatorList:
            maxGap = mv.PREY_SIZE
        else:
            maxGap = min(mv.PREDATOR_SIZE, mv.PREY_SIZE, mv.FOOD_SIZE)
        objHitList = self.look(dist, fieldOfViewAngle, maxGap)
        preyHit = []
        predatorsHit = []
        foodHit = []
        for obj in objHitList:
            hitObject = hsm.objIDToObject[obj[0]]
            if hitObject in hsm.preyList and obj not in preyHit:
                preyHit.append(obj)
            elif hitObject in hsm.predatorList and obj not in predatorsHit:
                predatorsHit.append(obj)
            elif hitObject in hsm.foodList and obj not in foodHit:
                foodHit.append(obj)
        return [preyHit, predatorsHit, foodHit]
            
    
    @abstractmethod
    def takeAction(self, tiredSpeed, maxSpeed, tiredStamina):
        """Take appropriate action according to observations. Simply gives character a velocity
        according to setVelocity(). Should be overridden according to predator and prey.
        inputs:
            tiredSpeed: float, speed of the character when their stamina is low
            maxSpeed: float, maximum speed of the character. See magicVariables.py
            tiredStamina: float, value of stamina of character when character is tired. See magicVariables.py.
        """   

    def look(self, dist, viewAngle, maxGap):
        """looks at the environment
        by performing a ray test batch centered at the position of the character in the direction its facing
        input:
            dist: maximum sight distance 
            viewAngle: the field of view (in degree)
            maxGap: the maximum arclength between two adjacent raycasts
        output:
            hitObjList: a list of nested lists that contain the object IDs that were hit and their positions
        """
        viewAngle = math.radians(viewAngle)
        center = self.pos
        z_rot = self.yaw
        numRayCasts = math.ceil((dist) * (viewAngle) / (maxGap + 0.0)) + 1
        startPosList = [center]*numRayCasts
        endPosList = []
        viewAngle = maxGap * (numRayCasts - 1) / (dist + 0.0) # because numRayCasts is rounded up, original view angle has likely changed
        angle = z_rot - viewAngle / 2
        for i in range(numRayCasts):
            x = center[0] + math.cos(angle) * dist
            y = center[1] + math.sin(angle) * dist
            z = maxGap / 2.0
            endPosList.append([x,y,z])
            angle += viewAngle / (numRayCasts - 1)
        rayList = p.rayTestBatch(startPosList, endPosList, collisionFilterMask=mv.RAY_MASK)

        hitObjList = []
        for rayOutput in rayList:
            if rayOutput[0] != -1 and rayOutput[0] not in hitObjList:
                hitID = rayOutput[0]
                objPos = hsm.objIDToObject[hitID].pos
                hitObjList.append([hitID, objPos])
        return hitObjList


    """----------------------- Helper methods ------------------------"""

    def __generateRandYaw(self):
        """Generates a random yaw about the y-axis in RADIANS""" 
        return random.uniform(0.0, 2.0 * np.pi)


