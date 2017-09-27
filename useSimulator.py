#import Queue
import time
import sys
import pandas as pd
import numpy as np
import os
#import random as rd


#from SimulatorSources.Instance import Instance
from SimulatorSources.VM import VM
#from Simulator import *
from SimulatorOfPolicies import *
from SimulatorOfMIP import *
from datetime import datetime


##############################
##############################


def createDefaultVMs(n):
    return [VM(i, -1, 0) for i in range(n)]

##############################
##############################

def prepareSimulationData(interArrivalTime, inputFileR, inputFileC, outputFile, Rseed, predictionType, instanceMaximumExpectedWaitingTime, instanceCapTime, onlySolvable=False):

    np.random.seed(Rseed)

    simData = pd.read_csv(inputFileR)
    simDataC = pd.read_csv(inputFileC)

    simData["interArrivalTime"] = np.random.choice(interArrivalTime, simData.shape[0])
    if instanceMaximumExpectedWaitingTime==0: #if instanceMaximumExpectedWaitingTime is disabled, then the maximum waiting time is the biggest number allowed
        simData["maximumWaitingTime"] = sys.maxsize
    elif type(instanceMaximumExpectedWaitingTime) is int:#if a particular value is given
        simData["maximumWaitingTime"]=instanceMaximumExpectedWaitingTime
    else:#if a range of possible values is given
        simData["maximumWaitingTime"] = np.random.choice(instanceMaximumExpectedWaitingTime, simData.shape[0])

    # We decided to round the real and predicted times using the ceil function
    simData["RealServiceTime"] = np.ceil(10 ** simData["actual"])
    simData["RealSolvable"] = simData["RealServiceTime"] < instanceCapTime

    if predictionType == "PredictedServiceTime":
        simData["PredictedServiceTime"] = np.ceil(10 ** simData["predicted"])
        simData["PredictedSolvable"] = (simDataC["predicted"].str.contains("yes"))
    else:
        simData["PredictedServiceTime"] = np.ceil(10 ** simData["actual"])
        simData["PredictedSolvable"] = simData["RealServiceTime"] < instanceCapTime

    del simData["inst#"]
    del simData["actual"]
    del simData["predicted"]
    del simData["error"]

    finalSimData=0
    if onlySolvable:
        finalSimData = simData[simData["RealServiceTime"] < instanceCapTime]
        #finalSimData = simData[(simData["RealServiceTime"] > 10) & (simData["RealServiceTime"] < 2500)]
        #finalSimData = simData[(simData["RealServiceTime"] > 10)]
    else:
        finalSimData =simData


    finalSimData=finalSimData.reset_index(drop=True)
    finalSimData.loc[0, "interArrivalTime"] = 1
    finalSimData.loc[0, "ArrivalTime"] = 1
    for i in range(1, finalSimData.shape[0]):
        finalSimData.loc[i, "ArrivalTime"] = finalSimData.loc[i - 1, "ArrivalTime"] + finalSimData.loc[i, "interArrivalTime"]
    finalSimData.to_csv(outputFile)

    return finalSimData


##############################
##############################

# def convertValuesToCSV(simulationData, column, startInstance, endInstance):
#     s = str(int(simulationData.loc[startInstance, column]))
#     for i in range(startInstance+1, endInstance+1):
#          s = (s + "," + str(int(simulationData.loc[i, column])))
#     return s
#
#
# ##############################
# ##############################
#
# def createEqualMaximumExpectedWaitingTime(value, n):
#     s = str(int(value))
#     for i in range(1, n):
#         s = (s + "," + str(value))
#     return s


##############################
##############################


