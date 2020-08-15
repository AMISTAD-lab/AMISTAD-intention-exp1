""" Script that generates a linear run graph from two csv's, each of which have the same varied variable.
Format:
	python linearRunGraph.py "csv file name #1" "csv file name #2" "csv file name for cautious prey" "variable being varied" "x-axis label" "title" (MFI)
Example: 
	python linearRunGraph.py "results/preyPredRatio5.csv" "results/preyPredRatio10.csv" "cppr.csv" "preyPredRatio" "prey-predator ratio (prey/pred)" "Prey-Predator Ratio" 2000

	python linearRunGraph.py "results/predSightDist5.csv" "results/predSightDist10.csv" "predSightDistanceCautious.csv" "predSightDistance" "predator sight distance" "Predator Sight Distance" 2000

Note: for predSightAngle, use predSightAngle2 as the other file so that we don't include extra columns.

"""

import argparse # allow for command line inputs
import datastuff as ds 
import helpData as hd

parser = argparse.ArgumentParser()
parser.add_argument("inputFileName1", type=str, help="Input the first csv file name to read from here. Include the .csv")
parser.add_argument("inputFileName2", type=str, help="Input the second csv file name to read from here. Include the .csv")
parser.add_argument("cautiousFileName", type=str, help="Input the csv file name to use for the cautious mode.")
parser.add_argument("inputToVary", type=str, help="Input the variable to vary as a string.")
parser.add_argument("x_label", type=str, help="Input the x label.")
parser.add_argument("title", type=str, help="Input the title.")
parser.add_argument("MFI", type=int, help="The MFI value")

args = parser.parse_args()
 
inputFileName1 = args.inputFileName1
inputFileName2 = args.inputFileName2
cautiousFileName = args.cautiousFileName
x_label = args.x_label
title = args.title
inputToVary = args.inputToVary
MFI = args.MFI

print("inputFileName1 is", inputFileName1)
print("inputFileName2 is", inputFileName2)
print("cautiousFileName is", cautiousFileName)
print("x_label is", x_label)
print("title is", title)
print("inputToVary is " + str(inputToVary))
print("MFI is", MFI)

newCSVName = inputToVary + "Combined.csv"
hd.combineCSVs(newCSVName, [inputFileName1, inputFileName2])
ds.linearRunGraph(newCSVName, inputToVary, MFI, x_label, title, cautiousFile=cautiousFileName)
#ds.linearRunGraph("results/predsightangle60to120.csv", "predSightAngle", 2000, "predator sight angle (degrees)", "Predator Sight Angle", cautiousFile="predSightAngleCautious.csv")