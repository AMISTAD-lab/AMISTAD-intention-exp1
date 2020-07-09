"""hunger.py
New file to re-evaluate prey count over time according to prey hunger/starvation.
Todo: 
Account for when prey die because of predators! Need to decrement only UP TO the frame in which a prey is eaten by a predator.
the order of the prey in the food per prey list is such that the first prey in the foodperpreyList is eaten first. 
Idea: loop through predator lists. Save the time steps that they eat prey, in increasing order.

When going through first prey list, IF this prey dies of hunger at timestep X, then compare timestep X to timestep Y at which
it was supposed to be killed by predator. If timestep X is smaller, then decrement up to timestep Y at which it was killed by predator. 
If it was killed by predator already (WAIT prey cannot eat when they are killed so throw error.)

NOTE: prey stay alive on the frame that they die! The length of prey list is added before predators have a chance to eat the prey!
"""

import csv
import pandas as pd
import ast




def getNewPreyCountOverTimeList(foodPerPreyList, preyCountOverTimeList, preyPerPredList, numTimeStep):
    """
    Inputs:
        foodPerPreyList: The foodPerPreyList for a single run. Prey that die first are included first. List containing one element for each prey. Each element is a list of elements of the form [timeFrame, # of food] for each food that the prey eats.
        preyCountOverTimeList: The preyCountOverTimeList for a single run.
        preyPerPredList: The preyPerPredList for a single run. Allows us to determine when prey die.
        numTimeStep: the number of steps we consider to be starve"""
    #print("foodPerPreyList is", foodPerPreyList)
    foodPerPreyList = ast.literal_eval(foodPerPreyList) # convert to list type
    preyCountOverTimeList = ast.literal_eval(preyCountOverTimeList)
    preyPerPredList = ast.literal_eval(preyPerPredList)
    preyEatenTimestamps = getPreyEatenTimestamps(preyPerPredList) # get timestamps from overall list

    # loop through the list of prey
    for preyFoodList in foodPerPreyList:
        # Don't do anything if the prey never ate
        if len(preyFoodList) != 0:
            isPreyStarved = False  # initialize variables to be used in loop
            timeStepIndex = 0
            prevEatTimeStep = preyFoodList[0][0] # Initialize this to the first timestep the prey ate. 
            # loop through each time step for a given prey (until prey dies of hunger :( )
            while (timeStepIndex < len(preyFoodList) and not isPreyStarved):
                #print("preyFoodList[timeStepIndex] is", preyFoodList[timeStepIndex])
                currentTimeStep = preyFoodList[timeStepIndex][0]
                #print("currentTimeStep is", currentTimeStep)
                isPreyStarved = currentTimeStep - prevEatTimeStep > numTimeStep
                if isPreyStarved: # revise prey count list
                    if len(preyEatenTimestamps) == 0: # if prey was never eaten, set this time step to the last possible time step.
                        preyEatenTimeStep = len(preyCountOverTimeList) - 1
                    else: 
                        preyEatenTimeStep = min(preyEatenTimestamps) # if prey was eaten, get time step at which it was eaten and remove it from the list.
                        preyEatenTimestamps.remove(preyEatenTimeStep)
                    preyCountOverTimeList = revisePreyCountList(preyCountOverTimeList, currentTimeStep, preyEatenTimeStep)
                prevEatTimeStep = currentTimeStep
                timeStepIndex += 1
    return preyCountOverTimeList


def revisePreyCountList(preyCountList, preyStarvedTimeStep, preyEatenTimeStep):
    """Revises the prey count list according to the time step at which a single prey dies.
    Decreases the prey count for all timeSteps after the given timeStep, including the given timestep.
    Input:
        preyCountList: list, the current preyCountList.
        preyDiedTimeStep: int, the timeStep at which a prey died.
    Returns:
        newPreyCountList: list, the new preyCountList
    """
    if preyStarvedTimeStep < preyEatenTimeStep:
        print("decreasing starting at timestep", preyStarvedTimeStep)
        for timeStep in range(preyStarvedTimeStep, preyEatenTimeStep + 1): # the +1 is because the prey count is not decremented on the exact frame that a prey is eaten.
            preyCountList[timeStep] -= 1
    
    return preyCountList


def getPreyEatenTimestamps(preyPerPredList):
    """Obtain a list of timestamps at which a prey dies.
    Inputs:
        preyPerPredList: the list of predators, with the time stamps at which they eat prey."""
    timeStepList = []
    timeStepIndex = 0
    for preyList in preyPerPredList:
        if len(preyPerPredList) != 0:
            while(timeStepIndex < len(preyList)):
                currentTimeStep = preyList[timeStepIndex][0]
                timeStepList.append(currentTimeStep)
                timeStepIndex += 1
    return timeStepList
    
            


def testGetNewPreyCountOverTimeList(filename, rowNum, numTimeStep):
    """filename = file.csv
    numTimeStep = the number of steps we consider to be starve"""
    col_list = ["foodPerPrey", "preyCountOverTime", "preyPerPred"] # get info from dataframe
    df = pd.read_csv(filename, usecols=col_list)
    preyList = df["foodPerPrey"][rowNum]
    preyCountOverTimeList = df["preyCountOverTime"][rowNum]
    preyPerPredList = df["preyPerPred"][rowNum]
    print("old preyCountOverTimeList is", preyCountOverTimeList)
    print("new preyCountOverTimeList is", getNewPreyCountOverTimeList(preyList, preyCountOverTimeList, preyPerPredList, numTimeStep))


def strToNumList(listStr):
    listStr = listStr.replace(" ","")
    listStr = listStr.strip("[]")
    listNum = [int(num) for num in listStr.split(",")]
    return listNum

testGetNewPreyCountOverTimeList("spdfrac.csv", 0, 1000)