def ExecutePolicySimulations(SimData, SimDataAll, SimDataCheap, SimDataTrivial, dataSetPartition="10_90", simulationResultsDir="", virtualMachines=1,  instanceCapTime=3598, stopWhenQueue=2):

    directory = "SimulationResults/"+dataSetPartition+"/"+simulationResultsDir
    if not os.path.exists(directory):
        os.makedirs(directory)


    #########################################
    # NAIVE STRATEGY SIMULATIONS -- Using real service time and regresion models
    #########################################
    print  "\nExecuting test FCFS_N_R_RealServiceTime_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimData,
                              outputFile=directory+"/FCFS_N_R_RealServiceTime_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime)

    print  "\nExecuting test FCFS_N_R_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimDataAll,
                              outputFile=directory + "/FCFS_N_R_PredictedServiceTime_AllFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime)

    print  "\nExecuting test FCFS_N_R_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimDataTrivial,
                              outputFile=directory + "/FCFS_N_R_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime)

    print  "\nExecuting test FCFS_N_R_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimDataCheap,
                              outputFile=directory + "/FCFS_N_R_PredictedServiceTime_CheapFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_R_RealServiceTime_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimData,
                              outputFile=directory + "/SJF_N_R_RealServiceTime_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_R_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimDataAll,
                              outputFile=directory + "/SJF_N_R_PredictedServiceTime_AllFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_R_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimDataTrivial,
                              outputFile=directory + "/SJF_N_R_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_R_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression( inputData=SimDataCheap,
                              outputFile=directory + "/SJF_N_R_PredictedServiceTime_CheapFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime)

    #########################################
    # NAIVE STRATEGY SIMULATIONS -- Using real service time and regresion/classification models
    #########################################

    print  "\nExecuting test FCFS_N_RC_RealServiceTime_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimData,
                             outputFile=directory + "/FCFS_N_RC_RealServiceTime_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime)

    print  "\nExecuting test FCFS_N_RC_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimDataAll,
                             outputFile=directory + "/FCFS_N_RC_PredictedServiceTime_AllFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime)

    print  "\nExecuting test FCFS_N_RC_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimDataTrivial,
                             outputFile=directory + "/FCFS_N_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime)

    print  "\nExecuting test FCFS_N_RC_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimDataCheap,
                             outputFile=directory + "/FCFS_N_RC_PredictedServiceTime_CheapFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_RC_RealServiceTime_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimData,
                             outputFile=directory + "/SJF_N_RC_RealServiceTime_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_RC_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimDataAll,
                             outputFile=directory + "/SJF_N_RC_PredictedServiceTime_AllFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_RC_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimDataTrivial,
                             outputFile=directory + "/SJF_N_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime)

    print  "\nExecuting test SJF_N_RC_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData=SimDataCheap,
                             outputFile=directory + "/SJF_N_RC_PredictedServiceTime_CheapFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime)


    #########################################
    # HEURISTIC STRATEGY SIMULATIONS -- Using real service time and regresion models
    #########################################
    print  "\nExecuting test FCFS_H_R_RealServiceTime_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimData,
                              outputFile=directory+"/FCFS_H_R_RealServiceTime_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test FCFS_H_R_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataAll,
                              outputFile=directory + "/FCFS_H_R_PredictedServiceTime_AllFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test FCFS_H_R_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataTrivial,
                              outputFile=directory + "/FCFS_H_R_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test FCFS_H_R_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataCheap,
                              outputFile=directory + "/FCFS_H_R_PredictedServiceTime_CheapFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="FCFS",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_R_RealServiceTime_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimData,
                              outputFile=directory + "/SJF_H_R_RealServiceTime_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_R_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataAll,
                              outputFile=directory + "/SJF_H_R_PredictedServiceTime_AllFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_R_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataTrivial,
                              outputFile=directory + "/SJF_H_R_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_R_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataCheap,
                              outputFile=directory + "/SJF_H_R_PredictedServiceTime_CheapFeatures_Simulation.csv",
                              VMs=createDefaultVMs(virtualMachines),
                              schedulingPolicy="SJF",
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)


    #########################################
    # HEURISTIC STRATEGY SIMULATIONS -- Using real service time and regresion/classification models
    #########################################
    print  "\nExecuting test FCFS_H_RC_RealServiceTime_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimData,
                             outputFile=directory + "/FCFS_H_RC_RealServiceTime_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test FCFS_H_RC_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataAll,
                             outputFile=directory + "/FCFS_H_RC_PredictedServiceTime_AllFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test FCFS_H_RC_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataTrivial,
                             outputFile=directory + "/FCFS_H_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test FCFS_H_RC_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataCheap,
                             outputFile=directory + "/FCFS_H_RC_PredictedServiceTime_CheapFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="FCFS",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_RC_RealServiceTime_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimData,
                             outputFile=directory + "/SJF_H_RC_RealServiceTime_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_RC_PredictedServiceTime_AllFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataAll,
                             outputFile=directory + "/SJF_H_RC_PredictedServiceTime_AllFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_RC_PredictedServiceTime_TrivialFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataTrivial,
                             outputFile=directory + "/SJF_H_RC_PredictedServiceTime_TrivialFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

    print  "\nExecuting test SJF_H_RC_PredictedServiceTime_CheapFeatures_Simulation"
    simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataCheap,
                             outputFile=directory + "/SJF_H_RC_PredictedServiceTime_CheapFeatures_Simulation.csv",
                             VMs=createDefaultVMs(virtualMachines),
                             schedulingPolicy="SJF",
                             instanceCapTime=instanceCapTime,
                             stopWhenQueue=stopWhenQueue)

