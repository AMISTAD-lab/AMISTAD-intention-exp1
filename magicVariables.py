import algorithms as alg
import math

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
PREDATOR_STAMINA_FACTOR = 0.01 # changes should only be 1/100 th of what the difference between speed and threshhold is.

PREY_MAX_STAMINA = 2.0
PREY_STAMINA_FACTOR = 0.01 # changes should only be 1/100 th of what the difference between speed and threshhold is.

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
#PREY_DECISION_PREDATOR_STD = STD_DEV_CIRCLE/5.0
PREY_DECISION_FOOD_FACTOR = 1.0
#PREY_DECISION_FOOD_STD = STD_DEV_CIRCLE/5.0
#PREY_DECISION_BAD_DIST_CURRENT_YAW_FACTOR = 2.0 * PREY_DECISION_CURRENT_YAW_FACTOR # NOT currently being used, double check this
#PREY_DECISION_CURRENT_YAW_STD = STD_DEV_CIRCLE/4.0
PREY_DECISION_CURRENT_SPEED_FACTOR = 0.5 # this one must be in range [0, 1]. Used in genCharSpeed


PREY_DECISION_BIN_NUM = 12# math.ceil(FULL_CIRCLE * 0.5/PREY_DECISION_CURRENT_YAW_STD) # number of bins to use in estimation. larger means more accurate, but longer run time
#PREY_DECISION_CLOSE_WALL_FACTOR = 15 * PREY_DECISION_WALL_FACTOR
#PREY_DECISION_BAD_WALL_DIST = 1
#PREY_WALL_STD_DEV = 90.0


#PREDATOR_DECISION_ACTIVATION_RADIUS =  deprecated because CHASE_RADIUS is used instead.
#PREDATOR_DECISION_PREY_FACTOR = 1.0
#PREDATOR_DECISION_CURRENT_YAW_STD = STD_DEV_CIRCLE / 4.0
PREDATOR_DECISION_BIN_NUM = 12 #<--- COME BACK TO THIS NUMBER! DEFINITELY NEEDS TWEAKING math.ceil(FULL_CIRCLE * 0.5/PREDATOR_DECISION_CURRENT_YAW_STD)

TERRAIN_CENTER = [0, 0, 0] # center point of terrain. Used to attract pred/prey to center

#####################
## D E F A U L T S ##
#####################

UPDATE_FRAME_RATE = 4 # means prey and predator are updated every _____ frame 

IS_PROXIMITY_AWARE = True
    
IS_TARGETED_AWARE = True

TERRAIN_SIZE = 50 #side length of square

# ---note: See reassignments!!!! these values are NOT the ending values for these vars! 
TERRAIN_DIAMETER = TERRAIN_SIZE * 0.6 #percentage of terrainSize subject to change
TERRAIN_RADIUS = TERRAIN_DIAMETER / 2.0 
CHASE_RADIUS = TERRAIN_RADIUS * 0.7 #border of predator chasing prey
#---#

PREY_START_COUNT = 10
    
PREDATOR_START_COUNT = 2
    
FOOD_START_COUNT = 4
    
FOOD_MAX_COUNT = 15
    
FOOD_SPAWN_RATE = 250 #every __ number of frames spawn 1 food

PREDATOR_SIGHT_DISTANCE = 20

PREDATOR_SIGHT_ANGLE = 100 #degrees

PREY_SIGHT_DISTANCE = 20

PREDATOR_MAX_SPEED = 20.0

PREDATOR_TIRED_SPEED = PREDATOR_MAX_SPEED / 3
    
PREDATOR_MEDIAN_SPEED = PREDATOR_MAX_SPEED/2
    
PREDATOR_STAMINA_SPEED_THRESHOLD = 0.5 * PREDATOR_MAX_SPEED


PREY_MAX_SPEED = 50.0

PREY_TIRED_SPEED =  PREY_MAX_SPEED / 3
    
PREY_MEDIAN_SPEED = PREY_MAX_SPEED/2

PREY_STAMINA_SPEED_THRESHOLD = 0.5 * PREY_MAX_SPEED

#PREY_DECISION_CURRENT_SPEED_STD = PREY_MAX_SPEED/12.0 

PREY_DECISION_ACTIVATION_RADIUS = TERRAIN_RADIUS * 0.7

PREY_DECISION_CENTER_FACTOR = 0.1 # should adjust later!!!

PREY_DECISION_CURRENT_YAW_FACTOR = 1.0

PREY_DECISION_PREDATOR_FACTOR = 1.0#1.5

PREY_DECISION_TARGETED_BY_PRED_FACTOR = 1.0#12.0 * PREY_DECISION_PREDATOR_FACTOR

#PREY_DECISION_WALL_FACTOR = 1.0

PREDATOR_DECISION_CURRENT_YAW_FACTOR = 0.5
PREDATOR_DECISION_CENTER_FACTOR = 0.1  # should adjust later!!!
PREDATOR_DECISION_CURRENT_SPEED_FACTOR = 0.5

PREDATOR_TARGET_SPEED = 20

###################
## REASSIGNMENTS ##
###################

