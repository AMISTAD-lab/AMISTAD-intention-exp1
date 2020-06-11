import helpSimulate as hsm
import csv
import helpData as hd

seed = {
        "targetedAware" : True,
        "proximityAware" : True,
        "preyStartCount" : 10,
        "predStartCount" : 5,
        "foodStartCount" : 0,
        "foodMaxCount" : 15,
        "foodSpawnRate" : 75,
        "terrainSize" : 100,
        "preySightDistance" : 10,
        "predSightDistance" : 15,
        "predSightAngle" : 100,
        "preySpeed" : 70,#50, # 70
        "predSpeed" : 60,#7, #5,
        "currentYawFactor" : 20.0,
        "regPredFactor" : 1.5,
        "targetPredFactor" : 4.5,
        "updateFrameRate" : 1.0,
        "preyDecisionCenterFactor" : 1.0,
        "predatorDecisionCenterFactor" : 1.0,#0.5,
        "predatorDecisionCurrentYawFactor" : 10,#3.5,
        "predatorDecisionCurrentSpeedFactor" : 0.5,
        "predatorTargetSpeed": 20
}

hsm.simulate(3000, True, seed)

#note, empty dictionary uses defaults

# NOTES
# WILL NEED TO CHANGe WALL/PRED WEIGHTINGS BACK TO NORMAL
# WILL NEED TO CHANGE PRED AND PREY SPAWN POSITIONS
