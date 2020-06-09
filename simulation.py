import helpSimulate as hsm
import csv
import helpData as hd

seed = {
        "targetedAware" : True,
        "proximityAware" : True,
        "preyStartCount" : 1,
        "predStartCount" : 1,
        "foodStartCount" : 0,
        "foodMaxCount" : 0,
        "foodSpawnRate" : 0,
        "terrainSize" : 50,
        "preySightDistance" : 20,
        "predSightDistance" : 20,
        "predSightAngle" : 360,
        "preySpeed" : 70,#50, # 70
        "predSpeed" : 30,#7, #5,
        "currentYawFactor" : 20.0,
        "regPredFactor" : 1.5,
        "targetPredFactor" : 4.5,
        "updateFrameRate" : 1.0,
        "preyDecisionCenterFactor" : 0.1,
        "predatorDecisionCenterFactor" : 0.1,
        "predatorDecisionCurrentYawFactor" : 3.5,
        "predatorDecisionCurrentSpeedFactor" : 0.5
}

hsm.simulate(3000, False, seed)

#note, empty dictionary uses defaults

# NOTES
# WILL NEED TO CHANGe WALL/PRED WEIGHTINGS BACK TO NORMAL
# WILL NEED TO CHANGE PRED AND PREY SPAWN POSITIONS
