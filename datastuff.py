import helpData as hd
import pandas as pd
import matplotlib.pyplot as plt
import copy
import hunger as h

def linearRunGraph(filename, param, n_steps):
    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    plt.rc('font', family='serif')
        
    df0 = hd.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True]])
    df1 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", True]])
    df2 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", False]])

    dfs = [df0, df1, df2]
    modes = [r"Proximity + Attention", r"Proximity Only", r"Unaware"]

    colorIter = iter(['#4FADAC', '#5386A6', '#2F5373'])
    
    for i in range(3):
        df = dfs[i]
        paramValues = []
        survival = []
        up_ci = []
        low_ci = []

        for val, group in df.groupby(param):
            groupLifeTimes = []
            for index, run in group.iterrows():
                counts = run["preyCountOverTime"]
                foodPerPrey = run["foodPerPrey"]
                preyPerPred = run["preyPerPred"]
                revisedCounts, preyStarved = h.getNewPreyCountOverTimeList(foodPerPrey, counts, preyPerPred, n_steps)
                lifetimes = hd.lifeTimes(revisedCounts)
                groupLifeTimes += lifetimes
            
            avg, std, ci = hd.listStats(groupLifeTimes)

            paramValues.append(val)
            survival.append(avg)
            low_ci.append(ci[0])
            up_ci.append(ci[1])

        color = next(colorIter)
        plt.plot(paramValues, survival, label=modes[i], color=color, linewidth=2)
        plt.fill_between(paramValues, low_ci, up_ci, color=color, alpha=.15)
    
    ax = plt.gca()
    ax.set(ylim=(0, 10000))
    ax.set_ylabel(r"prey lifespan (time steps)")
    ax.set_xlabel(r"speed fraction (pred/prey)")
    ax.tick_params(axis='both', which='major', labelsize=9, direction='in')
    plt.legend()
    plt.title(r"Prey Lifespan vs Speed Fraction")
    plt.rc('text', usetex=True)
    plt.show()




def hungerGraph(filename):

    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    plt.rc('font', family='serif')
        
    df0 = hd.filterDataFrame(data, [["targetedAware", True], ["proximityAware", True], ["predSightAngle", 90]])
    df1 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", True], ["predSightAngle", 90]])
    df2 = hd.filterDataFrame(data, [["targetedAware", False], ["proximityAware", False], ["predSightAngle", 90]])

    dfs = [df0, df1, df2]
    modes = [r"Proximity + Attention", r"Proximity Only", r"Unaware"]

    colorIter = iter(['#4FADAC', '#5386A6', '#2F5373'])

    intention_list = []
    proximity_list = []
    unaware_list = []
    all_lists = [intention_list, proximity_list, unaware_list]
    
    x = [step for step in range(1, 10000+2, 500)]
    for n_steps in x:
        print("step:",n_steps)
        for i in range(3):
            df = dfs[i]
            groupLifeTimes = []
            for index, run in df.iterrows():
                counts = run["preyCountOverTime"]
                foodPerPrey = run["foodPerPrey"]
                preyPerPred = run["preyPerPred"]
                revisedCounts, preyStarved = h.getNewPreyCountOverTimeList(foodPerPrey, counts, preyPerPred, n_steps)
                lifetimes = hd.lifeTimes(revisedCounts)
                groupLifeTimes += lifetimes
            avg, std, ci = hd.listStats(groupLifeTimes)
            all_lists[i].append([avg, ci[0], ci[1]])

    for i in range(len(all_lists)):
        tier = all_lists[i]
        val = []
        l_ci = []
        u_ci = []
        for point in tier:
            a, lc, uc = point
            val.append(a)
            l_ci.append(lc)
            u_ci.append(uc)
        
        color = next(colorIter)
        plt.plot(x, val, label=modes[i], color=color, linewidth=2)
        plt.fill_between(x, l_ci, u_ci, color=color, alpha=.15)
    
    ax = plt.gca()
    ax.set(ylim=(0, 10000), xlim=(0,10000))
    ax.set_ylabel(r"prey lifespan (time steps)")
    ax.set_xlabel(r"maximum fasting interval (time steps)")
    ax.tick_params(axis='both', which='major', labelsize=9, direction='in')
    plt.legend()
    plt.title(r"Prey Lifespan vs Maximum Fasting Interval")
    plt.rc('text', usetex=True)
    plt.show()