def redefineMagicVariables(preferences):
    """preferences is a dictionary with values for the following keys:
    "targetedAware"
    "proximityAware"
    "preyStartCount"
    "predStartCount"
    "foodStartCount"
    "foodMaxCount"
    "foodSpawnRate"
    "terrainSize"
    "preySightDistance"
    "predSightDistance"
    "predSightAngle"
    "preySpeed"
    "predSpeed"
    "currentYawFactor" *
    "regPredFactor" *
    "targetPredFactor" *
    "updateFrameRate" *
    "preyDecisionCenterFactor" *
    "predatorDecisionCenterFactor" *
    "predatorDecisionCurrentYawFactor" *
    "predatorDecisionCurrentSpeedFactor" *
    """

    global IS_TARGETED_AWARE
    IS_TARGETED_AWARE = preferences["targetedAware"]

    global IS_PROXIMITY_AWARE
    IS_PROXIMITY_AWARE = preferences["proximityAware"]

    global PREY_START_COUNT
    PREY_START_COUNT = preferences["preyStartCount"]
    
    global PREDATOR_START_COUNT
    PREDATOR_START_COUNT = preferences["predStartCount"]
    
    global FOOD_START_COUNT
    FOOD_START_COUNT = preferences["foodStartCount"]
    
    global FOOD_MAX_COUNT
    FOOD_MAX_COUNT = preferences["foodMaxCount"]
    
    global FOOD_SPAWN_RATE
    FOOD_SPAWN_RATE = preferences["foodSpawnRate"]

    global TERRAIN_SIZE
    TERRAIN_SIZE = preferences["terrainSize"] 

    global TERRAIN_DIAMETER
    TERRAIN_DIAMETER = TERRAIN_SIZE * 0.6 #percentage of terrainSize subject to change

    global TERRAIN_RADIUS
    TERRAIN_RADIUS = TERRAIN_DIAMETER / 2.0 

    global CHASE_RADIUS
    CHASE_RADIUS = TERRAIN_RADIUS * 0.7 #border of predator chasing prey

    global PREY_SIGHT_DISTANCE
    PREY_SIGHT_DISTANCE = preferences["preySightDistance"]

    global PREDATOR_SIGHT_DISTANCE
    PREDATOR_SIGHT_DISTANCE = preferences["predSightDistance"]

    global PREDATOR_SIGHT_ANGLE
    PREDATOR_SIGHT_ANGLE = preferences["predSightAngle"]

    global PREY_MAX_SPEED
    PREY_MAX_SPEED = preferences["preySpeed"]

    global PREY_TIRED_SPEED
    PREY_TIRED_SPEED = PREY_MAX_SPEED / 3
    
    global PREY_MEDIAN_SPEED
    PREY_MEDIAN_SPEED = PREY_MAX_SPEED/2

    global PREY_STAMINA_SPEED_THRESHOLD
    PREY_STAMINA_SPEED_THRESHOLD = 0.5 * PREY_MAX_SPEED

    #global PREY_DECISION_CURRENT_SPEED_STD
    #PREY_DECISION_CURRENT_SPEED_STD = PREY_MAX_SPEED/12.0 

    global PREDATOR_MAX_SPEED
    PREDATOR_MAX_SPEED = preferences["predSpeed"]

    global PREDATOR_TIRED_SPEED
    PREDATOR_TIRED_SPEED = PREDATOR_MAX_SPEED / 3
    
    global PREDATOR_MEDIAN_SPEED
    PREDATOR_MEDIAN_SPEED = PREDATOR_MAX_SPEED/2
    
    global PREDATOR_STAMINA_SPEED_THRESHOLD
    PREDATOR_STAMINA_SPEED_THRESHOLD = 0.5 * PREDATOR_MAX_SPEED

    global PREY_DECISION_CURRENT_YAW_FACTOR
    PREY_DECISION_CURRENT_YAW_FACTOR = preferences["currentYawFactor"]

    global PREY_DECISION_PREDATOR_FACTOR
    PREY_DECISION_PREDATOR_FACTOR = preferences["regPredFactor"] 

    global PREY_DECISION_TARGETED_BY_PRED_FACTOR 
    PREY_DECISION_TARGETED_BY_PRED_FACTOR = preferences["targetPredFactor"]

    #global PREY_DECISION_WALL_FACTOR
    #PREY_DECISION_WALL_FACTOR = preferences["wallFactor"]

    global UPDATE_FRAME_RATE
    UPDATE_FRAME_RATE = preferences["updateFrameRate"]

    global PREY_DECISION_CENTER_FACTOR
    PREY_DECISION_CENTER_FACTOR = preferences["preyDecisionCenterFactor"]

    global PREDATOR_DECISION_CENTER_FACTOR
    PREDATOR_DECISION_CENTER_FACTOR = preferences["predatorDecisionCenterFactor"]

    global PREDATOR_DECISION_CURRENT_YAW_FACTOR
    PREDATOR_DECISION_CURRENT_YAW_FACTOR = preferences["predatorDecisionCurrentYawFactor"]

    global PREDATOR_DECISION_CURRENT_SPEED_FACTOR
    PREDATOR_DECISION_CURRENT_SPEED_FACTOR = preferences["predatorDecisionCurrentSpeedFactor"]

    global PREDATOR_TARGET_SPEED 
    PREDATOR_TARGET_SPEED = preferences["predatorTargetSpeed"]