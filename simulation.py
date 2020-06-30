"""simulation.py
Now we just need to run this! 

Run:
python simulation.py {csv file name} {parameter to vary} {startValue} {endValue} {stepValue} {num simulations} {maxSteps} {shouldMakeScript}

Example:
python simulation.py "outputTest.csv" "preySightDistance" 5 50 5 1 10 True

Note: Planned ranges are:

"preySightDistance": 5 to 50, step 5
"predSightDistance": 5 to 50, step 5
"predSightAngle": 60 to 120, step 10
"preyPredRatio": 5 to 15, step 1
"speedFrac": 5 to 15, step 1
(all ranges are inclusive)
"""


import helpSimulate as hsm
import helpData as hd
import csv
import argparse # allow for command line inputs
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


parser = argparse.ArgumentParser()
parser.add_argument("outputFileName", type=str, help="Input the csv file name to output to here. Include the .csv")
parser.add_argument("inputToVary", type=str, help="Input a list of strings, each of which is a variable to vary")
parser.add_argument("startValue", type=int, help="The starting value for the varied parameter")
parser.add_argument("endValue", type=int, help="The ending value for the varied parameter")
parser.add_argument("stepValue", type=int, help="The step value for the varied parameter")
parser.add_argument("numSimulations", type=int, help="number of simulations to go through for each combination of variables")
parser.add_argument("maxSteps", type=int, help="maximum number of steps for each simulation")
parser.add_argument("shouldMakeScript", type=bool, help="Boolean, True if should generate Unity Script, False otherwise. ")
parser.add_argument("--append", action='store_true', help="Include if appending to outputFileName.")

args = parser.parse_args()

outputFileName = args.outputFileName
inputToVary = args.inputToVary
startValue = args.startValue
endValue = args.endValue
stepValue = args.stepValue
numSimulations = args.numSimulations
maxSteps = args.maxSteps
shouldMakeScript = args.shouldMakeScript
shouldAppend = args.append

print("inputToVary is " + str(inputToVary))


def runExperiment(outputFileName, inputToVary, startValue, endValue, stepValue, numSimulations, maxSteps, shouldMakeScript):
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
        print("ERROR: No file named " + outputFileName)
        return;

    inputFileName = hsm.createExpInputFile(inputToVary, startValue, endValue, stepValue)
    seedList = hsm.createSeedListFromFile(inputFileName)
    data = hsm.simulateManySetups(numSimulations, maxSteps, shouldMakeScript, seedList)
    if shouldAppend:
        hd.appendDataToCSV(data, outputFileName)
    else:
        hd.allDataToCSV(data, outputFileName)


runExperiment(outputFileName, inputToVary, startValue, endValue, stepValue, numSimulations, maxSteps, shouldMakeScript)