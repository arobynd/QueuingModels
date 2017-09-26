import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plotTestsWaitingTime(dataSets, labels, featureTimes, DirFileName):
    print ""
    print "Creating plot", DirFileName
    y = []
    f = []
    for data in dataSets:
        y.append(np.sum(data["WaitingTimeInQueue"]))
    for ft in featureTimes:
        f.append(ft)
    width = 1 / 1.5
    N = len(y)
    x = range(N)
    plt.figure(num=1, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')

    colors = ["r", "g", "b", "c", "y"]
    patterns = ["/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"]
    for i in range(N):
        # plt.bar(x[i], y[i], width, label=labels[i], color=colors[i%5])
        if i < len(colors) - 1:
            plt.bar(x[i], y[i], width, label=labels[i], color=colors[i % 5])
        else:
            plt.bar(x[i], y[i], width, label=labels[i], color=colors[i % 5], hatch=patterns[i % 10])
        plt.bar(x[i], f[i], width, bottom=y[i], color='m')
    plt.ylabel('Values')
    plt.xlabel('Waiting Time Addition')
    plt.legend(loc="center left", bbox_to_anchor=(0.88, 0.5))
    plt.savefig(DirFileName)
    plt.close()

def plotTestsAttendedAndSolvedInstances(dataSets, labels, DirFileName):
    print ""
    print "Creating plot", DirFileName
    y1 = []
    y2 = []
    for data in dataSets:
        y1.append(np.sum(data["Attended"]))
        y2.append(np.sum(data["Solved"]))

    n_groups = len(labels)

    #fig = plt.figure()
    ax = plt.subplots()
    index = np.arange(n_groups) +1
    bar_width = 0.35
    opacity = 0.7
    plt.bar(index, y1, bar_width, alpha=opacity,color='b',label='Attended Instances')
    plt.bar(index + bar_width, y2, bar_width,alpha=opacity,color='g',label='Solved Instances')
    plt.xlabel('Tests')
    plt.ylabel('Number of Instances')
    plt.title('Attended and Solved Instances')
    plt.xticks(index + bar_width , labels, rotation='vertical')
    plt.legend()
    plt.tight_layout()
    plt.savefig(DirFileName)
    plt.close()

def plotTestsSolvedInstances(dataSets, labels, DirFileName):
    print ""
    print "Creating plot", DirFileName
    y2 = []
    for data in dataSets:
        y2.append(np.sum(data["Solved"]))
    n_groups = len(labels)
    #fig = plt.figure()
    ax = plt.subplots()
    index = np.arange(n_groups) +1
    bar_width = 0.35
    opacity = 0.7
    plt.bar(index + bar_width, y2, bar_width,alpha=opacity,color='g',label='Solved Instances')
    plt.xlabel('Tests')
    plt.ylabel('Number of Instances')
    plt.title('Solved Instances')
    plt.xticks(index + bar_width , labels, rotation='vertical')
    plt.legend()
    plt.tight_layout()
    plt.savefig(DirFileName)
    plt.close()



def plotRealValuesAndPredictions(subDir,DirFileName):
    datSet = "../myTrainedModelsAndResults/" + subDir + "/1.INDU(minisat)(regression)(predictions)all.csv"
    simData = pd.read_csv(datSet)
    # simData["RealServiceTime"] = np.ceil(10 ** simData["actual"])
    # simData["PredictedServiceTime"] = np.ceil(10 ** simData["predicted"])
    x = np.ceil(10 ** simData["actual"])
    y = np.ceil(10 ** simData["predicted"])
    plt.figure(num=1, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
    plt.plot(x, y, 'b^')
    plt.xlabel("Real Time")
    plt.ylabel("Predicted Time")
    plt.plot([0, 3500], [0, 3500], linewidth=1.0, color="g")  # Diagonal green line
    plt.savefig(DirFileName)
    #plt.show()
    plt.close()


def plotRealValuesAndPredictions2(subDir, DirFileName):
    datSet = "../myTrainedModelsAndResults/" + subDir + "/1.INDU(minisat)(regression)(predictions)all.csv"
    simData = pd.read_csv(datSet)
    # simData["RealServiceTime"] = np.ceil(10 ** simData["actual"])
    # simData["PredictedServiceTime"] = np.ceil(10 ** simData["predicted"])
    x = simData["actual"]
    y = simData["predicted"]
    plt.figure(num=1, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
    plt.plot(x, y, 'b^')
    plt.xlabel("Real Time")
    plt.ylabel("Predicted Time")
    plt.plot([-3, 4], [-3, 4], linewidth=1.0, color="g")  # Diagonal green line
    plt.savefig(DirFileName)
    #plt.show()
    plt.close()


