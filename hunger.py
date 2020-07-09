"""hunger.py
Data analysis methods involving prey hunger.

Brainstorm: Things to analyze with hunger:
- Average food eaten per prey across different modes of intention.
    - Maybe graph this against preySightDistance, or something else?
- ratio of prey eaten by predators to prey dying from hunger. across different modes of intention
- Possibly?? When prey eat (i.e. graph eating food w/ respect to timestep, 
    or make a histogram of timesteps at which food is eaten for different intention modes)
- 

Todo:
- make graph work with latex
- For genEatenStarvedRatioGraph(filename, numTimeStep, paramIn=None):, make it work without parameters.

"""

import csv
import pandas as pd
import ast
import datastuff as ds # imports filterList method
import matplotlib.pyplot as plt

def avgFoodPerPrey(filename, paramVary):
    """returns a list of average food per prey based on perception tier
    filename = csv file
    param = param to vary
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
                superTotal += totalPrey
                superEatPrey += eatPrey
            avgNumList.append(superTotal / superEatPrey)
        xValList.append(paramList)
        yValList.append(avgNumList)
    print("xValList is", xValList)
    print("yValList is", yValList)
    plotPerceptionLineGraph(xValList, yValList, modes, paramVary, "average number of food eaten by prey", "preySightDistance" )    
    #return avgNum



    """
