import helpSimulate as hsm
import csv
import helpData as hd

seed = {
        #real parameters
        "targetedAware" : True,
        "proximityAware" : True,
        "preyStartCount" : 20,
        "predStartCount" : 5,
        "foodStartCount" : 0,
        "foodMaxCount" : 20,
        "foodSpawnRate" : 75,
        "terrainSize" : 250, #anything above 200 works well
        "preySightDistance" : 10,
        "predSightDistance" : 20,
        "predSightAngle" : 90,
        "preySpeed" : 75,#50, # 70
        "predSpeed" : 60,#7, #5,
        "predatorTargetSpeed": 25,

        #to be hidden later
        "currentYawFactor" : 30.0,
        "regPredFactor" : 1.5, #food is also 1.5
        "targetPredFactor" : 6,
        "updateFrameRate" : 1.0,
        "preyDecisionCenterFactor" : 5.0,
        "predatorDecisionCenterFactor" : 20.0,#0.5,
        "predatorDecisionCurrentYawFactor" : 30,#3.5,
        "predatorDecisionCurrentSpeedFactor" : 0.5,
}

hsm.simulate(12000, True, seed)

#note, empty dictionary uses defaults