##############################
##############################


def ExecuteMIPSimulations(MIPnumber,SimData, SimDataAll, SimDataCheap, SimDataTrivial, dataSetPartition="10_90", simulationResultsDir="", virtualMachines=1,  instanceCapTime=0, instanceGroupSize=[40], BigM=False, searchTime = 60, GAPsize = 0.1,  stopWhenQueue=2, dequeueWhenNotScheduledMIP=0):

    directory = "SimulationResults/" + dataSetPartition + "/" + simulationResultsDir
    if not os.path.exists(directory):
        os.makedirs(directory)

    H2=""
    if(dequeueWhenNotScheduledMIP):
        H2="_H"+str(dequeueWhenNotScheduledMIP)


    for gSize in instanceGroupSize:

        #########################################
        # HEURISTIC STRATEGY SIMULATIONS -- (Single Machine) Using model1 with regression and model 2 with regression/classification
        #########################################
        if (virtualMachines==1):

            if (MIPnumber==0 or MIPnumber==1):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimData,
                                                           outputFile=directory + "/MIP_H"+H2+"_R_RealServiceTime_G" + str(gSize) + "_Simulation.csv",
                                                           VMs=createDefaultVMs(virtualMachines),
                                                           schedulingPolicy="MIP",
                                                           instanceCapTime=instanceCapTime,
                                                           groupSize=gSize,
                                                           searchTime=searchTime,
                                                           GAPsize=GAPsize,
                                                           model="model1",
                                                           stopWhenQueue=stopWhenQueue,
                                                           dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)
            if (MIPnumber==0 or MIPnumber == 2):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimData,
                                                           outputFile=directory + "/MIP_H"+H2+"_RC_RealServiceTime_G" + str(gSize) + "_Simulation.csv",
                                                           VMs=createDefaultVMs(virtualMachines),
                                                           schedulingPolicy="MIP",
                                                           instanceCapTime=instanceCapTime,
                                                           groupSize=gSize,
                                                           searchTime=searchTime,
                                                           GAPsize=GAPsize,
                                                           model="model2",
                                                           stopWhenQueue=stopWhenQueue,
                                                           dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

                ###
            if (MIPnumber==0 or MIPnumber == 3):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataCheap,
                                                           outputFile=directory + "/MIP_H"+H2+"_R_PredictedServiceTime_CheapFeatures_G" + str(gSize) + "_Simulation.csv",
                                                           VMs=createDefaultVMs(virtualMachines),
                                                           schedulingPolicy="MIP",
                                                           instanceCapTime=instanceCapTime,
                                                           groupSize=gSize,
                                                           searchTime=searchTime,
                                                           GAPsize=GAPsize,
                                                           model="model1",
                                                           stopWhenQueue=stopWhenQueue,
                                                           dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

            if (MIPnumber==0 or MIPnumber == 4):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataCheap,
                                                           outputFile=directory + "/MIP_H"+H2+"_RC_PredictedServiceTime_CheapFeatures_G" + str(gSize) + "_Simulation.csv",
                                                           VMs=createDefaultVMs(virtualMachines),
                                                           schedulingPolicy="MIP",
                                                           instanceCapTime=instanceCapTime,
                                                           groupSize=gSize,
                                                           searchTime=searchTime,
                                                           GAPsize=GAPsize,
                                                           model="model2",
                                                           stopWhenQueue=stopWhenQueue,
                                                           dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

                ###
            if (MIPnumber==0 or MIPnumber == 5):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataTrivial,
                                                            outputFile=directory + "/MIP_H"+H2+"_R_PredictedServiceTime_TrivialFeatures_G" + str(gSize) + "_Simulation.csv",
                                                            VMs=createDefaultVMs(virtualMachines),
                                                            schedulingPolicy="MIP",
                                                            instanceCapTime=instanceCapTime,
                                                            groupSize=gSize,
                                                            searchTime=searchTime,
                                                            GAPsize=GAPsize,
                                                            model="model1",
                                                            stopWhenQueue=stopWhenQueue,
                                                            dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

            if (MIPnumber==0 or MIPnumber == 6):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification( inputData=SimDataTrivial,
                                                                            outputFile=directory + "/MIP_H"+H2+"_RC_PredictedServiceTime_TrivialFeatures_G" + str(gSize) + "_Simulation.csv",
                                                                            VMs=createDefaultVMs(virtualMachines),
                                                                            schedulingPolicy="MIP",
                                                                            instanceCapTime=instanceCapTime,
                                                                            groupSize=gSize,
                                                                            searchTime=searchTime,
                                                                            GAPsize=GAPsize,
                                                                            model="model2",
                                                                            stopWhenQueue=stopWhenQueue,
                                                                            dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

        if (virtualMachines > 1):

            if (MIPnumber == 0 or MIPnumber == 1):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimData,
                                                                         outputFile=directory + "/MIP_H" + H2 + "_R_RealServiceTime_G" + str(
                                                                             gSize) + "_Simulation.csv",
                                                                         VMs=createDefaultVMs(virtualMachines),
                                                                         schedulingPolicy="MIP",
                                                                         instanceCapTime=instanceCapTime,
                                                                         groupSize=gSize,
                                                                         searchTime=searchTime,
                                                                         GAPsize=GAPsize,
                                                                         model="model3",
                                                                         stopWhenQueue=stopWhenQueue,
                                                                         dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)
            if (MIPnumber == 0 or MIPnumber == 2):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimData,
                                                                                        outputFile=directory + "/MIP_H" + H2 + "_RC_RealServiceTime_G" + str(
                                                                                            gSize) + "_Simulation.csv",
                                                                                        VMs=createDefaultVMs(
                                                                                            virtualMachines),
                                                                                        schedulingPolicy="MIP",
                                                                                        instanceCapTime=instanceCapTime,
                                                                                        groupSize=gSize,
                                                                                        searchTime=searchTime,
                                                                                        GAPsize=GAPsize,
                                                                                        model="model4",
                                                                                        stopWhenQueue=stopWhenQueue,
                                                                                        dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

                ###
            if (MIPnumber == 0 or MIPnumber == 3):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataCheap,
                                                                         outputFile=directory + "/MIP_H" + H2 + "_R_PredictedServiceTime_CheapFeatures_G" + str(
                                                                             gSize) + "_Simulation.csv",
                                                                         VMs=createDefaultVMs(virtualMachines),
                                                                         schedulingPolicy="MIP",
                                                                         instanceCapTime=instanceCapTime,
                                                                         groupSize=gSize,
                                                                         searchTime=searchTime,
                                                                         GAPsize=GAPsize,
                                                                         model="model3",
                                                                         stopWhenQueue=stopWhenQueue,
                                                                         dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

            if (MIPnumber == 0 or MIPnumber == 4):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData=SimDataCheap,
                                                                                        outputFile=directory + "/MIP_H" + H2 + "_RC_PredictedServiceTime_CheapFeatures_G" + str(
                                                                                            gSize) + "_Simulation.csv",
                                                                                        VMs=createDefaultVMs(
                                                                                            virtualMachines),
                                                                                        schedulingPolicy="MIP",
                                                                                        instanceCapTime=instanceCapTime,
                                                                                        groupSize=gSize,
                                                                                        searchTime=searchTime,
                                                                                        GAPsize=GAPsize,
                                                                                        model="model4",
                                                                                        stopWhenQueue=stopWhenQueue,
                                                                                        dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

                ###
            if (MIPnumber == 0 or MIPnumber == 5):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData=SimDataTrivial,
                                                                         outputFile=directory + "/MIP_H" + H2 + "_R_PredictedServiceTime_TrivialFeatures_G" + str(
                                                                             gSize) + "_Simulation.csv",
                                                                         VMs=createDefaultVMs(virtualMachines),
                                                                         schedulingPolicy="MIP",
                                                                         instanceCapTime=instanceCapTime,
                                                                         groupSize=gSize,
                                                                         searchTime=searchTime,
                                                                         GAPsize=GAPsize,
                                                                         model="model3",
                                                                         stopWhenQueue=stopWhenQueue,
                                                                         dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)

            if (MIPnumber == 0 or MIPnumber == 6):
                MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification(
                                                                        inputData=SimDataTrivial,
                                                                        outputFile=directory + "/MIP_H" + H2 + "_RC_PredictedServiceTime_TrivialFeatures_G" + str(
                                                                            gSize) + "_Simulation.csv",
                                                                        VMs=createDefaultVMs(virtualMachines),
                                                                        schedulingPolicy="MIP",
                                                                        instanceCapTime=instanceCapTime,
                                                                        groupSize=gSize,
                                                                        searchTime=searchTime,
                                                                        GAPsize=GAPsize,
                                                                        model="model4",
                                                                        stopWhenQueue=stopWhenQueue,
                                                                        dequeueWhenNotScheduledMIP=dequeueWhenNotScheduledMIP)


