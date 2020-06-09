import helpSimulate as hsm
import magicVariables as mv
import helpUnity as hu
import pybullet as p
import helpScript as hsc
import math

class Terrain:
    def __init__(self, size):
        ver = p.getQuaternionFromEuler([0,0,math.radians(90)])
        hor = p.getQuaternionFromEuler([0,0,0])
        self.pos = [0,0,0] #shouldn't really be used anywhere

        #make floor
        self.floor = p.loadURDF(mv.prefabToURDF["plane"], [0,0,0], hor, useFixedBase=1, globalScaling=size/200)
        hu.unitySpawn(self.floor, "plane", [0,0,0], hor, size/10) #set prefab as plane
        hsm.objIDToObject[self.floor] = self
 
        #make walls
        self.walls = []
        self.walls.append(p.loadURDF(mv.prefabToURDF["wall"], [-0.59*size, 0, size/10.0], ver, useFixedBase=1, globalScaling = size*10)) # 0
        self.walls.append(p.loadURDF(mv.prefabToURDF["wall"], [0.59*size, 0, size/10.0], ver, useFixedBase=1, globalScaling = size*10)) #180
        self.walls.append(p.loadURDF(mv.prefabToURDF["wall"], [0, 0.59*size, size/10.0], hor, useFixedBase=1, globalScaling = size*10)) # 90
        self.walls.append(p.loadURDF(mv.prefabToURDF["wall"], [0, -0.59*size, size/10.0], hor, useFixedBase=1, globalScaling = size*10)) #270
        hu.unitySpawn(self.walls[0], "wall", [-(size + mv.WALL_WIDTH)/2.0, 0, mv.WALL_HEIGHT/2.0], ver, size) #set prefab as cube
        hu.unitySpawn(self.walls[1], "wall", [(size + mv.WALL_WIDTH)/2.0, 0, mv.WALL_HEIGHT/2.0], ver, size)
        hu.unitySpawn(self.walls[2], "wall", [0, (size + mv.WALL_WIDTH)/2.0, mv.WALL_HEIGHT/2.0], hor, size)
        hu.unitySpawn(self.walls[3], "wall", [0, -(size + mv.WALL_WIDTH)/2.0, mv.WALL_HEIGHT/2.0], hor, size)
        for wallID in self.walls:
            hsm.objIDToObject[wallID] = self
            hsm.terrainWallIDs.append(wallID)
