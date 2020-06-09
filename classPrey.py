"""classPrey.py
5/22/20
Subclass of Character. Provides attributes and behaviors for a Prey in the simulation.
Todo: factor speed into amount that stamina decreases
To check/test:
    - check if isTargeted is implemented by Predator, and that 
        it is reset if the prey is no longer targeted by that predator.
    - eat food: right now, hunger increments by half of the maximum hunger measurement, maybe implement 
        more complex algorithm later.
"""

import pybullet as p
import math as m
import helpSimulate as hsm
import magicVariables as mv
from classCharacter import *
import algorithms as alg


class Prey(Character):
    """A class for the prey"""

    def __init__(self, objPos):
        super().__init__("prey", mv.prefabToURDF["prey"], objPos, mv.PREY_MAX_STAMINA, mv.PREY_SIZE)
        self.isEaten = False    # True if predator has eaten this prey, False otherwise
        # initialize isTargetedNum depending on simulation type.
        #if mv.IS_TARGETED_AWARE:
        #    self.isTargetedNum = 0  # 1 if prey knows it is targeted, 0 if prey knows it is not targeted
        ##else:    
        #    self.isTargetedNum = 0.5    # 0.5 if prey does not know. Depends on simulation type.
        self.foodTimeStamps = []
        self.isTargeted = False

    def updateCharacter(self):
        """Overrides Character's updateCharacter method, called each step of simulation."""
        super().updateCharacter(mv.PREY_TIRED_SPEED, mv.PREY_MAX_SPEED, mv.FOOD_MAX_COUNT)

    def eatFood(self):
        """Overrides Character's eatFood method."""
        # if a prey is in contact with a food, then eat the food by removing the food and 
            # incrementing hunger. Use getContactPoints.
        objIDInContactList = super().getContactObjects()
        # if there are objects in contact with this prey, then determine if they are food and if so eat them!
        foodEaten = 0
        if objIDInContactList:
            for objID in objIDInContactList:
                food = hsm.objIDToObject[objID]
                if food in hsm.foodList:
                    hsm.foodList.remove(food)
                    hsm.destroy(objID)
                    foodEaten += 1
                    # incrememnt hunger accordingly
                    self.hunger += mv.PREY_INCREMENT_HUNGER 
                    # throw away excess, prey can only eat so much food at a time.
                    if self.hunger > mv.PREY_MAX_HUNGER:
                        self.hunger = mv.PREY_MAX_HUNGER
        if foodEaten > 0:
            self.foodTimeStamps.append([hsm.frameCount, foodEaten])

    def updateStamina(self):
        """Updates the stamina of the prey each frame according to its current speed."""
        return super().updateStamina(mv.PREY_STAMINA_SPEED_THRESHOLD, mv.PREY_STAMINA_FACTOR)

    #def isTargeted(self, status):
    #    """ Shows whether a prey is being targeted or not. """
    #    if status is True:
    #        self.isTargetedNum = 1

    def getObservations(self):
        """Overrides Character's getObservations"""
        # Take care of isTargeted (probably done in Predator)___?
        # determine what's in proximity
        observationList = super().getObservations(mv.PREY_SIGHT_DISTANCE, mv.PREY_SIGHT_ANGLE)
        return observationList

    def takeAction(self, observationList):
        """Overrides Character's takeAction"""
        # make prey more hungry each step of simulation
        self.hunger -= mv.PREY_DECREMENT_HUNGER
        # if no predators and no food nearby, then just move in a random direction.
        #if not observationList[1] and not observationList[2]:
            #super().takeAction(mv.PREY_TIRED_SPEED, mv.PREY_MAX_SPEED, mv.PREY_TIRED_STAMINA)
        #else:
        # If prey is not able to sense where the predators are, make them blind to predators.
        if (not mv.IS_PROXIMITY_AWARE): 
            observationList[1] = [] 
        
        if hsm.frameCount % mv.UPDATE_FRAME_RATE == 0:
            # use algorithm to figure out where to move next, according to proximity of food/predators
            #currentAngleDeg = p.getEulerFromQuaternion(self.rot)[2] # range of possible values is a full circle centered upon current rotation.
            #minAngle = currentAngleDeg - mv.HALF_CIRCLE
            #maxAngle = currentAngleDeg + mv.HALF_CIRCLE
            yawAndAngleArray = alg.genRandFromContinuousDist(alg.probPreyDirection, 0, mv.FULL_CIRCLE, mv.PREY_DECISION_BIN_NUM, self.objID, observationList[1], observationList[2])
            self.rot = super().getQuanternionFromYawDegree(yawAndAngleArray[0])#p.getQuaternionFromEuler([0.0, 0.0, m.radians(yawAndAngleArray[0])]) # yawAndAngleArray[0] is [yaw, list of yaws, list of probs]
            # make speed equal to the maximum possible (corrected for stamina) if prey is targeted.
            if self.isTargeted:
                if self.stamina < mv.PREY_TIRED_STAMINA:
                    self.speed = mv.PREY_TIRED_SPEED                
                else:
                    self.speed = mv.PREY_MAX_SPEED
            else:
                self.speed = alg.genCharSpeed(yawAndAngleArray, self.objID, mv.PREY_MAX_SPEED, mv.PREY_TIRED_SPEED, self.stamina, mv.PREY_TIRED_STAMINA, mv.PREY_DECISION_CURRENT_SPEED_FACTOR) # pass in this array so method knows 
                                                        # how much better or worse this direction is compared to others.
            # make pybullet base move
            #self.setAngleAndSpeed()


    