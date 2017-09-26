from SimulatorSources.plotResults import *
from SimulatorSources.CalculateSATfeatureOverhead import *

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

def plotResultsRealValues(simResultsDir, dataSetPartition):
    DirResults = "SimulationResults/"+dataSetPartition+"/"+simResultsDir+"/"
    #
    DataFiles=[pd.read_csv(DirResults + "FCFS_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "FCFS(stops)_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF2_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF(stops)_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "SJF2(stops)_RealServiceTime_Simulation.csv"),
               pd.read_csv(DirResults + "MIP1_stops_RealServiceTime_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP2_stops_RealServiceTime_G1_Simulation.csv")
               ]
    DataNames= ["FCFS(N)","FCFS(H)","SJF(R-N)","SJF(C-R-N)","SJF(R-H)","SJF(C-R-H)","MIP(1)","MIP(2)"]
    OverHead = [0, 0, 0, 0, 0, 0, 0, 0]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    printLatex(DataFiles[0],DataFiles[1],DataFiles[2],DataFiles[3],DataFiles[4],DataFiles[5],DataFiles[6],DataFiles[7])


def plotResultsTrivialValues(simResultsDir, dataSetPartition):
    # # PLOTTING RESULTS
    DirResults = "SimulationResults/"+dataSetPartition+"/"+simResultsDir+"/"
    #
    DataFiles=[pd.read_csv(DirResults + "FCFS_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "FCFS(stops)_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF2_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF(stops)_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF2(stops)_PredictedServiceTime_TrivialFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "MIP1_stops_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP2_stops_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv")
               ]
    DataNames= ["FCFS(N)","FCFS(H)","SJF(R-N)","SJF(C-R-N)","SJF(R-H)","SJF(C-R-H)","MIP(1)","MIP(2)"]
    OverHead = [0, 0, 0, 0, 0, 0, 0, 0]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    printLatex(DataFiles[0],DataFiles[1],DataFiles[2],DataFiles[3],DataFiles[4],DataFiles[5],DataFiles[6],DataFiles[7])


