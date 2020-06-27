import algorithms as alg

#change prefabs in script (if wanted), no longer drag&link
prefabToURDF = {
    "predator" : "sphere2.urdf",
    "prey" : "sphere2.urdf",
    "food" : "sphere2.urdf",
    "plane" : "plane.urdf",
    "wall": "block.urdf",
    "sphere" : "sphere2.urdf"
}

###################
## P R E S E T S ##
###################

FRAME_RATIO = 1
UPDATE_FRAME_RATE = 1 # means prey and predator are updated every _____ frame 

PREY_SPAWN_ALG = alg.randSpawnPos
PREDATOR_SPAWN_ALG = alg.randSpawnPos
FOOD_SPAWN_ALG = alg.randSpawnPos

PREDATOR_SIZE = 2
PREY_SIZE = 1
FOOD_SIZE = 0.5

WALL_HEIGHT = 5
WALL_WIDTH = 1

HALF_CIRCLE = 180.0
FULL_CIRCLE = 360.0

PREY_SIGHT_ANGLE = 360

# tired threshold for stamina for predator and prey. Max stamina is 1 for Predator and 2 for Prey. 
PREDATOR_TIRED_STAMINA = 0.2
PREY_TIRED_STAMINA = 0.2 

PREDATOR_MAX_STAMINA = 1.0

DECREASE_STAMINA_FACTOR = 0.0025
INCREASE_STAMINA_FACTOR = 0.01

PREY_MAX_STAMINA = 1.5

INIT_HUNGER = 1.0 # for predator and prey
PREY_MAX_HUNGER = 1.0 # prey cannot eat more food than this. 
PREDATOR_MAX_HUNGER = 1.0
PREY_INCREMENT_HUNGER = PREY_MAX_HUNGER/2 # amount by which each food increases the hunger measure of the prey (larger means more full)
PREDATOR_INCREMENT_HUNGER = PREDATOR_MAX_HUNGER / 2
PREY_DECREMENT_HUNGER = PREY_MAX_HUNGER/2000 # amount by which to decrement prey's hunger each step of simulation.
PREDATOR_DECREMENT_HUNGER = PREDATOR_MAX_HUNGER/3000

PROB_KEEP_TARGET = 0.95 # the probability of sticking with the current targeted prey instead of choosing again (includes current)

# magic variables applying to prey's direction method
STD_DEV_CIRCLE = FULL_CIRCLE/6.0

# control how much prey favor avoiding predators vs. getting food. Higher values mean greater influence.
PREY_DECISION_FOOD_FACTOR = 1.5
PREY_DECISION_CURRENT_SPEED_FACTOR = 0.5 # this one must be in range [0, 1]. Used in genCharSpeed

PREY_DECISION_BIN_NUM = 12# math.ceil(FULL_CIRCLE * 0.5/PREY_DECISION_CURRENT_YAW_STD) # number of bins to use in estimation. larger means more accurate, but longer run time

PREDATOR_DECISION_BIN_NUM = 12 #<--- COME BACK TO THIS NUMBER! DEFINITELY NEEDS TWEAKING math.ceil(FULL_CIRCLE * 0.5/PREDATOR_DECISION_CURRENT_YAW_STD)

TERRAIN_CENTER = [0, 0, 0] # center point of terrain. Used to attract pred/prey to center

TERRAIN_GROUP = 0x01 # group number is like an identifier
PREDATOR_GROUP = 0x02 
PREY_GROUP = 0x04
FOOD_GROUP = 0x08

PREY_DECISION_CENTER_FACTOR = 5

PREY_DECISION_CURRENT_YAW_FACTOR = 30

PREY_DECISION_PREDATOR_FACTOR = 1.5

PREY_DECISION_TARGETED_BY_PRED_FACTOR = 6

PREDATOR_DECISION_CURRENT_YAW_FACTOR = 30
PREDATOR_DECISION_CENTER_FACTOR = 20  
PREDATOR_DECISION_CURRENT_SPEED_FACTOR = 0.5