def avgFoodPerPrey(filename, paramVary):
    returns a list of average food per prey based on perception tier

    filename = csv file
    param = param to vary
    
    modes, dfs = getPerceptionTierDataframes(filename)
    avgNum = []
    for i in range (3):
        df = dfs[i]
        paramList = []
        for param, dataframe in df.groupby(paramVary):
            paramList.append(param)
            preyList = df["foodPerPrey"]
            superTotal = 0
            superEatPrey = 0
            for run in df.index:
                foodPerPreyList = ast.literal_eval(preyList[run])
                eatPrey = len(foodPerPreyList)
                noEatPrey = countEmptyList(foodPerPreyList, True)
                totalPrey = eatPrey + noEatPrey
                superTotal += totalPrey
                superEatPrey += eatPrey
        avgNum.append(superTotal / superEatPrey)
    
    plotPerceptionLineGraph(avgNum, paramList, modes, paramVary, "average number of food eaten by prey", "preySightDistance" )    
    return avgNum
    """

def preyEatTime(filename):
    ...

def countEmptyList(inputList, isOuterList = True):
    "helper method for avgFoodPerPrey, takes in a list and count all the empty lists inside it"
    if inputList == []:
        if isOuterList:
            return 0
        else:
            return 1
    elif isinstance(inputList, list):
        return sum(countEmptyList(item, False) for item in inputList) 
    else:
        return 0

def getPerceptionTierDataframes(filename):
    """Takes in a csv file and returns data frames according to perception tiers """
    data = pd.read_csv(filename)
    df0 = ds.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True]])
    df1 = ds.filterDataFrame(data, [["targetedAware", False], ["proximityAware", True]])
    df2 = ds.filterDataFrame(data, [["targetedAware", False], ["proximityAware", False]])
    dfs = [df0, df1, df2]
    modes = [r"Proximity + Attention", r"Proximity Only", r"Unaware"]
    return modes, dfs

def plotPerceptionLineGraph(xValList, yValList, modes, xlabel, ylabel, title):
    """ Plots a line graph with 3 lines, one for each intention mode. The lines themselves vary
    upon a particular parameter (see xValList)
    Inputs:
        xValList: list, List of 3 lists, each of which is the x-values for the parameter varied for a given intention mode. Should all be the same.
        yValList: list, List of 3 lists, each of which is the y-values for a given intention mode.
        modes: list, List of intention modes
        xlabel: String, The parameter we are varying
        ylabel: String, the value
        title: String, The title of the graph"""
    colorIter = iter(['#4FADAC', '#5386A6', '#2F5373'])
    for lineNum in range(len(xValList)):
        color = next(colorIter)
        plt.plot(xValList[lineNum], yValList[lineNum], label=modes[lineNum], color=color, linewidth=2)
        #plt.fill_between(xValList[lineNum], low_ci, up_ci, color=color, alpha=.15)   
    ax = plt.gca()
    #ax.set(ylim=(0, 10000))
    ax.set_ylabel("" + ylabel) # the "r" is for latex
    ax.set_xlabel("" + xlabel)
    ax.tick_params(axis='both', which='major', labelsize=9, direction='in')
    plt.legend()
    plt.title("" + title)
    #plt.rc('text', usetex=True)
    plt.show()
    

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
        plotPerceptionLineGraph(allParamList, allRatioList, modes, paramIn, "Proportion of Prey Deaths due to Starvation", "Proportion of Prey Deaths due to Starvation vs. " + paramIn)
    #else:s
        #...
    

def getEatenStarvedRatio(dataframe, numTimeStep):
    """Get the average eaten: starved ratio of prey that die in a given dataframe.
    Inputs:
        dataframe: the dataframe from which to compute the average ratio.
        numTimeStep: Int, the number of time steps a prey has before dying of hunger"""
    foodPerPreyList = dataframe["foodPerPrey"]
    preyCountOverTimeList = dataframe["preyCountOverTime"]
    preyPerPredList = dataframe["preyPerPred"]

    print("foodPerPreyList is", foodPerPreyList)
    print("preyCountOverTimeList is", preyCountOverTimeList)
    print("preyPerPredList is", preyPerPredList)

    totalPreyStarved = 0 # totals
    totalPreyDied = 0

    # loop through each run
    for run in dataframe.index:
        # get total number of prey starved
        newPreyCountOverTimeList, numPreyStarved = getNewPreyCountOverTimeList(foodPerPreyList[run], preyCountOverTimeList[run], preyPerPredList[run], numTimeStep) 
        # get total number prey eaten
        numPreyDied = newPreyCountOverTimeList[0] - newPreyCountOverTimeList[-1]
        #numPreyEaten = numPreyDied - numPreyStarved 
        # increment totals
        totalPreyStarved += numPreyStarved
        totalPreyDied += numPreyDied

    return totalPreyStarved/totalPreyDied  # return the ratio.


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
    numPreyStarved = 0
    # loop through the list of prey
    for preyFoodList in foodPerPreyList:
        # Don't do anything if the prey never ate
        if len(preyFoodList) != 0:
            isPreyStarved = False  # initialize variables to be used in loop
            timeStepIndex = 0
            prevEatTimeStep = preyFoodList[0][0] # Initialize this to the first timestep the prey ate. 
            # loop through each time step for a given prey (until prey dies of hunger :( )
            while (timeStepIndex < len(preyFoodList) and not isPreyStarved):
                currentTimeStep = preyFoodList[timeStepIndex][0]
                isPreyStarved = (currentTimeStep - prevEatTimeStep) > numTimeStep
                if isPreyStarved: # revise prey count list
                    numPreyStarved += 1
                    if len(preyEatenTimestamps) == 0: # if prey was never eaten, set this time step to the last possible time step.
                        preyEatenTimeStep = len(preyCountOverTimeList) - 1
                    else: 
                        preyEatenTimeStep = min(preyEatenTimestamps) # if prey was eaten, get time step at which it was eaten and remove it from the list.
                        preyEatenTimestamps.remove(preyEatenTimeStep)
                    preyCountOverTimeList = revisePreyCountList(preyCountOverTimeList, currentTimeStep, preyEatenTimeStep)
                prevEatTimeStep = currentTimeStep
                timeStepIndex += 1
    return preyCountOverTimeList, numPreyStarved


def revisePreyCountList(preyCountList, preyStarvedTimeStep, preyEatenTimeStep):
    """Revises the prey count list according to the time step at which a single prey dies. Helper method for 
    getNewPreyCountOverTimeList()
    Decreases the prey count for all timeSteps after the given timeStep, including the given timestep.
    Input:
        preyCountList: list, the current preyCountList.
        preyDiedTimeStep: int, the timeStep at which a prey died.
    Returns:
        newPreyCountList: list, the new preyCountList
    """
    if preyStarvedTimeStep < preyEatenTimeStep:
        for timeStep in range(preyStarvedTimeStep, preyEatenTimeStep + 1): # the +1 is because the prey count is not decremented on the exact frame that a prey is eaten.
            preyCountList[timeStep] -= 1
    return preyCountList


def getPreyEatenTimestamps(preyPerPredList):
    """Obtain a list of timestamps at which a prey is eaten by predators.
    Helper method for getNewPreyCountOverTimeList()
    Inputs:
        preyPerPredList: the list of predators, with the time stamps at which they eat prey."""
    timeStepList = []
    for predList in preyPerPredList:
        for eatenList in predList:
            currentTimeStep = eatenList[0]
            timeStepList.append(currentTimeStep)
    return timeStepList
    
            


def testGetNewPreyCountOverTimeList(filename, rowNum, numTimeStep):
    """ Testing method
    filename = file.csv
    numTimeStep = the number of steps we consider to be starve"""
    col_list = ["foodPerPrey", "preyCountOverTime", "preyPerPred"] # get info from dataframe
    df = pd.read_csv(filename, usecols=col_list)
    preyList = df["foodPerPrey"][rowNum]
    preyCountOverTimeList = df["preyCountOverTime"][rowNum]
    preyPerPredList = df["preyPerPred"][rowNum]
    #print("old preyCountOverTimeList is\n", preyCountOverTimeList)
    newList = getNewPreyCountOverTimeList(preyList, preyCountOverTimeList, preyPerPredList, numTimeStep)[0]
    #print("new preyCountOverTimeList is\n", newList)

#testGetNewPreyCountOverTimeList("spdfrac.csv", 0, 2000)
avgFoodPerPrey("spdfrac.csv", paramVary = "speedFrac")
#genEatenStarvedRatioGraph("spdfrac.csv", 1000, paramIn="speedFrac")
