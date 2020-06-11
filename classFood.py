import magicVariables as mv
import helpSimulate as hsm
import pybullet as p
import random
import numpy as np

class Food:
    def __init__(self, objPos):
        self.yaw = random.uniform(0.0, 2.0 * np.pi)
        self.pos = objPos
        self.objID = hsm.create("food", mv.prefabToURDF["food"], self.pos, self.yaw, mv.FOOD_SIZE)
        hsm.objIDToObject[self.objID] = self
