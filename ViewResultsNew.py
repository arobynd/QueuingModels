#from SimulatorSources.plotResults import *
#from SimulatorSources.CalculateSATfeatureOverhead import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
    rects = plt.bar(index + bar_width, y2, bar_width,alpha=opacity,color='g')
    plt.xlabel('Tests')
    plt.ylabel('Number of Instances')
    plt.title('Solved Instances')
    plt.xticks(index + bar_width , labels, rotation='vertical')

    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2., 0.99 * height, '%d' % int(height), ha='center', va='bottom')

    plt.legend()
    plt.tight_layout()
    plt.savefig(DirFileName)
    plt.close()

#####################################################
#####################################################
#####################################################
#####################################################


def printLatex(simData1,simData2,simData3,simData4,simData5,simData6,simData7,simData8):
    print str(int(simData1["Solved"].sum())) + " & " + str(int(simData1["WaitingTimeInQueue"].sum()))+" & " + \
          str(int(simData2["Solved"].sum())) + " & " + str(int(simData2["WaitingTimeInQueue"].sum())) + " & " + \
          str(int(simData3["Solved"].sum())) + " & " + str(int(simData3["WaitingTimeInQueue"].sum())) + " & " + \
          str(int(simData4["Solved"].sum())) + " & " + str(int(simData4["WaitingTimeInQueue"].sum())) + " & " + \
          str(int(simData5["Solved"].sum())) + " & " + str(int(simData5["WaitingTimeInQueue"].sum())) + " & " + \
          str(int(simData6["Solved"].sum())) + " & " + str(int(simData6["WaitingTimeInQueue"].sum())) + " & " + \
          str(int(simData7["Solved"].sum())) + " & " + str(int(simData7["WaitingTimeInQueue"].sum())) + " & " + \
          str(int(simData8["Solved"].sum())) + " & " + str(int(simData8["WaitingTimeInQueue"].sum())) + " \\\\ \hline "

def printLatex2(simData1,simData2,simData3,simData4,simData5,simData6,simData7,simData8,simData9,simData10,simData11,simData12):
    print str(int(simData1["Solved"].sum())) +" & " + \
          str(int(simData2["Solved"].sum())) + " & " + \
          str(int(simData3["Solved"].sum())) + " & " + \
          str(int(simData4["Solved"].sum())) + " & " + \
          str(int(simData5["Solved"].sum())) + " & " + \
          str(int(simData6["Solved"].sum())) + " & " + \
          str(int(simData7["Solved"].sum())) + " & " + \
          str(int(simData8["Solved"].sum())) + " & " + \
          str(int(simData9["Solved"].sum())) + " & " + \
          str(int(simData10["Solved"].sum())) + " & " + \
          str(int(simData11["Solved"].sum())) + " & " + \
          str(int(simData12["Solved"].sum())) + " \\\\ \hline "


#####################################################
#####################################################
#####################################################
#####################################################



def plotResultsRealValues2(simResultsDir, dataSetPartition):
    DirResults = "SimulationResults/"+dataSetPartition+"/"+simResultsDir+"/"
    #
    DataFiles=[pd.read_csv(DirResults + "FCFS_N_R_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "FCFS_H_R_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "FCFS_N_RC_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "FCFS_H_RC_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF_N_R_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF_H_R_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF_N_RC_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF_H_RC_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "MIP_H_R_RealServiceTime_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP_H_RC_RealServiceTime_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP_H_H8_R_RealServiceTime_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP_H_H8_RC_RealServiceTime_G1_Simulation.csv")
               ]
    DataNames= ["FCFS(N-R)","FCFS(H-R)","FCFS(N-RC)","FCFS(H-RC)","SJF(N-R)","SJF(H-R)","SJF(N-RC)","SJF(H-RC)","MIP(H-R)","MIP(H-RC)","MIP(H8-R)","MIP(H8-RC)"]
    #OverHead = [0, 0, 0, 0, 0, 0, 0, 0]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    #printLatex2(DataFiles[0], DataFiles[1], DataFiles[2], DataFiles[3], DataFiles[4], DataFiles[5], DataFiles[6], DataFiles[7], DataFiles[8], DataFiles[9], DataFiles[10], DataFiles[11])
    plotTestsSolvedInstances(DataFiles,DataNames,DirResults + "xAttendedRealServiceTime.png")