# 1's correspond to groups that COLLIDE with this object. 0's correspond to groups that DO NOT COLLIDE
TERRAIN_MASK = PREDATOR_GROUP | PREY_GROUP | FOOD_GROUP # collide with everything except other terrain
PREDATOR_MASK = TERRAIN_GROUP| PREDATOR_GROUP| PREY_GROUP # dont collide with food
PREY_MASK = TERRAIN_GROUP| PREDATOR_GROUP| PREY_GROUP | FOOD_GROUP # collide with everything!
FOOD_MASK = TERRAIN_GROUP| PREY_GROUP | FOOD_GROUP # dont collide with predators

RAY_MASK = TERRAIN_GROUP| PREDATOR_GROUP| PREY_GROUP | FOOD_GROUP  # collide with everything!

#####################
## D E F A U L T S ##
#####################

IS_PROXIMITY_AWARE = True
    
IS_TARGETED_AWARE = True

TERRAIN_SIZE = 250 #side length of square
# ---note: See reassignments!!!! these values are NOT the ending values for these vars! 
TERRAIN_DIAMETER = TERRAIN_SIZE * 0.6 #percentage of terrainSize subject to change
TERRAIN_RADIUS = TERRAIN_DIAMETER / 2.0 
CHASE_RADIUS = TERRAIN_RADIUS * 0.7 #border of predator chasing prey
SPAWN_RADIUS = CHASE_RADIUS * 0.7
#---#

PREY_PRED_RATIO = 4
    
PREDATOR_START_COUNT = 5

PREY_START_COUNT = PREDATOR_START_COUNT * PREY_PRED_RATIO
    
FOOD_START_COUNT = 0
    
FOOD_MAX_COUNT = PREY_START_COUNT
    
FOOD_SPAWN_RATE = 70 #every __ number of frames spawn 1 food

PREDATOR_SIGHT_DISTANCE = 20

PREDATOR_SIGHT_ANGLE = 90 #degrees

PREY_SIGHT_DISTANCE = 10
    
PREY_MAX_SPEED = 75.0

PREY_TIRED_SPEED =  PREY_MAX_SPEED / 3
    
PREY_MEDIAN_SPEED = PREY_MAX_SPEED/2

PREDATOR_MAX_SPEED = PREY_MAX_SPEED * 0.8

PREDATOR_TIRED_SPEED = PREDATOR_MAX_SPEED / 3
    
PREDATOR_MEDIAN_SPEED = PREDATOR_MAX_SPEED/2

PREY_DECISION_ACTIVATION_RADIUS = TERRAIN_RADIUS * 0.7

PREDATOR_TARGET_SPEED = PREDATOR_MAX_SPEED * (2/3.0)

###################
## REASSIGNMENTS ##
###################

def redefineMagicVariables(preferences):
    """preferences is a dictionary with values for the following keys:
    "targetedAware"
    "proximityAware"
    "preyPredRatio"
    "preySightDistance"
    "predSightDistance"
    "predSightAngle"
    "speedFrac" #pred speed is fraction of prey speed
    """

    global IS_TARGETED_AWARE
    IS_TARGETED_AWARE = preferences["targetedAware"]

    global IS_PROXIMITY_AWARE
    IS_PROXIMITY_AWARE = preferences["proximityAware"]

    global PREY_START_COUNT
    PREY_START_COUNT = PREDATOR_START_COUNT * int(preferences["preyPredRatio"])
    
    global FOOD_MAX_COUNT
    FOOD_MAX_COUNT = PREY_START_COUNT 

    global PREY_SIGHT_DISTANCE
    PREY_SIGHT_DISTANCE = preferences["preySightDistance"]

    global PREDATOR_SIGHT_DISTANCE
    PREDATOR_SIGHT_DISTANCE = preferences["predSightDistance"]

    global PREDATOR_SIGHT_ANGLE
    PREDATOR_SIGHT_ANGLE = preferences["predSightAngle"]

    global PREDATOR_MAX_SPEED
    PREDATOR_MAX_SPEED = PREY_MAX_SPEED * preferences["speedFrac"]

    global PREDATOR_TIRED_SPEED
    PREDATOR_TIRED_SPEED = PREDATOR_MAX_SPEED / 3
    
    global PREDATOR_MEDIAN_SPEED
    PREDATOR_MEDIAN_SPEED = PREDATOR_MAX_SPEED/2

    global PREDATOR_TARGET_SPEED 
    PREDATOR_TARGET_SPEED = PREDATOR_MAX_SPEED * 2/3.0