def plotResultsCheapValues(simResultsDir, dataSetPartition):
    # # PLOTTING RESULTS
    DirResults = "SimulationResults/"+dataSetPartition+"/"+simResultsDir+"/"
    # #FeatureOverheadAll=SATfeatureOverhead("../dataSets/"+dataSetPartition+"/1.INDU(minisat)(regression)all_test.csv")
    # #FeatureOverheadTrivial = SATfeatureOverhead("../dataSets/" + dataSetPartition + "/2.INDU(minisat)(regression)trivial_test.csv")
    #FeatureOverheadCheap = SATfeatureOverhead("../dataSets/" + dataSetPartition + "/3.INDU(minisat)(regression)cheap_test.csv")
    #
    DataFiles=[pd.read_csv(DirResults + "FCFS_PredictedServiceTime_CheapFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "FCFS(stops)_PredictedServiceTime_CheapFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF_PredictedServiceTime_CheapFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF2_PredictedServiceTime_CheapFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF(stops)_PredictedServiceTime_CheapFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "SJF2(stops)_PredictedServiceTime_CheapFeatures_Simulation.csv"),
               pd.read_csv(DirResults + "MIP1_stops_PredictedServiceTime_CheapFeatures_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP2_stops_PredictedServiceTime_CheapFeatures_G1_Simulation.csv")
               ]
    DataNames= ["FCFS(N)","FCFS(H)","SJF(R-N)","SJF(C-R-N)","SJF(R-H)","SJF(C-R-H)","MIP(1)","MIP(2)"]
    #OverHead = [0, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    printLatex(DataFiles[0],DataFiles[1],DataFiles[2],DataFiles[3],DataFiles[4],DataFiles[5],DataFiles[6],DataFiles[7])


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
               pd.read_csv(DirResults + "MIP_H_H8_R_RealServiceTime_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP_H_RC_RealServiceTime_G1_Simulation.csv"),
               pd.read_csv(DirResults + "MIP_H_H8_RC_RealServiceTime_G1_Simulation.csv")
               ]
    #DataNames= ["FCFS(N)","FCFS(H)","SJF(N)","SJF(H)","MIP(H)"]
    #OverHead = [0, 0, 0, 0, 0, 0, 0, 0]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    printLatex2(DataFiles[0], DataFiles[1], DataFiles[2], DataFiles[3], DataFiles[4], DataFiles[5], DataFiles[6], DataFiles[7], DataFiles[8], DataFiles[9], DataFiles[10], DataFiles[11])


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
                pd.read_csv(DirResults + "MIP_H_H8_R_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_RC_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_H8_RC_PredictedServiceTime_TrivialFeatures_G1_Simulation.csv")
                 ]
    #DataNames = ["FCFS(N)", "FCFS(H)", "SJF(N)", "SJF(H)", "MIP(H)"]
    #OverHead = [0, 0, 0, 0, 0, 0, 0, 0]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    printLatex2(DataFiles[0], DataFiles[1], DataFiles[2], DataFiles[3], DataFiles[4], DataFiles[5], DataFiles[6], DataFiles[7], DataFiles[8], DataFiles[9], DataFiles[10], DataFiles[11])


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
                pd.read_csv(DirResults + "MIP_H_H8_R_PredictedServiceTime_CheapFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_RC_PredictedServiceTime_CheapFeatures_G1_Simulation.csv"),
                pd.read_csv(DirResults + "MIP_H_H8_RC_PredictedServiceTime_CheapFeatures_G1_Simulation.csv")
                 ]
    #DataNames = ["FCFS(N)", "FCFS(H)", "SJF(N)", "SJF(H)", "MIP(H)"]
    #OverHead = [0, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap, FeatureOverheadCheap]
    #plotTestsWaitingTime(DataFiles,DataNames,OverHead,DirResults+"plotWaitingTimeFromFiles.png")
    #plotTestsAttendedAndSolvedInstances(DataFiles,DataNames,DirResults + "plotAttendedAndSolvedInstancesFromFiles.png")
    printLatex2(DataFiles[0], DataFiles[1], DataFiles[2], DataFiles[3], DataFiles[4], DataFiles[5], DataFiles[6], DataFiles[7], DataFiles[8], DataFiles[9], DataFiles[10], DataFiles[11])



#####################################################
#####################################################
#####################################################
#####################################################


Test="30_70"


plotResultsRealValues2("xVM_1_WaitingTime_1_300_interArrival_300",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1_600_interArrival_300",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1_1000_interArrival_300",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1_1500_interArrival_3600",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1_3600_interArrival_3600",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1_500_interArrival_1000",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1000_3000_interArrival_1000",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1000_3000_interArrival_500",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1000_3000_interArrival_400",Test)
plotResultsRealValues2("xVM_1_WaitingTime_1000_3000_interArrival_300",Test)



print ""


plotResultsTrivialValues2("xVM_1_WaitingTime_1_300_interArrival_300",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1_600_interArrival_300",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1_1000_interArrival_300",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1_1500_interArrival_3600",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1_3600_interArrival_3600",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1_500_interArrival_1000",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1000_3000_interArrival_1000",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1000_3000_interArrival_500",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1000_3000_interArrival_400",Test)
plotResultsTrivialValues2("xVM_1_WaitingTime_1000_3000_interArrival_300",Test)



print ""

plotResultsCheapValues2("xVM_1_WaitingTime_1_300_interArrival_300",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1_600_interArrival_300",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1_1000_interArrival_300",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1_1500_interArrival_3600",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1_3600_interArrival_3600",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1_500_interArrival_1000",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1000_3000_interArrival_1000",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1000_3000_interArrival_500",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1000_3000_interArrival_400",Test)
plotResultsCheapValues2("xVM_1_WaitingTime_1000_3000_interArrival_300",Test)

