"""simulation.py
Now we just need to run this! 

Run:
python simulation.py {csv file name} {parameter to vary} {startValue} {endValue} {stepValue} {num simulations} {maxSteps} {--script} {--append} 

Example:
python simulation.py "outputTest.csv" "preySightDistance" 1 51 5 100 10000
(does not generate script, does not append.)

Note: The program should print out all the values you inputted. Please
check to make sure these are correct! And, wait for a progress bar before
detatching from the screen. 

Note: "ERROR: No file named " + outputFileName" probably means you mistyped the file to 
append to.
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
parser.add_argument("--script", action='store_true', help="Include if should generate Unity Script.")
parser.add_argument("--append", action='store_true', help="Include if appending to outputFileName.")

args = parser.parse_args()

outputFileName = args.outputFileName
inputToVary = args.inputToVary
startValue = args.startValue
endValue = args.endValue
stepValue = args.stepValue
numSimulations = args.numSimulations
maxSteps = args.maxSteps
shouldMakeScript = args.script
shouldAppend = args.append

print("outputFileName is", outputFileName)
print("inputToVary is " + str(inputToVary))
print("startValue is", startValue)
print("endValue is", endValue)
print("stepValue is", stepValue)
print("numSimulations (per seed) is", numSimulations)
print("maxSteps (per simulation) is", maxSteps)
print("shouldMakeScript is " + str(shouldMakeScript))
print("shouldAppend is " + str(shouldAppend))


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
        raise Exception("ERROR: No file named " + outputFileName)

    inputFileName = hsm.createExpInputFile(inputToVary, startValue, endValue, stepValue)
    seedList = hsm.createSeedListFromFile(inputFileName)
    data = hsm.simulateManySetups(numSimulations, maxSteps, shouldMakeScript, seedList)
    if shouldAppend:
        hd.appendDataToCSV(data, outputFileName)
    else:
        hd.allDataToCSV(data, outputFileName)

runExperiment(outputFileName, inputToVary, startValue, endValue, stepValue, numSimulations, maxSteps, shouldMakeScript)