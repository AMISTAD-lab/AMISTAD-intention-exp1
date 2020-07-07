standardSeed = {
        "targetedAware" : False,
        "proximityAware" : False,
        "preyPredRatio" : 4,
        "preySightDistance" : 10,
        "predSightDistance" : 20,
        "predSightAngle" : 90,
        "speedFrac": 0.8
    }

import helpSimulate as hs
hs.simulate(12000, True, standardSeed)