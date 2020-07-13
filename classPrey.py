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
        self.foodTimeStamps = []
        self.isTargeted = False
        self.targetList = [[],[],[],[],[]] #new
        p.setCollisionFilterGroupMask(self.objID, -1, mv.PREY_GROUP, mv.PREY_MASK)


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
        return super().updateStamina(mv.PREY_MAX_SPEED * 0.5, mv.PREY_MAX_STAMINA)

    def getObservations(self):
        """Overrides Character's getObservations"""
        # determine what's in proximity
        observationList = super().getObservations(mv.PREY_SIGHT_DISTANCE, mv.PREY_SIGHT_ANGLE)
        return observationList

    def takeAction(self, observationList):
        """Overrides Character's takeAction"""
        # make prey more hungry each step of simulation
        self.hunger -= mv.PREY_DECREMENT_HUNGER

        # If prey is not able to sense where the predators are, make them blind to predators.
        if (not mv.IS_PROXIMITY_AWARE): 
            observationList[1] = [] 
        if hsm.frameCount % mv.UPDATE_FRAME_RATE == 0:
            # use algorithm to figure out where to move next, according to proximity of food/predators
            yawAndAngleArray = alg.genRandFromContinuousDist(alg.probPreyDirection, 0, mv.FULL_CIRCLE, mv.PREY_DECISION_BIN_NUM, self.objID, observationList[1], observationList[2])
            self.yaw = m.radians(yawAndAngleArray[0])
    
            if self.isTargeted and mv.IS_TARGETED_AWARE:
                if self.isTired:
                    self.speed = mv.PREY_TIRED_SPEED                
                else:
                    self.speed = mv.PREY_MAX_SPEED
            else:
                self.speed = alg.genCharSpeed(yawAndAngleArray, self.objID, mv.PREY_MAX_SPEED, mv.PREY_TIRED_SPEED, self.stamina, mv.PREY_TIRED_STAMINA, mv.PREY_DECISION_CURRENT_SPEED_FACTOR) # pass in this array so method knows

    # def avgTargets(self):
    # '''
    # averages for each of the prey targets' attentions
    # '''
    # for i in self.targetList:
