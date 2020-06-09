#from helpScript import *
import helpScript as hsc
import magicVariables as mv
import pybullet as p
import algorithms as alg
import math as m

def drawLine(lineID, line):
    lineID = "line" + str(lineID)
    length = alg.calcDistance(line.startPos, line.endPos)
    eulerAngle = alg.calcAngleTo(line.startPos, line.endPos)
    q = p.getQuaternionFromEuler([0,0,m.radians(90 - eulerAngle)])
    hsc.write(lineID + " = Instantiate(line," + hsc.vf(line.startPos) + "," + hsc.qf(q) + ");")
    hsc.write(lineID + ".transform.localScale = " + hsc.vf([0,length,0]) + ";")

def destroyLine(lineID):
    lineID = "line" + str(lineID)
    hsc.write("Destroy(" + lineID + ");")

def unitySpawn(objID, prefab, pos, rot, scale=1):
    """creates a GameObject in unity from the prefab at the indicated pos and rot
    input:
        script: list of lists
        objID: int
        prefab: string
        pos: vector (list)
        rot: quaternion (tuple)
        scale: int, defaulted to 1
    """
    if prefab == "wall":
        scaling = [scale, mv.WALL_WIDTH, mv.WALL_HEIGHT]
    else:
        scaling = [scale, scale, scale]
    hsc.write(hsc.makeID(objID) + " = Instantiate(" + prefab + "," + hsc.vf(pos) + "," + hsc.qf(rot) + ");")
    hsc.write(hsc.makeID(objID) + ".transform.localScale = " + hsc.vf(scaling) + ";")
    if objID > hsc.maxID[0]:
        hsc.maxID[0] = objID

def unityDestroy(objID):
    """destroys a gameobject in unity
    input:
        objID: int
    """
    hsc.write("Destroy(" + hsc.makeID(objID) + ");")

def unityUpdateObj(objID, objPos, objRot):
    """updates the position and rotation of an object in unity
    input:
        objID: int
        objPos: vector (list)
        objRot: quaternion (tuple)
    """
    hsc.write(hsc.makeID(objID) + ".transform.position = " + hsc.vf(objPos) + ";")
    hsc.write(hsc.makeID(objID) + ".transform.rotation = " + hsc.qf(objRot) + ";")
