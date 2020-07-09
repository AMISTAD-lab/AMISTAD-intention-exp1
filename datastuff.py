import helpData as hd
import pandas as pd
import matplotlib.pyplot as plt
import copy


def filterDataFrame(data, filterlist):
    data = copy.deepcopy(data)
    for param, value in filterlist:
        booleans = data[param] == value
        data = data[booleans]
    return data

def linearRunGraph(filename, param):
    data = pd.read_csv(filename)
    plt.style.use('ggplot')
    plt.rc('font', family='serif')
        
    df0 = filterDataFrame(data, [["targetedAware", True], ["proximityAware", True]])
    df1 = filterDataFrame(data, [["targetedAware", False], ["proximityAware", True]])
    df2 = filterDataFrame(data, [["targetedAware", False], ["proximityAware", False]])

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
            group = group["preyCountOverTime"]
            groupLifeTimes = []
            for countStr in group:
                countList = hd.strToNumList(countStr)
                lifetimes = hd.lifeTimes(countList)
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
    ax.set_xlabel(r"prey-predator ratio")
    ax.tick_params(axis='both', which='major', labelsize=9, direction='in')
    plt.legend()
    plt.title(r"Prey Lifespan vs Prey-Predator Ratio")
    plt.rc('text', usetex=True)
    plt.show()


#linearRunGraph("ppratio.csv", "preyPredRatio")