############################################################
############################################################
############################################################
############################################################
############################################################





def Test(testType,MIPnumber, simResultsDir="Simulation", dataSetPartition="10_90", instanceMaximumExpectedWaitingTime=0, instanceGroupSize=[40],
         virtualMachines=1, maxInterArrival=3600, onlySolvable=False, stopWhenQueue=2,
         PredictionsInputFileR="", PredictionsInputFileAllR="", PredictionsInputFileTrivialR="",
         PredictionsInputFileCheapR="", PredictionsInputFileC="", PredictionsInputFileAllC="",
         PredictionsInputFileTrivialC="", PredictionsInputFileCheapC="",
         seed=12345, instanceCapTime=3598, searchTime=60, GAPsize=0):



    directory = "SimulationResults/"+dataSetPartition+"/"+simResultsDir
    if not os.path.exists(directory):
        os.makedirs(directory)

    print "Creating simulation data "

    SimData = directory + "/Simulation_Data_RealServiceTime.csv"
    SimDataAll = directory + "/Simulation_Data_PredictedServiceTime_AllFeatures.csv"
    SimDataTrivial = directory + "/Simulation_Data_PredictedServiceTime_TrivialFeatures.csv"
    SimDataCheap = directory + "/Simulation_Data_PredictedServiceTime_CheapFeatures.csv"
    prepareSimulationData(interArrivalTime=range(1, maxInterArrival),
                          inputFileR=PredictionsInputFileR,
                          inputFileC=PredictionsInputFileC,
                          outputFile=SimData,
                          Rseed=seed,
                          predictionType="RealServiceTime",
                          instanceMaximumExpectedWaitingTime=instanceMaximumExpectedWaitingTime,
                          instanceCapTime=instanceCapTime,
                          onlySolvable=onlySolvable)

    prepareSimulationData(interArrivalTime=range(1, maxInterArrival),
                          inputFileR=PredictionsInputFileAllR,
                          inputFileC=PredictionsInputFileAllC,
                          outputFile=SimDataAll,
                          Rseed=seed,
                          predictionType="PredictedServiceTime",
                          instanceMaximumExpectedWaitingTime=instanceMaximumExpectedWaitingTime,
                          instanceCapTime=instanceCapTime,
                          onlySolvable=onlySolvable)

    prepareSimulationData(interArrivalTime=range(1, maxInterArrival),
                          inputFileR=PredictionsInputFileTrivialR,
                          inputFileC=PredictionsInputFileTrivialC,
                          outputFile=SimDataTrivial,
                          Rseed=seed,
                          predictionType="PredictedServiceTime",
                          instanceMaximumExpectedWaitingTime=instanceMaximumExpectedWaitingTime,
                          instanceCapTime=instanceCapTime,
                          onlySolvable=onlySolvable)

    prepareSimulationData(interArrivalTime=range(1, maxInterArrival),
                          inputFileR=PredictionsInputFileCheapR,
                          inputFileC=PredictionsInputFileCheapC,
                          outputFile=SimDataCheap,
                          Rseed=seed,
                          predictionType="PredictedServiceTime",
                          instanceMaximumExpectedWaitingTime=instanceMaximumExpectedWaitingTime,
                          instanceCapTime=instanceCapTime,
                          onlySolvable=onlySolvable)

    if(testType=="ALLTESTS" or testType=="POLICY"):
        ExecutePolicySimulations(SimData = SimData ,
                              SimDataAll = SimDataAll ,
                              SimDataCheap = SimDataCheap ,
                              SimDataTrivial = SimDataTrivial,
                              dataSetPartition=dataSetPartition,
                              simulationResultsDir=simResultsDir,
                              virtualMachines=virtualMachines,
                              instanceCapTime=instanceCapTime,
                              stopWhenQueue=stopWhenQueue)

    if (testType == "ALLTESTS" or testType == "MIP"):
        ExecuteMIPSimulations(MIPnumber,
                                      SimData = SimData ,
                                      SimDataAll = SimDataAll ,
                                      SimDataCheap = SimDataCheap ,
                                      SimDataTrivial = SimDataTrivial,
                                      dataSetPartition=dataSetPartition,
                                      simulationResultsDir=simResultsDir,
                                      virtualMachines=virtualMachines,
                                      instanceCapTime=instanceCapTime,
                                      instanceGroupSize=instanceGroupSize,
                                      BigM=False,
                                      searchTime=searchTime,
                                      GAPsize=GAPsize,
                                      stopWhenQueue=stopWhenQueue,
                                      dequeueWhenNotScheduledMIP=0)






