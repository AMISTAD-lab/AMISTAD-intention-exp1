import magicVariables as mv
import algorithms as alg
import math as m

script = [[]]   # list of c# lines
maxID = [0]     # maximum id of the objects, allows us to 
                    # create objects first before running other c# code.

def write(code):
    """writes a line of code to the indicated script
    input:
        script: list of lists
        code: string
    """
    script[-1].append(code + "\n")

def vf(vector):
    """formats a vector for unity c# code
    input:
        vector: list of numbers
    output:
        vStr: string"""
    vStr = "new Vector3(" 
    for i in [0,2,1]:
        vStr += str(vector[i]) + "f,"
    vStr = vStr[:-1] + ")"
    return vStr

def posf(vector):
    """USELESS BUT ALREADY IMPLEMENTED, SAME AS VF"""
    #90 degree rotation around z axis, [x,y] -> [-y, x]
    #vector = [-vector[1], vector[0], vector[2]]
    return vf(vector)

def qf(yaw):
    """formats a yaw into quaternion for unity c# code
    input:
        yaw: an angle in radians around the vertical axis
    output:
        qStr: string"""
    
    #get quat from yaw (reflect over x/y axis)
    quaternion = alg.quatFromYawRad(m.pi/2 - yaw)
    
    qStr = "new Quaternion(" 
    for i in [0,2,1,3]:
        qStr += str(quaternion[i]) + "f,"
    qStr = qStr[:-1] + ")"
    return qStr

def makeID(objID):
    """formats an object ID for use as a gameobject name
    input:
        objID: int
    output:
        string"""
    return "obj" + str(objID)

def makeScript():
    """creates a unity c# script and saves it under UnityMasterScript
    input:
        maxID: one element list containing maximum object ID
    """
    #open c# file
    masterScript = "UnityMasterScript.cs"
    masterScript = open(masterScript, "w")
    #write in standard beginning stuff, including declaring frameCount
    masterScript.writelines(["using UnityEngine;\n","using System.Collections;\n","using System.Collections.Generic;\n","using System;\n","public class UnityMasterScript : MonoBehaviour\n","{\n","private int frameCount = 0;\n"])
    #create public prefab objects
    for prefab in mv.prefabToURDF:
        masterScript.write("public static GameObject " + prefab + ";\n")
    masterScript.write("public static GameObject line;\n")
    #create game object references
    for i in range(maxID[0]+1):
        masterScript.write("static GameObject obj" + str(i) + ";\n")
    for i in range(mv.PREDATOR_START_COUNT): #one line per predator
        masterScript.write("static GameObject line" + str(i) + ";\n")
    masterScript.writelines(["float camSens = 0.25f;\n","private Vector3 lastMouse = new Vector3(255, 255, 255);\n","private double speed = 0.05;\n"])
    #create interface
    masterScript.writelines(["public interface frame\n","{\n","void visualize();\n","}\n"])
    #create methods/classes
    for i in range(len(script)):
        masterScript.writelines(["public class frame" + str(i) + " : frame\n","{\n", "public void visualize()\n","{\n"])
        masterScript.writelines(script[i])
        masterScript.write("}\n}\n")
    #create array of methods (using interface)
    makeMethodArr = "frame[] frames = {"
    for i in range(len(script)):
        makeMethodArr += " new frame" + str(i) + "(),"
    makeMethodArr = makeMethodArr[:-1] + "};\n"
    masterScript.write(makeMethodArr)
    #write start method which initializes prefabs
    masterScript.write("void Start()\n{\n")
    masterScript.write("transform.position = new Vector3(0f,8f,0f);")
    masterScript.write('predator = (GameObject) Resources.Load("Predator");\n')
    masterScript.write('prey = (GameObject) Resources.Load("Prey");\n')
    masterScript.write('food = (GameObject) Resources.Load("Food");\n')
    masterScript.write('plane = (GameObject) Resources.Load("Plane");\n')
    masterScript.write('wall = (GameObject) Resources.Load("Cube");\n')
    masterScript.write('sphere = (GameObject) Resources.Load("Sphere");\n')
    masterScript.write('line = (GameObject) Resources.Load("Line");\n')
    masterScript.write("}\n")
    #write update method and finish file
    masterScript.writelines(["void Update()\n","{\n","lastMouse = Input.mousePosition - lastMouse;\n","lastMouse = new Vector3(-lastMouse.y * camSens, lastMouse.x * camSens, 0 );\n","lastMouse = new Vector3(transform.eulerAngles.x + lastMouse.x , transform.eulerAngles.y + lastMouse.y, 0);\n","transform.eulerAngles = lastMouse;\n","lastMouse =  Input.mousePosition;\n","double angle = transform.eulerAngles.y;\n","angle = (Math.PI/180) * angle;\n"])
    masterScript.write("if (Input.GetKey(KeyCode.R))\n")
    masterScript.write("{\n")
    for i in range(mv.PREDATOR_START_COUNT):
        masterScript.write("Destroy(line" + str(i) +");\n")
    for i in range(maxID[0] + 1):
        masterScript.write("Destroy(obj" + str(i) +");\n")
    masterScript.write("frameCount = 0;\n")
    masterScript.write("}\n")
    masterScript.writelines(["if (Input.GetKey(KeyCode.W))\n","{\n","transform.position += new Vector3(Convert.ToSingle(Math.Sin(angle)*speed),0f, Convert.ToSingle(Math.Cos(angle)*speed));\n","}\n","if (Input.GetKey(KeyCode.S))\n","{\n","transform.position -= new Vector3(Convert.ToSingle(Math.Sin(angle)*speed),0f, Convert.ToSingle(Math.Cos(angle)*speed));\n","}\n","if (Input.GetKey(KeyCode.A))\n","{\n","transform.position -= new Vector3(Convert.ToSingle(Math.Sin(angle + Math.PI/2)*speed),0f, Convert.ToSingle(Math.Cos(angle + Math.PI/2)*speed));\n","}\n","if (Input.GetKey(KeyCode.D))\n","{\n","transform.position += new Vector3(Convert.ToSingle(Math.Sin(angle + Math.PI/2)*speed),0f, Convert.ToSingle(Math.Cos(angle + Math.PI/2)*speed));\n","}\n","if (frameCount < " + str(len(script)) + ")\n","{\n","frames[frameCount].visualize();\n","frameCount++;\n","}\n","}\n","}\n"]) 
    masterScript.close()