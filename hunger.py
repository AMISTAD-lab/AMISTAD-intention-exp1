"""hunger.py
Data analysis methods involving prey hunger.

genNewStackPlotvsTimeGraph(): generates separate survival stack plots for each mode.
    Usage: 
    genNewStackPlotvsTimeGraph({csv file name}, {maximum fasting interval}, filterList={filter list}, includeCaution={True if generating a caution graph, False otherwise})
    ex) genNewStackPlotvsTimeGraph("results/preyPredRatio3.csv", 2000, filterList=[["preyPredRatio", 4]], includeCaution=True)

genStackPlotvsTimeGraph(): generates survival stack plots for each mode that are all combined in one figure. Does not graph caution.

plotPerceptionLineGraph(xValList, yValList, modes, xlabel, ylabel, title): Plots 3 line graphs (one for each intention mode).

avgFoodPerPrey(filename, paramVary): A graph varying the food per prey with another parameter.

"""

import csv
import pandas as pd
import ast
import helpData as ds # imports filterList method
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc

def getPerceptionTierDataframes(filename):
    """Takes in a csv file and returns data frames according to perception tiers 
    Inputs:
        filename: String, the name of the csv file to read from"""
    data = pd.read_csv(filename)
    df0 = ds.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True]])
    df1 = ds.filterDataFrame(data, [["targetedAware", False], ["proximityAware", True]])
    df2 = ds.filterDataFrame(data, [["targetedAware", False], ["proximityAware", False]])
    dfs = [df0, df1, df2]
    modes = [r"Proximity and Attention Awareness", r"Only Proximity Awareness", r"No Awareness"]
    return modes, dfs

def avgFoodPerPrey(filename, paramVary):
    """Displays a graph varying food per prey with another parameter
    Inputs: 
        filename: String, the csv file to read from
        paramVary: String, the parameter to vary
    """
    modes, dfs = getPerceptionTierDataframes(filename)
    xValList = []
    yValList = []
    for i in range (3):
        df = dfs[i]
        paramList = []
        avgNumList = []
        for param, dataframe in df.groupby(paramVary):
            paramList.append(param)
            preyList = dataframe["foodPerPrey"]
            superTotal = 0
            superEatPrey = 0
            for run in dataframe.index:
                foodPerPreyList = ast.literal_eval(preyList[run])
                eatPrey = len(foodPerPreyList)
                noEatPrey = countEmptyList(foodPerPreyList, True)
                totalPrey = eatPrey + noEatPrey
                superTotal += totalPrey #
                superEatPrey += eatPrey
            avgNumList.append(superTotal / superEatPrey)
        xValList.append(paramList)
        yValList.append(avgNumList)
    print("xValList is", xValList)
    print("yValList is", yValList)
    plotPerceptionLineGraph(xValList, yValList, modes, paramVary, r"average # of food eaten per prey", " " )    

def countEmptyList(inputList, isOuterList = True):
    """Helper method for avgFoodPerPrey, takes in a list and counts all the empty lists inside it
    Inputs:
        inputList: list, the list to analyze
        isOuterList: boolean"""
    if inputList == []:
        if isOuterList:
            return 0
        else:
            return 1
    elif isinstance(inputList, list):
        return sum(countEmptyList(item, False) for item in inputList) 
    else:
        return 0

