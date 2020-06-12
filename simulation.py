import helpSimulate as hsm
import helpData as hd
import csv

standardSeedCopy = {
        "targetedAware" : True,
        "proximityAware" : True,
        "preyStartCount" : 20,
        "predStartCount" : 5,
        "foodStartCount" : 0,
        "foodMaxCount" : 20,
        "foodSpawnRate" : 75,
        "terrainSize" : 250,
        "preySightDistance" : 10,
        "predSightDistance" : 20,
        "predSightAngle" : 90,
        "preySpeed" : 75,
        "predSpeed" : 60,
        "predatorTargetSpeed": 25,
}

hsm.simulate(12000, True, standardSeedCopy)