def plotResultsTrivialValues2(simResultsDir, dataSetPartition):
    # # PLOTTING RESULTS
    DirResults = "SimulationResults/"+dataSetPartition+"/"+simResultsDir+"/"
    #
    DataFiles = [
                pd.read_csv(DirResults + "FCFS_N_R_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "FCFS_H_R_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "FCFS_N_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "FCFS_H_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_N_R_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_H_R_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_N_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_H_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_R_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_RC_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_H8_R_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_H8_RC_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv")
                 ]
    DataNames = ["FCFS(N-R)", "FCFS(H-R)", "FCFS(N-RC)", "FCFS(H-RC)", "SJF(N-R)", "SJF(H-R)", "SJF(N-RC)", "SJF(H-RC)",
                 "MIP(H-R)", "MIP(H-RC)", "MIP(H8-R)", "MIP(H8-RC)"]
    #OverHead = [0, 0, 0, 0, 0, 0, 0, 0]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    #printLatex2(DataFiles[0], DataFiles[1], DataFiles[2], DataFiles[3], DataFiles[4], DataFiles[5], DataFiles[6], DataFiles[7], DataFiles[8], DataFiles[9], DataFiles[10], DataFiles[11])
    plotTestsSolvedInstances(DataFiles, DataNames, DirResults + "xAttendedTrivialFeatures.png")


def plotResultsCheapValues2(simResultsDir, dataSetPartition):
    # # PLOTTING RESULTS
    DirResults = "SimulationResults/"+dataSetPartition+"/"+simResultsDir+"/"
    # #FeatureOverheadAll=SATfeatureOverhead("../dataSets/"+dataSetPartition+"/1.INDU(minisat)(regression)all_test.csv")
    # #FeatureOverheadTrivial = SATfeatureOverhead("../dataSets/" + dataSetPartition + "/2.INDU(minisat)(regression)trivial_test.csv")
    #FeatureOverheadCheap = SATfeatureOverhead("../dataSets/" + dataSetPartition + "/3.INDU(minisat)(regression)cheap_test.csv")
    #
    DataFiles = [pd.read_csv(DirResults + "FCFS_N_R_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "FCFS_H_R_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "FCFS_N_RC_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "FCFS_H_RC_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_N_R_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_H_R_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_N_RC_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "SJF_H_RC_PredictedServiceTime_CheapFeatures_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_R_PredictedServiceTime_CheapFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_RC_PredictedServiceTime_CheapFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_H8_R_PredictedServiceTime_CheapFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_H8_RC_PredictedServiceTime_CheapFeatures_G1_Simulation.csv")
                 ]
    #DataNames = ["FCFS(N)", "FCFS(H)", "SJF(N)", "SJF(H)", "MIP(H)"]
    DataNames = ["FCFS(N-R)", "FCFS(H-R)", "FCFS(N-RC)", "FCFS(H-RC)", "SJF(N-R)", "SJF(H-R)", "SJF(N-RC)", "SJF(H-RC)",
                 "MIP(H-R)", "MIP(H-RC)", "MIP(H8-R)", "MIP(H8-RC)"]
    #OverHead = [0, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    #printLatex2(DataFiles[0], DataFiles[1], DataFiles[2], DataFiles[3], DataFiles[4], DataFiles[5], DataFiles[6], DataFiles[7], DataFiles[8], DataFiles[9], DataFiles[10], DataFiles[11])
    plotTestsSolvedInstances(DataFiles, DataNames, DirResults + "xAttendedCheapFeatures.png")



#####################################################
#####################################################
#####################################################
#####################################################




def plot(data,Test):
    plotResultsRealValues2(data, Test)
    plotResultsTrivialValues2(data, Test)
    plotResultsCheapValues2(data, Test)


Test="30_70"
plot("xVM_1_WaitingTime_1_300_interArrival_300",Test)
# plot("xVM_1_WaitingTime_1_600_interArrival_300",Test)
# plot("xVM_1_WaitingTime_1_1000_interArrival_300",Test)
# plot("xVM_1_WaitingTime_1_1500_interArrival_3600",Test)
# plot("xVM_1_WaitingTime_1_3600_interArrival_3600",Test)
# plot("xVM_1_WaitingTime_1_500_interArrival_1000",Test)
# plot("xVM_1_WaitingTime_1000_3000_interArrival_1000",Test)
# plot("xVM_1_WaitingTime_1000_3000_interArrival_500",Test)
# plot("xVM_1_WaitingTime_1000_3000_interArrival_400",Test)
# plot("xVM_1_WaitingTime_1000_3000_interArrival_300",Test)