def plotPerceptionLineGraph(xValList, yValList, modes, xlabel, ylabel, title):
    """ Plots a line graph with 3 lines, one for each intention mode. The lines themselves vary
    upon a particular parameter (see xValList)
    Inputs:
        xValList: list, a list of 3 lists, each of which is the x-values for the parameter varied for a given intention mode. Should all be the same.
        yValList: list, a list of 3 lists, each of which is the y-values for a given intention mode.
        modes: list, List of intention modes
        xlabel: String, the parameter we are varying
        ylabel: String, the value
        title: String, the title of the graph"""
    plt.style.use('ggplot')
    colorIter = iter(['#4FADAC', '#5386A6', '#2F5373'])
    for lineNum in range(len(xValList)):
        color = next(colorIter)
        plt.plot(xValList[lineNum], yValList[lineNum], label=modes[lineNum], color=color, linewidth=2)
    ax = plt.gca()
    ax.set_ylabel("" + ylabel)
    ax.set_xlabel("" + xlabel)
    ax.tick_params(axis='both', which='major', labelsize=9, direction='in')
    plt.legend(fontsize=11)
    plt.title("" + title)
    plt.show()


def genStackPlotvsTimeGraph(filename, numTimeStep, filterList=None):
    """Generates a stack plot of prey states over time step for Intention and 
    non intention modes. NOTE: Will probably need to include cautiousness
    as another graph later.
    NOTE: Requires the last dataframe in dataframes to be the one that makes prey die the fastest
    Inputs:
        filename: the name of the csv file to read from
        numTimeStep: the time for which the prey can go without eating before
        dying of hunger.
        filterList: a filter list to filter the runs by. Most likely use if 
            we need to filter to only get the standard seed from a csv with 
            varied parameters. eg. [["predSightDistance", 10]]"""
    modes, dfs = getPerceptionTierDataframes(filename)

    plt.rc('font', family='serif')
    fig, axes = plt.subplots(1,3 )
    fig.tight_layout(w_pad=1, h_pad=1, rect=[0,0,.9, .9])
    fig.suptitle("Prey Status over Time", fontsize=16)
    axs = axes.flat
    plt.style.use('ggplot')
    colorList = ['#4FADAC', '#5386A6', '#2F5373']

    maxX = 0 # initialize. This will be set later and will make all x axes the same. 

    graphInfo = []

    # loop through dataframes. We will want one stackplot per mode.
    for perceptionNum in range(len(dfs)):
        perceptionDf = dfs[perceptionNum]
        # filter
        if filterList != None:
            perceptionDf = ds.filterDataFrame(perceptionDf, filterList)
        aliveOverTime, eatenOverTime, starvedOverTime = helpStackPlot(perceptionDf, numTimeStep)
        graphInfo.append([aliveOverTime, starvedOverTime, eatenOverTime])
    
    maxX = calcMaxX(graphInfo)
       
    for perceptionNum in range(len(dfs)):
        # x-list is timestep
        x_list = range(maxX)

        axs[perceptionNum].set_title(modes[perceptionNum], fontsize=12)        
        axs[perceptionNum].set_ylabel("" + "Average Number of Prey", fontsize=10)
        axs[perceptionNum].set_xlabel("" + "Timestep of Simulation", fontsize=10)
        axs[perceptionNum].tick_params(axis='both', which='major', labelsize=9, direction='in')
        axs[perceptionNum].set(ylim=(0, 20), xlim=(0, maxX))

        plt.sca(axs[perceptionNum])
        yList1 = extendList(graphInfo[perceptionNum][0][:maxX], maxX)
        yList2 = extendList(graphInfo[perceptionNum][1][:maxX], maxX)
        yList3 = extendList(graphInfo[perceptionNum][2][:maxX], maxX)
        
        plt.stackplot(x_list, yList1, yList2, yList3, colors=colorList)    
    fig.legend(labels=["Alive", "Starved", "Eaten"])
    plt.rc('text', usetex=True)
    plt.show()

def getPerceptionDataframesCaution(filename, cfilename):
    """New version of getPerceptionTierDataframes() that includes the caution mode.
    Inputs:
        filename: the filename to read from"""
    data = pd.read_csv(filename)
    df0 = ds.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True]])
    df1 = ds.filterDataFrame(data, [["targetedAware", False], ["proximityAware", True]])
    df2 = ds.filterDataFrame(data, [["targetedAware", False], ["proximityAware", False]])
    df3 = pd.read_csv(cfilename)

    dfs = [df0, df1, df2, df3]
    modes = [r"Proximity + Attention", r"Proximity Only", r"Unaware", r"Cautious"]
    return modes, dfs

    

