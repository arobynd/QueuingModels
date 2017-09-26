import Queue
from SimulatorSources.Instance import Instance
from SimulatorCommon import *
import os


import pandas as pd
import numpy as np




##############################
##############################

def HeuristicEvaluateContinueToExecute(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, stopWhenQueue, useClassification = False):
    vmID = getVMwithSmallestEndTime(VMs)
    auxQueue = Queue.PriorityQueue()

    counter = 0
    while not queue.empty():
        instance = queue.get()
        auxQueue.put(instance)
        if VMs[vmID].nextEndTime > (instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1

    queue = auxQueue
    if counter>= stopWhenQueue:
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
            q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():

                QueuedInstance = q.get()
                simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
                simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
                simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                simData.loc[QueuedInstance.ID, "VM"] = vmID

                if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]:
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
                vmID = getVMwithSmallestEndTime(VMs)

        #If the queue is not empty after simulation, then put it in queue. Otherwise attend it

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
        else:
            VMs[vmID].processingInstanceID = ArrivingInstance.ID
            simData.loc[ArrivingInstance.ID, "TimeServiceBegins"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "TimeServiceEnds"] = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "WaitingTimeInQueue"] = 0
            simData.loc[ArrivingInstance.ID, "TimeInstanceInSystem"] = ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "IdleTimeOfServer"] = ArrivingInstance.ArrivalTime - VMs[vmID].nextEndTime
            simData.loc[ArrivingInstance.ID, "VM"] = VMs[vmID].ID
            simData.loc[ArrivingInstance.ID, "Attended"] = 1
            VMs[vmID].nextEndTime = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime

            if (ArrivingInstance.RealServiceTime < instanceCapTime):
                simData.loc[ArrivingInstance.ID, "Solved"] = 1
            else:
                simData.loc[ArrivingInstance.ID, "Solved"] = 0

    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]:
                simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + QueuedInstance.RealServiceTime
                simData.loc[QueuedInstance.ID, "Attended"] = 1
                if (QueuedInstance.RealServiceTime < instanceCapTime):
                    simData.loc[QueuedInstance.ID, "Solved"] = 1
                else:
                    simData.loc[QueuedInstance.ID, "Solved"] = 0
            else:
                simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = simData.loc[
                    QueuedInstance.ID, "TimeServiceBegins"]  # No execution time is given
                simData.loc[QueuedInstance.ID, "Attended"] = 0
                simData.loc[QueuedInstance.ID, "Solved"] = 0

            simData.loc[QueuedInstance.ID, "TimeInstanceInSystem"] = simData.loc[QueuedInstance.ID, "TimeServiceEnds"] - simData.loc[QueuedInstance.ID, "ArrivalTime"]
            VMs[vmID].processingInstanceID = QueuedInstance.ID
            VMs[vmID].nextEndTime = simData.loc[QueuedInstance.ID, "TimeServiceEnds"]

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
            q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():

                QueuedInstance = q.get()
                simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
                simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
                simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                simData.loc[QueuedInstance.ID, "VM"] = vmID

                if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"] and (QueuedInstance.PredictedSolvable != 0):
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
                vmID = getVMwithSmallestEndTime(VMs)

        #If the queue is not empty after simulation, then put it in queue. Otherwise attend it

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
        elif (ArrivingInstance.PredictedSolvable != 0):
            VMs[vmID].processingInstanceID = ArrivingInstance.ID
            simData.loc[ArrivingInstance.ID, "TimeServiceBegins"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "TimeServiceEnds"] = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "WaitingTimeInQueue"] = 0
            simData.loc[ArrivingInstance.ID, "TimeInstanceInSystem"] = ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "IdleTimeOfServer"] = ArrivingInstance.ArrivalTime - VMs[vmID].nextEndTime
            simData.loc[ArrivingInstance.ID, "VM"] = VMs[vmID].ID
            simData.loc[ArrivingInstance.ID, "Attended"] = 1
            VMs[vmID].nextEndTime = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime

            if (ArrivingInstance.RealServiceTime < instanceCapTime):
                simData.loc[ArrivingInstance.ID, "Solved"] = 1
            else:
                simData.loc[ArrivingInstance.ID, "Solved"] = 0
        else:
            VMs[vmID].processingInstanceID = ArrivingInstance.ID
            simData.loc[ArrivingInstance.ID, "TimeServiceBegins"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "TimeServiceEnds"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "WaitingTimeInQueue"] = 0
            simData.loc[ArrivingInstance.ID, "TimeInstanceInSystem"] = 1
            simData.loc[ArrivingInstance.ID, "IdleTimeOfServer"] = ArrivingInstance.ArrivalTime - VMs[vmID].nextEndTime
            simData.loc[ArrivingInstance.ID, "VM"] = VMs[vmID].ID
            simData.loc[ArrivingInstance.ID, "Attended"] = 0
            VMs[vmID].nextEndTime = simData.loc[ArrivingInstance.ID, "TimeServiceEnds"]
            simData.loc[ArrivingInstance.ID, "Solved"] = 0

    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"] and (QueuedInstance.PredictedSolvable != 0):
                simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + QueuedInstance.RealServiceTime
                simData.loc[QueuedInstance.ID, "Attended"] = 1
                if (QueuedInstance.RealServiceTime < instanceCapTime):
                    simData.loc[QueuedInstance.ID, "Solved"] = 1
                else:
                    simData.loc[QueuedInstance.ID, "Solved"] = 0
            else:
                simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = simData.loc[
                    QueuedInstance.ID, "TimeServiceBegins"]  # No execution time is given
                simData.loc[QueuedInstance.ID, "Attended"] = 0
                simData.loc[QueuedInstance.ID, "Solved"] = 0

            simData.loc[QueuedInstance.ID, "TimeInstanceInSystem"] = simData.loc[QueuedInstance.ID, "TimeServiceEnds"] - simData.loc[QueuedInstance.ID, "ArrivalTime"]
            VMs[vmID].processingInstanceID = QueuedInstance.ID
            VMs[vmID].nextEndTime = simData.loc[QueuedInstance.ID, "TimeServiceEnds"]

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


