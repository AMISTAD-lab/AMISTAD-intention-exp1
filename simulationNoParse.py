import helpSimulate as hsm
import helpData as hd
import csv

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