####################
Partition=""
instanceType=""
solver=""
testNumber=""
testType  = ""
MIPnumber = ""
virtualMachine = ""

if(len(sys.argv)==1):
    Partition = "30_70"
    instanceType = "INDU"
    solver = "minisat"
    testNumber = 1 #0 - all tests
    testType = "ALLTESTS" #ALLTESTS, POLICY or MIP
    MIPnumber = 3 #0 - all MIP tests
    virtualMachine = 1
else:
    print "parametros", sys.argv[1]
    Partition = str(sys.argv[1])
    instanceType = str(sys.argv[2])
    solver = str(sys.argv[3])
    testNumber = int(sys.argv[4]) #Number of test, so far 1 to 10
    testType = str(sys.argv[5]) #POLICY or MIP
    MIPnumber = int(sys.argv[6]) #If the testType is MIP, then a number of test must be provided...so far 1 to 6
    virtualMachine = int(sys.argv[7])



####################
if (testNumber==1 or testNumber==0):
    waitingL=1
    waitingU= int(300 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)




####################
if (testNumber==2 or testNumber==0):
    waitingL=1
    waitingU= int(500 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)


####################
if (testNumber==3 or testNumber==0):
    waitingL=1
    waitingU= int(700 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)




####################
if (testNumber==4 or testNumber==0):
    waitingL=1
    waitingU= int(1000 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)