def simulateInstanceArrivals_HeuristicStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, stopWhenQueue=2):
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
            q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():

                QueuedInstance = q.get()
                simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
                simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
                simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                simData.loc[QueuedInstance.ID, "VM"] = vmID

                if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]:
                    simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + QueuedInstance.RealServiceTime
                    simData.loc[QueuedInstance.ID, "Attended"] = 1
                    if (QueuedInstance.RealServiceTime < instanceCapTime):
                        simData.loc[QueuedInstance.ID, "Solved"] = 1
                    else:
                        simData.loc[QueuedInstance.ID, "Solved"] = 0
                else:
                    simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = simData.loc[
                        QueuedInstance.ID, "TimeServiceBegins"]  # No execution time is given
                    simData.loc[QueuedInstance.ID, "Attended"] = 0
                    simData.loc[QueuedInstance.ID, "Solved"] = 0

                simData.loc[QueuedInstance.ID, "TimeInstanceInSystem"] = simData.loc[QueuedInstance.ID, "TimeServiceEnds"] - simData.loc[QueuedInstance.ID, "ArrivalTime"]
                VMs[vmID].processingInstanceID = QueuedInstance.ID
                VMs[vmID].nextEndTime = simData.loc[QueuedInstance.ID, "TimeServiceEnds"]
                vmID = getVMwithSmallestEndTime(VMs)

        # If the queue is not empty after simulation, then put it in queue. Otherwise attend it

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            q = HeuristicEvaluateContinueToExecute(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue, useClassification=False)
        else:
            VMs[vmID].processingInstanceID = ArrivingInstance.ID
            simData.loc[ArrivingInstance.ID, "TimeServiceBegins"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "TimeServiceEnds"] = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "WaitingTimeInQueue"] = 0
            simData.loc[ArrivingInstance.ID, "TimeInstanceInSystem"] = ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "IdleTimeOfServer"] = ArrivingInstance.ArrivalTime - VMs[vmID].nextEndTime
            simData.loc[ArrivingInstance.ID, "VM"] = VMs[vmID].ID
            simData.loc[ArrivingInstance.ID, "Attended"] = 1
            VMs[vmID].nextEndTime = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime

            if (ArrivingInstance.RealServiceTime < instanceCapTime):
                simData.loc[ArrivingInstance.ID, "Solved"] = 1
            else:
                simData.loc[ArrivingInstance.ID, "Solved"] = 0

    # Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]:
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
def simulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, stopWhenQueue=2):
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
            q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)

            if not q.empty():
                QueuedInstance = q.get()
                simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
                simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
                simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                simData.loc[QueuedInstance.ID, "VM"] = vmID

                if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"] and (QueuedInstance.PredictedSolvable != 0):
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
                vmID = getVMwithSmallestEndTime(VMs)

        #If the queue is not empty after simulation, then put it in queue. Otherwise attend it

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            q = HeuristicEvaluateContinueToExecute(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue, useClassification=True)
        elif (ArrivingInstance.PredictedSolvable != 0):
            VMs[vmID].processingInstanceID = ArrivingInstance.ID
            simData.loc[ArrivingInstance.ID, "TimeServiceBegins"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "TimeServiceEnds"] = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "WaitingTimeInQueue"] = 0
            simData.loc[ArrivingInstance.ID, "TimeInstanceInSystem"] = ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "IdleTimeOfServer"] = ArrivingInstance.ArrivalTime - VMs[vmID].nextEndTime
            simData.loc[ArrivingInstance.ID, "VM"] = VMs[vmID].ID
            simData.loc[ArrivingInstance.ID, "Attended"] = 1
            VMs[vmID].nextEndTime = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime

            if (ArrivingInstance.RealServiceTime < instanceCapTime):
                simData.loc[ArrivingInstance.ID, "Solved"] = 1
            else:
                simData.loc[ArrivingInstance.ID, "Solved"] = 0
        else:
            VMs[vmID].processingInstanceID = ArrivingInstance.ID
            simData.loc[ArrivingInstance.ID, "TimeServiceBegins"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "TimeServiceEnds"] = ArrivingInstance.ArrivalTime
            simData.loc[ArrivingInstance.ID, "WaitingTimeInQueue"] = 0
            simData.loc[ArrivingInstance.ID, "TimeInstanceInSystem"] = 1
            simData.loc[ArrivingInstance.ID, "IdleTimeOfServer"] = ArrivingInstance.ArrivalTime - VMs[vmID].nextEndTime
            simData.loc[ArrivingInstance.ID, "VM"] = VMs[vmID].ID
            simData.loc[ArrivingInstance.ID, "Attended"] = 0
            VMs[vmID].nextEndTime = simData.loc[ArrivingInstance.ID, "TimeServiceEnds"]
            simData.loc[ArrivingInstance.ID, "Solved"] = 0

    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"] and (QueuedInstance.PredictedSolvable != 0):
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

