"""simulation.py
Now we just need to run this! 

Run:
python simulation.py {csv file name} [{parameter to vary}] {num simulations} {maxSteps} {shouldMakeScript}

Example:
python simulation.py "outputTest.csv" ["preySightDistance"] 1 10 True
"""


import helpSimulate as hsm
import helpData as hd
import csv
import argparse # allow for command line inputs

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
#parser.add_argument('-l','--list', type=str, dest="inputsToVary", nargs='+', help='<Required> Set flag', required=True)
parser.add_argument("inputsToVary", help="Input a list of strings, each of which is a variable to vary")
parser.add_argument("numSimulations", type=int, help="number of simulations to go through for each combination of variables")
parser.add_argument("maxSteps", type=int, help="maximum number of steps for each simulation")
parser.add_argument("shouldMakeScript", type=bool, help="Boolean, True if should generate Unity Script, False otherwise. ")
args = parser.parse_args()

outputFileName = args.outputFileName
inputsToVary = args.inputsToVary
numSimulations = args.numSimulations
maxSteps = args.maxSteps
shouldMakeScript = args.shouldMakeScript

print("inputsToVary is " + str(inputsToVary))


def runExperiment(outputFileName, inputsToVary, numSimulations, maxSteps, shouldMakeScript):
	"""Runs a set of experiments, outputs results to a csv file.
	Inputs: 
		outputFileName: String, the csv file name to write to
		inputsToVary: list, of variables of type string to vary. Eeg. ["preySightDistance", "predSightDistance"] runs both 
            "preySightDistance" and "predSightDistance" linearly.
        numSimulatons:  number of simulations to go through for each combination of variables
        maxSteps:  maximum number of steps for each simulation
        shouldMakeScript: Boolean, True if should generate Unity Script, False otherwise. """
	inputFileName = hsm.createExpInputFile(inputsToVary)
	seedList = hsm.createSeedListFromFile(inputFileName)
	data = hsm.simulateManySetups(numSimulations, maxSteps, shouldMakeScript, seedList)
	hd.allDataToCSV(data, outputFileName)


runExperiment(outputFileName, inputsToVary, numSimulations, maxSteps, shouldMakeScript)
