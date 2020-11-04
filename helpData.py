import matplotlib.pyplot as plt 
import seaborn as sb 
import csv
import pandas as pd
import numpy as np
import statistics as stats
import math as m
import copy
import ast
from KDEpy import FFTKDE

def filterDataFrame(data, filterlist):
    data = copy.deepcopy(data)
    for param, value in filterlist:
        booleans = data[param] == value
        data = data[booleans]
    return data

def combineCSVs(fileNameToCreate, csvFileNameList):
    """Combines the specified csv files into one big csv file.
    Note: only works for csvs with exactly 15 columns.
    Inputs:
        fileNameToCreate: the file name for the combined csvs
        csvFolderName: the name of the folder that contains all the csvs to be 
        appended."""
    dfList = []
    for fileName in csvFileNameList:
        df = pd.read_csv(fileName, header=0, index_col=None, usecols=range(0, 15)) # uses columns from 0 to 15 only.
        dfList.append(df)
    resultDf = pd.concat(dfList) # concatenate dataframe versions of csv
    resultDf.to_csv(fileNameToCreate, index=False)
    return resultDf, dfList

def allDataToCSV(allData, filename):
    """takes in a data list obtained from simulateManySetups and writes all of the run information into a csv"""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ["BATCH #"] + ["RUN #"] + [key for key in allData[0]["runsData"][0]]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for batchIndex in range(len(allData)):
            batchData = allData[batchIndex]
            runsData = batchData["runsData"]
            for runIndex in range(len(runsData)):
                runDict = runsData[runIndex]
                runDict["BATCH #"] = batchIndex
                runDict["RUN #"] = runIndex
                writer.writerow(runDict)

def appendDataToCSV(allData, filename):
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = ["BATCH #"] + ["RUN #"] + [key for key in allData[0]["runsData"][0]]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for batchIndex in range(len(allData)):
            batchData = allData[batchIndex]
            runsData = batchData["runsData"]
            for runIndex in range(len(runsData)):
                runDict = runsData[runIndex]
                runDict["BATCH #"] = batchIndex
                runDict["RUN #"] = runIndex
                writer.writerow(runDict)

def histFromCSV(filename, param):
    """Inputs:
        filename: name of csv to read from
        param: String, name of column in csv file"""
    df = pd.read_csv(filename)
    countSeries = df[param]
    countList = [int(count) for count in countSeries]
    plt.hist(countList, histtype='bar', orientation= 'vertical')
    plt.xlabel(param)
    plt.ylabel("Number of trials")
    plt.title(param + " distribution")
    plt.show()

def lifeTimeStatsFromCSV(filename, groupParam):
    """Makes a point plot overlayed on a strip plot with statistics regarding the average life time of prey, grouped by the specified parameter"""
    df = pd.read_csv(filename)
    prey_df = df.groupby(groupParam)["preyCountOverTime"]
    allGroups = []
    allLifeTimes = []
    extraData = []
    for param, group in prey_df:
        groupLifeTimes = []
        for countStr in group:
            countList = strToNumList(countStr)
            groupLifeTimes += lifeTimes(countList)
        avg, std, ci = listStats(groupLifeTimes)
        allGroups += [str(param) + "\nCI: "+ str((int(ci[0]), int(ci[1])))]*len(groupLifeTimes)
        allLifeTimes += groupLifeTimes
        extraData.append([str(groupParam) + " " + str(param), avg, std, ci, groupLifeTimes])
    data = {groupParam: allGroups, "lifespan (time steps)": allLifeTimes}
    data_df = pd.DataFrame(data, columns=[groupParam, "lifespan (time steps)"])
    numGroups = len(df[groupParam].unique())
    colorList = [color for color in plt.cm.jet(np.linspace(0, 0.9, numGroups))]
    ax = sb.pointplot(x=groupParam, y="lifespan (time steps)", data=data_df, estimator=np.mean, ci=95, palette=colorList, errwidth=2, capsize=0.05)
    sb.catplot(x=groupParam, y="lifespan (time steps)", data=data_df, ax=ax, palette=colorList)
    plt.close()
    plt.show()
    return extraData

def lifeTimes(countList):
    """takes in a prey count over time list and returns lifetimes of prey"""
    currentNumPrey = countList[0]
    preyLifeTimes = []
    for i in range(len(countList)):
        if countList[i] < currentNumPrey:
            for j in range(currentNumPrey - countList[i]):
                preyLifeTimes.append(i)
            currentNumPrey = countList[i]
    for i in range(countList[-1]):
        preyLifeTimes.append(len(countList))
    return preyLifeTimes

def listStats(numList):
    """takes in a list of numbers and returns [average, standard deviation, 95% confidence interval]"""
    avg = stats.mean(numList)
    std = stats.stdev(numList)
    sem = std / m.sqrt(len(numList))
    z = 1.96 # 95% ci
    ci = (avg - z*sem, avg + z*sem)
    return [avg, std, ci]

def survivalGraphFromCSV(filename, groupParam):
    """takes in a csv file of runs and plots prey count over time, organized by color with respect to the indicated grouping parameter (ie targetedAware)"""
    df = pd.read_csv(filename)
    numGroups = len(df[groupParam].unique())
    prey_df = df.groupby(groupParam)["preyCountOverTime"] # get the numpy series with preyCountOverTime column for all values grouped according to groupParam
    colorIter=iter(plt.cm.jet(np.linspace(0, 0.9, numGroups))) # only set label for first in each group, keep this color till we get to the next group
    for param, group in prey_df: # loop through groups. param is the thing we are grouping by. group is the group itself
        color = next(colorIter) # change the color with new group
        firstInGroup = True 
        for countStr in group: # loop through preyCountOverTime string "lists" within a group. Iterating though group gives values!
            counts = strToNumList(countStr) 
            if firstInGroup: # change label if first in group
                plt.plot(counts, label=groupParam + " " + str(param), color=color)
            else:
                plt.plot(counts, color=color)
            firstInGroup = False
    plt.xlabel("time (# of steps)")
    plt.ylabel("population (# of prey)")
    plt.title("Prey Population Over Time")
    plt.legend()
    plt.show()


def strToNumList(listStr):
    listStr = listStr.replace(" ","")
    listStr = listStr.strip("[]")
    listNum = [int(num) for num in listStr.split(",")]
    return listNum

def heatMapFromCSV(fileName, groupParam1, groupParam2): 
    """
    Inputs: 
        fileName: string, the csv file name
        groupParam1: string, the first variable 
        groupParam2: string, the second variable to consider"""
    df = pd.read_csv(fileName)
    
    data = df.pivot_table(index=groupParam1, columns=groupParam2, values='stepCount')

    heat_map = sb.heatmap(data, annot=True)
    plt.show()

def avgTargetInfo(targetInfo, graph=False):
    probList, durationList = targetInfo
    s_avg, s_std, s_ci = listStats(probList)
    d_avg, d_std, d_ci = listStats(durationList)
    if graph:
        plt.hist(durationList)
        plt.title("Distribution for Duration of Targeting")
        plt.xlabel("Duration of Targeting (timesteps")
        plt.ylabel("Count")
        plt.show()
    return s_avg, s_ci, d_avg, d_ci

def loadCautiousDict(filename):
    data = pd.read_csv(filename)
    paramDict = data.set_index('keys').T.to_dict('list')
    
    for key, value in paramDict.items():
        prob, length = ast.literal_eval(value[0])
        if len(length) > 200:
            kde = FFTKDE(kernel='gaussian', bw='ISJ').fit(length)
            kde.evaluate()
            paramDict[key] = prob, kde.bw, length

    return paramDict