def genNewStackPlotvsTimeGraph(filename, numTimeStep, filterList=None, cfilename=None):
    """Generates separate stack plots of prey states over time step for intention and 
    non intention modes. Includes an option to make a stackplot for the caution mode.

    Inputs:
        filename: String, the name of the csv file to read from
        numTimeStep: Int, the time for which the prey can go without eating before
        dying of hunger.
        filterList: List, a filter list to filter the runs by. Most likely use if 
            we need to filter to only get the standard seed from a csv with 
            varied parameters. eg. [["predSightDistance", 10]]"""
    
    labelsize = 18
    legendsize = 14
    titlesize = 20
    ticksize = 16

    # Determine whether the "Cautious" stackplot should be made.
    if cfilename:
        modes, dfs = getPerceptionDataframesCaution(filename, cfilename)
    else:
        modes, dfs = getPerceptionTierDataframes(filename)

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.style.use('ggplot')
    colorList = ['#4FADAC', '#5386A6', '#2F5373']

    maxX = 0 # Initialize. This will be set later and will make all x axes the same. 

    graphInfo = []

    # loop through dataframes. We will want one stackplot per mode.
    for perceptionNum in range(len(dfs)):
        perceptionDf = dfs[perceptionNum]
        # filter
        if filterList != None:
            perceptionDf = ds.filterDataFrame(perceptionDf, filterList)
        aliveOverTime, eatenOverTime, starvedOverTime = helpStackPlot(perceptionDf, numTimeStep)
        graphInfo.append([aliveOverTime, starvedOverTime, eatenOverTime])
    
    maxX = calcMaxX(graphInfo)
       
    for perceptionNum in range(len(dfs)):

        fig = plt.figure(figsize=[5, 5])

        axs = fig.gca()

        # x-list is timestep
        x_list = range(maxX)

        axs.set_title("" + modes[perceptionNum], fontsize=titlesize, fontweight='bold')        
        axs.set_ylabel("" + "Average Number of Prey", fontsize=labelsize, fontweight='bold')
        axs.set_xlabel("" + "Timestep of Simulation", fontsize=labelsize, fontweight='bold')
        axs.tick_params(axis='both', which='major', labelsize=ticksize, direction='in')
        axs.set(ylim=(0, 20), xlim=(0, maxX))

        yList1 = extendList(graphInfo[perceptionNum][0][:maxX], maxX)
        yList2 = extendList(graphInfo[perceptionNum][1][:maxX], maxX)
        yList3 = extendList(graphInfo[perceptionNum][2][:maxX], maxX)
        plt.stackplot(x_list, yList1, yList2, yList3, colors=colorList) 
        plt.legend(labels=["Alive", "Starved", "Eaten"], prop={"size":legendsize})
        fig.tight_layout()
        fig.savefig("hungerstack" + str(perceptionNum), bbox_inches='tight', pad_inches=0)
    plt.close('all')

def calcMaxX(graphInfo):
    """Calculates the maximum x value given all the graph info. Maximum x value should be
    a bit greater than the x value that makes all but one of the graphs show 0 prey alive.
    Inputs:
        graphInfo: List of lists. Each inner list is of the form [aliveOverTime, eatenOverTime, starvedOverTime].
        Each inner list corresponds to one perception mode.
    """
    xRanges = [len(graphInfo[i][0]) for i in range(len(graphInfo))] # xRange is the length of the first list in graphInfo for a given intention mode.
    xRanges.remove(max(xRanges)) # remove greatest value; this is the value we want to cut.
    return max(xRanges) + 500

