import Queue
from SimulatorSources.Instance import Instance
from SimulatorCommon import *
import os
import pandas as pd
import numpy as np




##############################
##############################

def HeuristicEvaluateContinueToExecute(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, heuristicH, useClassification = False):
    vmID = getVMwithSmallestEndTime(VMs)
    auxQueue = Queue.PriorityQueue()

    counter = 0
    while not queue.empty():
        instance = queue.get()
        auxQueue.put(instance)
        if VMs[vmID].nextEndTime > (instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1

    queue = auxQueue
    if counter>= heuristicH:
        OldInstanceID = VMs[vmID].processingInstanceID
        # If the instance is being attended, then it can be stopped, otherwise the end time could be smaller than the start time
        if (simData.loc[OldInstanceID, "TimeServiceEnds"] != simData.loc[OldInstanceID, "TimeServiceBegins"]) and (ArrivingInstanceTime >= simData.loc[OldInstanceID, "TimeServiceBegins"]):
            simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
            simData.loc[OldInstanceID, "Attended"] = 1
            simData.loc[OldInstanceID, "Solved"] = 0
            simData.loc[OldInstanceID, "Stopped"] = 1
            simData.loc[OldInstanceID, "TimeInstanceInSystem"] = ArrivingInstanceTime - simData.loc[OldInstanceID, "ArrivalTime"]
            VMs[vmID].nextEndTime = ArrivingInstanceTime

        processing = False
        while (not queue.empty()) and processing == False:
            QueuedInstance = queue.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            PredictedSolvable = True
            if useClassification == True:
                PredictedSolvable = (QueuedInstance.PredictedSolvable != 0)

            if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"] and PredictedSolvable:
                processing = True
                simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + QueuedInstance.RealServiceTime
                simData.loc[QueuedInstance.ID, "Attended"] = 1
                if (QueuedInstance.RealServiceTime < instanceCapTime):
                    simData.loc[QueuedInstance.ID, "Solved"] = 1
                else:
                    simData.loc[QueuedInstance.ID, "Solved"] = 0
            else:
                simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = simData.loc[QueuedInstance.ID, "TimeServiceBegins"]  # No execution time is given
                simData.loc[QueuedInstance.ID, "Attended"] = 0
                simData.loc[QueuedInstance.ID, "Solved"] = 0

            simData.loc[QueuedInstance.ID, "TimeInstanceInSystem"] = simData.loc[QueuedInstance.ID, "TimeServiceEnds"] - simData.loc[QueuedInstance.ID, "ArrivalTime"]
            VMs[vmID].processingInstanceID = QueuedInstance.ID
            VMs[vmID].nextEndTime = simData.loc[QueuedInstance.ID, "TimeServiceEnds"]

    return queue



##############################
##############################


def simulateInstanceArrivals_NaiveStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["QueuedInstances"] = 0
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:

            ###########
            #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():
                QueuedInstance = q.get()
                VMs=beginToProcessInstance_R(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)
                vmID = getVMwithSmallestEndTime(VMs)

        #If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it because the system is idle

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
        else:
            VMs=beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)

    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            VMs = beginToProcessInstance_R(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)

    sim = simData.sort_values(by=["TimeServiceBegins", "TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)

    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim

##############################
##############################




def simulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["QueuedInstances"] = 0
    for index, row in simData.iterrows():

        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance

        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            ###########
            #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():
                QueuedInstance = q.get()
                VMs=beginToProcessInstance_R_C(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)
                vmID = getVMwithSmallestEndTime(VMs)

        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it only if predicted solvable

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
        elif (ArrivingInstance.PredictedSolvable != 0):
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)
        else:
            VMs = doNotProcessInstance(VMs, vmID, ArrivingInstance, simData)

    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            VMs = beginToProcessInstance_R_C(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)

    sim = simData.sort_values(by=["TimeServiceBegins", "TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)

    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim




##############################
##############################


def simulateInstanceArrivals_HeuristicStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, heuristicH=2):
    simData = pd.read_csv(inputData, index_col=0)
    simData["Stopped"] = 0
    simData["QueuedInstances"] = 0
    q = Queue.PriorityQueue()
    for index, row in simData.iterrows():

        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy)  # Create the instance

        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:

            ###########
            #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():
                QueuedInstance = q.get()
                VMs=beginToProcessInstance_R(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)
                vmID = getVMwithSmallestEndTime(VMs)

        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it because the system is idle

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            if heuristicH > 0:
                q = HeuristicEvaluateContinueToExecute(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH, useClassification=False)
        else:
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)

    # Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            VMs = beginToProcessInstance_R(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)

    sim = simData.sort_values(by=["TimeServiceBegins", "TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)

    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim


##############################
##############################
def simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, heuristicH=2):
    simData = pd.read_csv(inputData, index_col=0)
    simData["Stopped"] = 0
    simData["QueuedInstances"] = 0
    q = Queue.PriorityQueue()
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:

            ###########
            #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():
                QueuedInstance = q.get()
                VMs=beginToProcessInstance_R_C(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)
                vmID = getVMwithSmallestEndTime(VMs)

        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it only if predicted solvable

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            if heuristicH > 0:
                q = HeuristicEvaluateContinueToExecute(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH, useClassification=True)
        elif (ArrivingInstance.PredictedSolvable != 0):
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)
        else:
            VMs = doNotProcessInstance(VMs, vmID, ArrivingInstance, simData)

    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        #q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            VMs = beginToProcessInstance_R_C(q, QueuedInstance, simData, VMs, vmID, instanceCapTime)

    sim = simData.sort_values(by=["TimeServiceBegins", "TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)

    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim
##############################
##############################