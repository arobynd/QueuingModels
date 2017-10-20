#from SimulatorSources.plotResults import *
#from SimulatorSources.CalculateSATfeatureOverhead import *
import numpy as np
import pandas as pd
import os


def solvedInstances(Data):
    simData = pd.read_csv(Data)
    return simData["Solved"].sum()

directoryLocation="SimulationResults/30_70/"
directories = os.listdir(directoryLocation) #returns and array with the directories
experiments = [ "FCFS_H_R_RealServiceTime_Simulation.csv",
                "FCFS_H_R_PredictedServiceTime_CheapFeatures_Simulation.csv",
                "FCFS_H_R_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                "FCFS_H_RC_RealServiceTime_Simulation.csv",
                "FCFS_H_RC_PredictedServiceTime_CheapFeatures_Simulation.csv",
                "FCFS_H_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                "SJF_H_R_RealServiceTime_Simulation.csv",
                "SJF_H_R_PredictedServiceTime_CheapFeatures_Simulation.csv",
                "SJF_H_R_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                "SJF_H_RC_RealServiceTime_Simulation.csv",
                "SJF_H_RC_PredictedServiceTime_CheapFeatures_Simulation.csv",
                "SJF_H_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                "MIP_H_R_RealServiceTime_Q2_Simulation.csv",
                "MIP_H_R_PredictedServiceTime_CheapFeatures_Q2_Simulation.csv",
                "MIP_H_R_PredictedServiceTime_TrivialFeatures_Q2_Simulation.csv",
                "MIP_H_RC_RealServiceTime_Q2_Simulation.csv",
                "MIP_H_RC_PredictedServiceTime_CheapFeatures_Q2_Simulation.csv",
                "MIP_H_RC_PredictedServiceTime_TrivialFeatures_Q2_Simulation.csv"
                ]

# ##############GENERAL DATASET
# ##############
# data = []
# columns = ["TestID","VM", "Test", "MLmodel", "Features", "WTlower", "WTupper", "AvgRunT", "AvgRunTDiv", "InterArr", "Heuristic", "Solved"]
# testID = 0
# for dir in directories:
#     values = dir.split("_")
#     #print values
#     #print values[6]
#     testID = testID + 1
#     for test in experiments:
#         testName =  test.split("_")
#         #print testName
#         solvedInst = int(solvedInstances(directoryLocation+""+dir+"/"+test))
#         if testName[3]=="RealServiceTime":
#             data.append([testID, values[1], testName[0], testName[2], "Real",values[3],values[4],values[9],values[11],values[6],values[13],solvedInst])
#         else:
#             data.append([testID, values[1], testName[0], testName[2], testName[4], values[3], values[4], values[9], values[11], values[6],values[13], solvedInst])
#
# AllTestResults = pd.DataFrame(data, columns=columns)
# AllTestResults .to_csv("AllTestResults.csv")


##############GENERAL DATASET
##############
columns = ["TestID","VM", "Test", "MLmodel", "Features", "WTlower", "WTupper", "AvgRunT", "AvgRunTDiv", "InterArr", "Heuristic", "Solved"]
AllTestResults =  pd.DataFrame(columns=columns)
#print AllTestResults

testID = 0
for dir in directories:
    values = dir.split("_")
    #print values
    #print values[6]
    testID = testID + 1
    for test in experiments:
        testName =  test.split("_")
        #print testName
        solvedInst = int(solvedInstances(directoryLocation+""+dir+"/"+test))
        df2=""
        if testName[3]=="RealServiceTime":
            df2 = pd.DataFrame([[testID, values[1], testName[0], testName[2], "Real",values[3],values[4],values[9],values[11],values[6],values[13],solvedInst]], columns=columns)
        else:
            df2 = pd.DataFrame([[testID, values[1], testName[0], testName[2], testName[4], values[3], values[4], values[9], values[11], values[6],values[13], solvedInst]], columns=columns)

        AllTestResults=AllTestResults.append(df2, ignore_index=True)

#print AllTestResults
AllTestResults.to_csv("AllTestResults.csv")