def extendList(listIn, extendNum):
    """Extends a list till extendNum (but not including extendNum).
    Inputs:
        listIn: List, the list to be extended
        extendNum: Int, the index at which to stop extending (exclusive)"""
    lengthDiff = extendNum - len(listIn)
    listIn += lengthDiff * [listIn[-1]]
    return listIn


def helpStackPlot(dataframe, numTimeStep):
    """ Takes in a dataframe with a single perception mode.
    Returns lists of average preyAlive over time, prey Eaten over time, and prey starved over time.
    Inputs:
        dataframe: the pandas dataframe to make the stackplot from
        numTimeStep: the number of time steps a prey can go without food until it starves.
    """
    # get info
    foodPerPreyList = dataframe["foodPerPrey"]
    preyCountOverTimeList = dataframe["preyCountOverTime"]
    preyPerPredList = dataframe["preyPerPred"]


    # hold all alive y-arrays for this perception type, same for eaten and starved.
    aliveOverTimeLists = []
    eatenOverTimeLists = []
    starvedOverTimeLists = []

    # loop through runs
    for run in dataframe.index:
        # get info
        # 3 y-arrays: alive, starved, eaten.
        aliveOverTimeList, starvedOverTimeList = getNewPreyCountOverTimeList(foodPerPreyList[run], preyCountOverTimeList[run], preyPerPredList[run], numTimeStep)
        eatenOverTimeList = [aliveOverTimeList[0] - starvedOverTimeList[index] - aliveOverTimeList[index] for index in range(len(aliveOverTimeList))] # calculate number eaten.
        aliveOverTimeLists.append(aliveOverTimeList)
        eatenOverTimeLists.append(eatenOverTimeList)
        starvedOverTimeLists.append(starvedOverTimeList)

    # make all list lengths equal
    aliveOverTimeLists = equalizeListLengths(aliveOverTimeLists, "alive")
    eatenOverTimeLists = equalizeListLengths(eatenOverTimeLists, "eaten")
    starvedOverTimeLists = equalizeListLengths(starvedOverTimeLists, "starved")

    meanAliveOverTime = np.mean(np.array(aliveOverTimeLists), axis=0).tolist() # axis = 0 does elementwise means
    meanEatenOverTime = np.mean(np.array(eatenOverTimeLists), axis=0).tolist() 
    meanStarvedOverTime = np.mean(np.array(starvedOverTimeLists), axis=0).tolist() 
    return meanAliveOverTime, meanEatenOverTime, meanStarvedOverTime


def equalizeListLengths(listIn, listType, maxLength=None):
    """ Makes all lists the same length. Uses the length of the maximum length list.
    Inputs:
        listIn: list, the list whose sublists we want to equalize lengths.
        listType: String, the type of list we are equalizing"""
    if maxLength == None:
        maxLength = max(map(len, listIn)) 
    for index in range(len(listIn)):
        # check if it meets the max length, otherwise add values to end.
        lengthDiff = maxLength - len(listIn[index])
        if lengthDiff != 0:
            if listType == "alive":
                listIn[index] += lengthDiff * [0] # should be 0 at end for sims that end early
            elif listType == "eaten":
                listIn[index] += lengthDiff * [listIn[index][-1] + 1] # values added are same as last value in list plus one, because last prey died when predator ate it.
            else:
                listIn[index] += lengthDiff * [listIn[index][-1]] # values added are same as last value in list.
    return listIn
    