####################
if (testNumber==5 or testNumber==0):
    waitingL=1
    waitingU= int(1500 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)



####################
if (testNumber==6 or testNumber==0):
    waitingL=1
    waitingU= int(3000 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)



####################
if (testNumber==7 or testNumber==0):
    waitingL= int(1000 / virtualMachine)
    waitingU= int(2000 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)



####################
if (testNumber==8 or testNumber==0):
    waitingL= int(1000 / virtualMachine)
    waitingU= int(3000 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)



####################
if (testNumber==9 or testNumber==0):
    waitingL= int(2000 / virtualMachine)
    waitingU= int(3000 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)



####################
if (testNumber==10 or testNumber==0):
    waitingL= int(2000 / virtualMachine)
    waitingU= int(4000 / virtualMachine)
    interMax= int(130 / virtualMachine)
    onlySolvableInstances=False
    PredictionsInputFileR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileAllR = "../myTrainedModelsAndResults/" + Partition + "/1." + instanceType + "("+solver+")(regression)(predictions)all.csv"
    PredictionsInputFileTrivialR = "../myTrainedModelsAndResults/" + Partition + "/2." + instanceType + "("+solver+")(regression)(predictions)trivial.csv"
    PredictionsInputFileCheapR = "../myTrainedModelsAndResults/" + Partition + "/3." + instanceType + "("+solver+")(regression)(predictions)cheap.csv"
    PredictionsInputFileC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileAllC = "../myTrainedModelsAndResults/" + Partition + "/4." + instanceType + "("+solver+")(classification)(predictions)all.csv"
    PredictionsInputFileTrivialC = "../myTrainedModelsAndResults/" + Partition + "/5." + instanceType + "("+solver+")(classification)(predictions)trivial.csv"
    PredictionsInputFileCheapC = "../myTrainedModelsAndResults/" + Partition + "/6." + instanceType + "("+solver+")(classification)(predictions)cheap.csv"

    Test(testType,MIPnumber,
        simResultsDir="xVM_"+str(virtualMachine)+"_WaitingTime_"+str(waitingL)+"_"+str(waitingU)+"_interArrival_"+str(interMax)+"_"+datetime.now().strftime('#%Y_%m_%d_%H_%M_%S'),
        dataSetPartition=Partition,
        instanceMaximumExpectedWaitingTime=range(waitingL,waitingU),
        instanceGroupSize=[1],
        virtualMachines=virtualMachine,
        maxInterArrival=int(interMax),
        onlySolvable=onlySolvableInstances,
        stopWhenQueue=2,
        PredictionsInputFileR=PredictionsInputFileR,
        PredictionsInputFileAllR = PredictionsInputFileAllR,
        PredictionsInputFileTrivialR = PredictionsInputFileTrivialR,
        PredictionsInputFileCheapR = PredictionsInputFileCheapR,
        PredictionsInputFileC = PredictionsInputFileC,
        PredictionsInputFileAllC = PredictionsInputFileAllC,
        PredictionsInputFileTrivialC = PredictionsInputFileTrivialC,
        PredictionsInputFileCheapC = PredictionsInputFileCheapC,
        seed=12345,
        instanceCapTime=3598,
        searchTime = 1,
        GAPsize = 0.3)