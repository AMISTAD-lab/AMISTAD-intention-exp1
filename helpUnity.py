import helpScript as hsc
import magicVariables as mv
import pybullet as p
import algorithms as alg
import math as m

def drawLine(lineID, line):
    lineID = "line" + str(lineID)
    length = alg.calcDistance(line.startPos, line.endPos)
    yaw = m.radians(alg.calcAngleTo(line.startPos, line.endPos))
    hsc.write(lineID + " = Instantiate(line," + hsc.posf(line.startPos) + "," + hsc.qf(yaw) + ");")
    hsc.write(lineID + ".transform.localScale = " + hsc.vf([0,length,0]) + ";")

def destroyLine(lineID):
    lineID = "line" + str(lineID)
    hsc.write("Destroy(" + lineID + ");")

def unitySpawn(objID, prefab, pos, yaw, scale=1):
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
        scaling = [mv.WALL_WIDTH, scale, mv.WALL_HEIGHT]
    else:
        scaling = [scale, scale, scale]
    hsc.write(hsc.makeID(objID) + " = Instantiate(" + prefab + "," + hsc.posf(pos) + "," + hsc.qf(yaw) + ");")
    hsc.write(hsc.makeID(objID) + ".transform.localScale = " + hsc.vf(scaling) + ";")
    if objID > hsc.maxID[0]:
        hsc.maxID[0] = objID

def unityDestroy(objID):
    """destroys a gameobject in unity
    input:
        objID: int
    """
    hsc.write("Destroy(" + hsc.makeID(objID) + ");")

def unityUpdateObj(objID, objPos, objYaw):
    """updates the position and rotation of an object in unity
    input:
        objID: int
        objPos: vector (list)
        objRot: quaternion (tuple)
    """
    
    hsc.write(hsc.makeID(objID) + ".transform.position = " + hsc.posf(objPos) + ";")
    hsc.write(hsc.makeID(objID) + ".transform.rotation = " + hsc.qf(objYaw) + ";")