def getNewPreyCountOverTimeList(foodPerPreyList, preyCountOverTimeList, preyPerPredList, numTimeStep):
    """
    Account for when prey die because of predators! Returns a new preyCountOverTime list.
    Inputs:
        foodPerPreyList: The foodPerPreyList for a single run. Prey that die first are included first. List containing one element for each prey. Each element is a list of elements of the form [timeFrame, # of food] for each food that the prey eats.
        preyCountOverTimeList: The preyCountOverTimeList for a single run.
        preyPerPredList: The preyPerPredList for a single run. Allows us to determine when prey die.
        numTimeStep: the number of steps we consider to be starve"""
    foodPerPreyList = ast.literal_eval(foodPerPreyList) # convert to list type
    preyCountOverTimeList = ast.literal_eval(preyCountOverTimeList)
    preyPerPredList = ast.literal_eval(preyPerPredList)
    preyEatenTimestamps = getPreyEatenTimestamps(preyPerPredList) # get timestamps from overall list
    preyStarvedOverTimeList = [0] * len(preyCountOverTimeList) # create a list of number of prey that have starved.
    testCount = 0
    for preyFoodList in foodPerPreyList:
        testCount += 1
        # If the prey never ate, immediately check if it starved or died from being eaten, and act accordingly
        if len(preyFoodList) == 0:
            preyEatenTimeStep, preyEatenTimestamps = getPreyEatenTimeStep(preyEatenTimestamps, preyCountOverTimeList)
            preyCountOverTimeList, preyStarvedOverTimeList = revisePreyCountList(preyCountOverTimeList, preyStarvedOverTimeList, numTimeStep, preyEatenTimeStep)
        else:
            # initialize variables to be used in loop
            isPreyStarved = False
            timeStepIndex = 0
            prevEatTimeStep = 0

            # loop through each time step for a given prey
            while (timeStepIndex < len(preyFoodList) and not isPreyStarved):
                currentTimeStep = preyFoodList[timeStepIndex][0]
                isPreyStarved = (currentTimeStep - prevEatTimeStep) > numTimeStep
                if isPreyStarved: # revise prey count list 
                    preyEatenTimeStep, preyEatenTimestamps = getPreyEatenTimeStep(preyEatenTimestamps, preyCountOverTimeList)
                    preyCountOverTimeList, preyStarvedOverTimeList = revisePreyCountList(preyCountOverTimeList, preyStarvedOverTimeList, prevEatTimeStep + numTimeStep, preyEatenTimeStep)
                prevEatTimeStep = currentTimeStep
                timeStepIndex += 1
    return preyCountOverTimeList, preyStarvedOverTimeList


def revisePreyCountList(preyCountList, preyStarvedList, preyStarvedTimeStep, preyEatenTimeStep):
    """Revises the prey count list according to the time step at which a single prey dies. Helper method for 
    getNewPreyCountOverTimeList()
    Decreases the prey count for all timeSteps after the given timeStep, including the given timestep.
    Input:
        preyCountList: List, the current preyCountList.
        preyDiedTimeStep: Int, the timeStep at which a prey died.
    Returns:
        newPreyCountList: List, the new preyCountList
    """
    if preyStarvedTimeStep < preyEatenTimeStep:
        # revise preyCountList
        for timeStep in range(preyStarvedTimeStep, preyEatenTimeStep + 1): # the +1 is because the prey count is not decremented on the exact frame that a prey is eaten.
            preyCountList[timeStep] -= 1
        # revise preyStarvedList
        for timeStep in range(preyStarvedTimeStep, len(preyCountList)):
            preyStarvedList[timeStep] += 1
    return preyCountList, preyStarvedList


def getPreyEatenTimeStep(preyEatenTimestamps, preyCountOverTimeList):
    """Helper method for getNewPreyCountOverTimeList."""
    if len(preyEatenTimestamps) == 0: # if prey was never eaten, set this time step to the last possible time step.
        preyEatenTimeStep = len(preyCountOverTimeList) - 1
    else: 
        preyEatenTimeStep = min(preyEatenTimestamps) # if prey was eaten, get time step at which it was eaten and remove it from the list.
        preyEatenTimestamps.remove(preyEatenTimeStep)
    return preyEatenTimeStep, preyEatenTimestamps


