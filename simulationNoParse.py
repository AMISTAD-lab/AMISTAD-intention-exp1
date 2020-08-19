"""same as simulation.py but runs with ipython instead of parsing
"""


import helpSimulate as hsm
import helpData as hd
import csv
import os.path
from os import path

standardSeedCopy = {
        "targetedAware" : True,
        "proximityAware" : True,
        "preyPredRatio" : 4,
        "preySightDistance" : 10,
        "predSightDistance" : 20,
        "predSightAngle" : 90,
        "speedFrac" : 0.8,
}


def runExperiment(outputFileName, inputToVary, startValue, endValue, stepValue, numSimulations, maxSteps, shouldMakeScript, shouldAppend):
    """Runs a set of experiments, outputs results to a csv file.
    Inputs: 
        outputFileName: String, the csv file name to write to
        inputsToVary: list, of variables of type string to vary. Eeg. ["preySightDistance", "predSightDistance"] runs both 
            "preySightDistance" and "predSightDistance" linearly.
        numSimulatons:  number of simulations to go through for each combination of variables
        maxSteps:  maximum number of steps for each simulation
        shouldMakeScript: Boolean, True if should generate Unity Script, False otherwise. """
    # make sure the file we are trying to append to exists!
    if (shouldAppend and not path.exists(outputFileName)):
        raise Exception("ERROR: No file named " + outputFileName)

    inputFileName = hsm.createExpInputFile(inputToVary, startValue, endValue, stepValue)
    seedList = hsm.createSeedListFromFile(inputFileName)
    data = hsm.simulateManySetups(numSimulations, maxSteps, shouldMakeScript, seedList)
    if shouldAppend:
        hd.appendDataToCSV(data, outputFileName)
    else:
        hd.allDataToCSV(data, outputFileName)


def runCautiousExperiment(outputFileName, inputToVary, startValue, endValue, stepValue, numSimulations, maxSteps, shouldMakeScript, shouldAppend):
    """Runs a set of experiments, outputs results to a csv file.
    Inputs: 
        outputFileName: String, the csv file name to write to
        inputsToVary: list, of variables of type string to vary. Eeg. ["preySightDistance", "predSightDistance"] runs both 
            "preySightDistance" and "predSightDistance" linearly.
        numSimulatons:  number of simulations to go through for each combination of variables
        maxSteps:  maximum number of steps for each simulation
        shouldMakeScript: Boolean, True if should generate Unity Script, False otherwise. """
    # make sure the file we are trying to append to exists!
    if (shouldAppend and not path.exists(outputFileName)):
        raise Exception("ERROR: No file named " + outputFileName)

    inputFileName = hsm.createCautiousFile(inputToVary, startValue, endValue, stepValue)
    seedList = hsm.createSeedListFromFile(inputFileName)
    data = hsm.simulateManySetups(numSimulations, maxSteps, shouldMakeScript, seedList)
    if shouldAppend:
        hd.appendDataToCSV(data, outputFileName)
    else:
        hd.allDataToCSV(data, outputFileName)