##############DATASET TEST/HEURISTIC
##############

columns = ["TestID", "VM", "Features", "WTlower", "WTupper", "AvgRunT", "AvgRunTDiv", "InterArr", "Heuristic", "FCFS_R", "FCFS_RC", "SJF_R", "SJF_RC", "MIP_R", "MIP_RC"]
AllTestResults_TestHeuristic = pd.DataFrame(columns=columns)

for i in range(1, testID + 1):
    dataTest = AllTestResults[AllTestResults.TestID == i]
    #print dataTest
    #Create dataframes with default column values
    dfReal = pd.DataFrame([columns],columns=columns)
    dfTrivial =  pd.DataFrame([columns],columns=columns)
    dfCheap = pd.DataFrame([columns],columns=columns)

    for index, row in dataTest.iterrows():

        if row["Features"] == "Real":
            dfReal.loc[0].TestID = row["TestID"]
            dfReal.loc[0].VM = row["VM"]
            dfReal.loc[0].Features = row["Features"]
            dfReal.loc[0].WTlower = row["WTlower"]
            dfReal.loc[0].WTupper = row["WTupper"]
            dfReal.loc[0].AvgRunT = row["AvgRunT"]
            dfReal.loc[0].AvgRunTDiv = row["AvgRunTDiv"]
            dfReal.loc[0].InterArr = row["InterArr"]
            dfReal.loc[0].Heuristic = row["Heuristic"]
            TestName=row["Test"] + "_"+row["MLmodel"] #"FCFS_R", "FCFS_RC", "SJF_R", "SJF_RC", "MIP_R", "MIP_RC"
            dfReal.loc[0][TestName] = row["Solved"]
        elif row["Features"] == "CheapFeatures":
            dfCheap.loc[0].TestID = row["TestID"]
            dfCheap.loc[0].VM = row["VM"]
            dfCheap.loc[0].Features = row["Features"]
            dfCheap.loc[0].WTlower = row["WTlower"]
            dfCheap.loc[0].WTupper = row["WTupper"]
            dfCheap.loc[0].AvgRunT = row["AvgRunT"]
            dfCheap.loc[0].AvgRunTDiv = row["AvgRunTDiv"]
            dfCheap.loc[0].InterArr = row["InterArr"]
            dfCheap.loc[0].Heuristic = row["Heuristic"]
            TestName = row["Test"] + "_" + row["MLmodel"] #"FCFS_R", "FCFS_RC", "SJF_R", "SJF_RC", "MIP_R", "MIP_RC"
            dfCheap.loc[0][TestName] = row["Solved"]
        elif row["Features"] ==  "TrivialFeatures":
            dfTrivial.loc[0].TestID = row["TestID"]
            dfTrivial.loc[0].VM = row["VM"]
            dfTrivial.loc[0].Features = row["Features"]
            dfTrivial.loc[0].WTlower = row["WTlower"]
            dfTrivial.loc[0].WTupper = row["WTupper"]
            dfTrivial.loc[0].AvgRunT = row["AvgRunT"]
            dfTrivial.loc[0].AvgRunTDiv = row["AvgRunTDiv"]
            dfTrivial.loc[0].InterArr = row["InterArr"]
            dfTrivial.loc[0].Heuristic = row["Heuristic"]
            TestName = row["Test"] + "_" + row["MLmodel"] #"FCFS_R", "FCFS_RC", "SJF_R", "SJF_RC", "MIP_R", "MIP_RC"
            dfTrivial.loc[0][TestName] = row["Solved"]

    AllTestResults_TestHeuristic = AllTestResults_TestHeuristic.append(dfReal, ignore_index=True)
    AllTestResults_TestHeuristic = AllTestResults_TestHeuristic.append(dfCheap, ignore_index=True)
    AllTestResults_TestHeuristic = AllTestResults_TestHeuristic.append(dfTrivial, ignore_index=True)
#print AllTestResults_TestHeuristic
AllTestResults_TestHeuristic .to_csv("AllTestResults_TestHeuristic.csv")