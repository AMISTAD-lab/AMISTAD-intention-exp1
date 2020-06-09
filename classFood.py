import magicVariables as mv
import helpSimulate as hsm
import pybullet as p
import random
import numpy as np

class Food:
    def __init__(self, objPos):
        self.objID = hsm.create("food", mv.prefabToURDF["food"], objPos, p.getQuaternionFromEuler([0.0, 0.0, random.uniform(0.0, 2.0 * np.pi)]), mv.FOOD_SIZE)
        hsm.objIDToObject[self.objID] = self
        self.pos = objPos
        self.rot = p.getQuaternionFromEuler([0,0,0]) #shouldn't be used for anything