def getPreyEatenTimestamps(preyPerPredList):
    """Obtain a list of timestamps at which a prey is eaten by predators.
    Helper method for getNewPreyCountOverTimeList()
    Inputs:
        preyPerPredList: the list of predators, with the time stamps at which they eat prey."""
    timeStepList = []
    for predList in preyPerPredList:
        for eatenList in predList:
            numPreyEaten = eatenList[1]
            currentTimeStep = eatenList[0]
            timeStepList += [currentTimeStep] * numPreyEaten # account for predators that eat multiple prey in one timestep
    return timeStepList
    

def getEatenStarvedRatio(dataframe, numTimeStep):
    """Get the average eaten: starved ratio of prey that die in a given dataframe.
    Inputs:
        dataframe: the dataframe from which to compute the average ratio.
        numTimeStep: Int, the number of time steps a prey has before dying of hunger"""
    foodPerPreyList = dataframe["foodPerPrey"]
    preyCountOverTimeList = dataframe["preyCountOverTime"]
    preyPerPredList = dataframe["preyPerPred"]

    totalPreyStarved = 0
    totalPreyDied = 0

    # loop through each run
    for run in dataframe.index:
        # get total number of prey starved
        newPreyCountOverTimeList, preyStarvedOverTimeList = getNewPreyCountOverTimeList(foodPerPreyList[run], preyCountOverTimeList[run], preyPerPredList[run], numTimeStep) 
        # get total number prey eaten
        numPreyDied = newPreyCountOverTimeList[0] - newPreyCountOverTimeList[-1]
        # increment totals
        totalPreyStarved += preyStarvedOverTimeList[-1] 
        totalPreyDied += numPreyDied

    return totalPreyStarved/totalPreyDied  # return the ratio.


def genEatenStarvedRatioGraph(filename, numTimeStep, paramIn=None):
    """If paramIn is given, generates a graph showing the prey eaten: prey starved ratio graphed vs. paramIn.
    Otherwise, generates a graph with just the ratio and different intention modes. 
    Inputs: 
        filename: String, the name of the csv file to make a graph from
        paramIn: String, the parameter to vary
        numTimeStep: Int, the number of time steps a prey has before dying of hunger"""
    # get 3 dataframes split based on perception
    modes, dfs = getPerceptionTierDataframes(filename) 
    # If given a parameter, filter all dataframes into different dataframes based on parameter.
    # Otherwise, simply calculate ratios on the different perception dataframes
    if paramIn != None:
        allParamList = [] # lists to use for graph
        allRatioList = []
        for i in range(0, len(dfs)): # loop through perception dataframes
            perceptionDf = dfs[i] 
            paramList = [] # info to display in graphf
            ratioList = []
            for param, paramDf in perceptionDf.groupby(paramIn):
                paramList.append(param)
                # get ratio
                ratioList.append(getEatenStarvedRatio(paramDf, numTimeStep))
            allParamList.append(paramList)
            allRatioList.append(ratioList)
        plotPerceptionLineGraph(allParamList, allRatioList, modes, paramIn, "Proportion of Prey Deaths due to Starvation", paramIn + " vs. Proportion of Prey Deaths due to Starvation")

def testGetNewPreyCountOverTimeList(filename, rowNum, numTimeStep):
    """ Testing method
    filename: String, the file name of the csv to read from
    numTimeStep: Int, the number of steps at which we consider prey to be starved"""
    col_list = ["foodPerPrey", "preyCountOverTime", "preyPerPred"]
    df = pd.read_csv(filename, usecols=col_list)
    preyList = df["foodPerPrey"][rowNum]
    preyCountOverTimeList = df["preyCountOverTime"][rowNum]
    preyPerPredList = df["preyPerPred"][rowNum]
    print("old preyCountOverTimeList is\n", preyCountOverTimeList)
    newPreyCountList, preyStarvedOverTimeList = getNewPreyCountOverTimeList(preyList, preyCountOverTimeList, preyPerPredList, numTimeStep)[0]
    print("new preyCountOverTimeList is\n", newPreyCountList)