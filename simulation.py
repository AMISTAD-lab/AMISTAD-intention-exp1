import helpSimulate as hsm
import csv
import helpData as hd

seed = {
        "targetedAware" : True,
        "proximityAware" : True,
        "preyStartCount" : 10,
        "predStartCount" : 1,
        "foodStartCount" : 0,
        "foodMaxCount" : 10,
        "foodSpawnRate" : 50,
        "terrainSize" : 200,
        "preySightDistance" : 20,
        "predSightDistance" : 25,
        "predSightAngle" : 100,
        "preySpeed" : 70,#50, # 70
        "predSpeed" : 70,#7, #5,
        "currentYawFactor" : 20.0,
        "regPredFactor" : 1.5,
        "targetPredFactor" : 4.5,
        "updateFrameRate" : 1.0,
        "preyDecisionCenterFactor" : 0.5,
        "predatorDecisionCenterFactor" : 1000,#0.5,
        "predatorDecisionCurrentYawFactor" : 10,#3.5,
        "predatorDecisionCurrentSpeedFactor" : 0.5,
        "predatorTargetSpeed": 20
}

hsm.simulate(12000, True, seed)

#note, empty dictionary uses defaults

# NOTES
# WILL NEED TO CHANGe WALL/PRED WEIGHTINGS BACK TO NORMAL
# WILL NEED TO CHANGE PRED AND PREY SPAWN POSITIONS
