import helpSimulate as hsm
import helpData as hd
import csv

standardSeedCopy = {
        "targetedAware" : True,
        "proximityAware" : True,
        "preyPredRatio" : 4,
        "preySightDistance" : 10,
        "predSightDistance" : 20,
        "predSightAngle" : 90,
        "speedFrac" : 0.8,
}

hsm.simulate(10000, False, standardSeedCopy)