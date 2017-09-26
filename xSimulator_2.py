import Queue
from SimulatorSources.Instance import Instance
import os


import pandas as pd
import numpy as np


##############################
##############################

def simulationSummary(data, nVMs, outputLog):
    file = open(outputLog, "w")
    file.write("************ SYSTEM SUMMARY ************")
    file.write( "\nNumber of instances used for the simulation," + str(data.shape[0]))
    file.write( "\nTotal waiting time," + str(np.sum(data["WaitingTimeInQueue"])))
    file.write( "\nAverage instance waiting time," + str(np.average(data["WaitingTimeInQueue"])))
    waitingInstances = data[(data.WaitingTimeInQueue > 0)].shape[0]
    file.write( "\nAverage waiting time for instances that waited," + str(float(np.sum(data["WaitingTimeInQueue"])) / float(
        waitingInstances)))
    file.write( "\nNumber of instances that waited for service," + str(waitingInstances))
    file.write( "\nProbability that an instance has to wait," + str(float(waitingInstances) / float(data.shape[0])))
    file.write( "\nAverage time an instance spends in the system," + str(np.average(data["TimeInstanceInSystem"])))
    file.write( "\nIdle time proportion of the server w.r.t simulation runtime," + str(np.sum(data["IdleTimeOfServer"]) / np.max(
        data["TimeServiceEnds"])))

    if nVMs > 1:
        for i in range(0, nVMs):
            file.write( "\n************ VM " + str(i) + " SUMMARY ************")
            aux = data[data.VM == i]
            file.write( "\nNumber of instances processed," + str(aux.shape[0]))
            file.write( "\nTotal waiting time," + str(np.sum(aux["WaitingTimeInQueue"])))
            file.write( "\nAverage instance waiting time," + str(np.average(aux["WaitingTimeInQueue"])))
            waitingInstances = aux[(aux.WaitingTimeInQueue > 0)].shape[0]
            file.write( "\nAverage waiting time for instances that waited," + str(float(
                np.sum(aux["WaitingTimeInQueue"])) / float(waitingInstances)))
            file.write( "\nNumber of instances that waited for service," + str(waitingInstances))
            file.write( "\nProbability that an instance has to wait," + str(float(waitingInstances) / float(aux.shape[0])))
            file.write( "\nAverage time an instance spends in the system," + str(np.average(aux["TimeInstanceInSystem"])))
            file.write( "\nIdle time proportion of the server w.r.t simulation runtime," + str(np.sum(
                aux["IdleTimeOfServer"]) / np.max(aux["TimeServiceEnds"])))

    file.close()
    file = open(outputLog, "r")
    print file.read()

##############################
##############################


def getVMwithSmallestEndTime(VMs):
    minimum = VMs[0].nextEndTime
    index = VMs[0].ID
    if len(VMs) >= 1:
        for i in range(1, len(VMs)):
            if VMs[i].nextEndTime < minimum:
                minimum = VMs[i].nextEndTime
                index = VMs[i].ID
    return index

##############################
##############################


def assignPriorityForScheduling(index, row, schedulingPolicy):
    # Returns an object Instance(ID, RealServiceTime, PredictedServiceTime, ArrivalTime, priority)

    if schedulingPolicy == "FCFS":  # The priority is the arrival time
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["ArrivalTime"])

    elif schedulingPolicy == "SJF":  # (SJF -Shortest Job First) The priority is the predicted service time
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["PredictedServiceTime"])

    elif schedulingPolicy == "MIP": #The priority is the predicted start time after running MIP using estimated service times
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["PredictedServiceTime"]*row["ArrivalTime"])#row["MIPPredictedTimeServiceBegins"])
    else:
        print "Unknown policy, default arrival time will be used as queuing priority"
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["ArrivalTime"])

##############################
##############################

def EvaluateContinueToExecute1(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, topQueue):
    vmID = getVMwithSmallestEndTime(VMs)
    auxQueue = Queue.PriorityQueue()

    counter = 0
    while not queue.empty():
        instance = queue.get()
        auxQueue.put(instance)
        if VMs[vmID].nextEndTime > (instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1

    queue = auxQueue
    if counter>= topQueue:
        OldInstanceID = VMs[vmID].processingInstanceID
        simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
        simData.loc[OldInstanceID, "Attended"] = 1
        simData.loc[OldInstanceID, "Solved"] = 0
        simData.loc[OldInstanceID, "Stopped"] = 1
        VMs[vmID].nextEndTime  = ArrivingInstanceTime

        QueuedInstance = queue.get()
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


    return queue


##############################
##############################

def EvaluateContinueToExecute2(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, topQueue):
    vmID = getVMwithSmallestEndTime(VMs)
    auxQueue = Queue.PriorityQueue()

    counter = 0
    while not queue.empty():
        instance = queue.get()
        auxQueue.put(instance)
        if VMs[vmID].nextEndTime > (instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1

    queue = auxQueue
    if counter>= topQueue:
        OldInstanceID = VMs[vmID].processingInstanceID
        simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
        simData.loc[OldInstanceID, "Attended"] = 1
        simData.loc[OldInstanceID, "Solved"] = 0
        simData.loc[OldInstanceID, "Stopped"] = 1
        VMs[vmID].nextEndTime  = ArrivingInstanceTime

        QueuedInstance = queue.get()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"])  and (QueuedInstance.PredictedSolvable != 0):
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

def EvaluateContinueToExecuteMIP1(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, stopWhenQueue,  outputFile, searchTime, GAPsize, model):
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
        simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
        simData.loc[OldInstanceID, "Attended"] = 1
        simData.loc[OldInstanceID, "Solved"] = 0
        simData.loc[OldInstanceID, "Stopped"] = 1
        VMs[vmID].nextEndTime  = ArrivingInstanceTime

        queue = updatePrioritiesMIP(queue, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData,model)

        QueuedInstance = queue.get()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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
def EvaluateContinueToExecuteMIP2(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, stopWhenQueue,  outputFile, searchTime, GAPsize, model):
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
        simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
        simData.loc[OldInstanceID, "Attended"] = 1
        simData.loc[OldInstanceID, "Solved"] = 0
        simData.loc[OldInstanceID, "Stopped"] = 1
        VMs[vmID].nextEndTime  = ArrivingInstanceTime

        queue = updatePrioritiesMIP(queue, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData,model)

        QueuedInstance = queue.get()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"])  and (QueuedInstance.PredictedSolvable != 0):
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
def EvaluateContinueToExecuteMIP3(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, stopWhenQueue,  outputFile, searchTime, GAPsize, model):
    vmID = getVMwithSmallestEndTime(VMs)
    auxQueue = Queue.PriorityQueue()

    counter = 0
    while not queue.empty():
        instance = queue.get()
        auxQueue.put(instance)
        if VMs[vmID].nextEndTime > (instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1

    queue = auxQueue
    if counter>= stopWhenQueue and  simData.loc[VMs[vmID].processingInstanceID, "MIPAttended"] == -1: #Perform operations only if the instance has not been scheduled by MIP
        OldInstanceID = VMs[vmID].processingInstanceID
        simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
        simData.loc[OldInstanceID, "Attended"] = 1
        simData.loc[OldInstanceID, "Solved"] = 0
        simData.loc[OldInstanceID, "Stopped"] = 1
        VMs[vmID].nextEndTime  = ArrivingInstanceTime

        queue = updatePrioritiesMIP(queue, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData,model)

        QueuedInstance = queue.get()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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
def EvaluateContinueToExecuteMIP4(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, stopWhenQueue,  outputFile, searchTime, GAPsize, model):
    vmID = getVMwithSmallestEndTime(VMs)
    auxQueue = Queue.PriorityQueue()

    counter = 0
    while not queue.empty():
        instance = queue.get()
        auxQueue.put(instance)
        if VMs[vmID].nextEndTime > (instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1

    queue = auxQueue
    if counter>= stopWhenQueue and simData.loc[VMs[vmID].processingInstanceID, "MIPAttended"] == -1: #Perform operations only if the instance has not been scheduled by MIP:
        OldInstanceID = VMs[vmID].processingInstanceID
        simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
        simData.loc[OldInstanceID, "Attended"] = 1
        simData.loc[OldInstanceID, "Solved"] = 0
        simData.loc[OldInstanceID, "Stopped"] = 1
        VMs[vmID].nextEndTime  = ArrivingInstanceTime

        queue = updatePrioritiesMIP(queue, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData,model)

        QueuedInstance = queue.get()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"])  and (QueuedInstance.PredictedSolvable != 0):
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



def simulateInstanceArrivals_HeuristicStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, stopWhenQueue=2):
    simData = pd.read_csv(inputData, index_col=0)
    simData["Stopped"] = 0
    q = Queue.PriorityQueue()
    for index, row in simData.iterrows():

        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy)  # Create the instance

        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
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
        # simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            q=EvaluateContinueToExecute1(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue)
        else:
            VMs[vmID].processingInstanceID = ArrivingInstance.ID
            simData.loc[ArrivingInstance.ID, "TimeServiceBegins"] = ArrivingInstance.ArrivalTime
            simData.loc[
                ArrivingInstance.ID, "TimeServiceEnds"] = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "WaitingTimeInQueue"] = 0
            simData.loc[ArrivingInstance.ID, "TimeInstanceInSystem"] = ArrivingInstance.RealServiceTime
            simData.loc[ArrivingInstance.ID, "IdleTimeOfServer"] = ArrivingInstance.ArrivalTime - VMs[
                vmID].nextEndTime
            simData.loc[ArrivingInstance.ID, "VM"] = VMs[vmID].ID
            simData.loc[ArrivingInstance.ID, "Attended"] = 1
            VMs[vmID].nextEndTime = ArrivingInstance.ArrivalTime + ArrivingInstance.RealServiceTime

            if (ArrivingInstance.RealServiceTime < instanceCapTime):
                simData.loc[ArrivingInstance.ID, "Solved"] = 1
            else:
                simData.loc[ArrivingInstance.ID, "Solved"] = 0

    # Finish to attend queued instances
    while not q.empty():
        # simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[
                                                                   vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[
            QueuedInstance.ID, "maximumWaitingTime"]:
            simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[
                                                                    vmID].nextEndTime + 1 + QueuedInstance.RealServiceTime
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

        simData.loc[QueuedInstance.ID, "TimeInstanceInSystem"] = simData.loc[QueuedInstance.ID, "TimeServiceEnds"] - \
                                                                 simData.loc[QueuedInstance.ID, "ArrivalTime"]
        VMs[vmID].processingInstanceID = QueuedInstance.ID
        VMs[vmID].nextEndTime = simData.loc[QueuedInstance.ID, "TimeServiceEnds"]

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)

    # print "Creating simulation log: " + outputFile + "LOG.csv"
    # simulationSummary(sim, len(VMs), outputFile + "LOG.csv")

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
    for index, row in simData.iterrows():

        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance

        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
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
        #simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()

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
        #simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)

    #print "Creating simulation log: " + outputFile + "LOG.csv"
    #simulationSummary(sim, len(VMs), outputFile + "LOG.csv")

    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim
##############################
##############################


def simulateInstanceArrivals_NaiveStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    for index, row in simData.iterrows():

        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance

        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
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
        #simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()

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
        #simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)

    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim


##############################
##############################

def updatePrioritiesMIP(queue, outputFile, searchTime, GAPsize, instanceCapTime, lastEndTime, simData, model="model1"):
    auxQueue = Queue.PriorityQueue()
    finalQueue = Queue.PriorityQueue()
    print "Executing MIP with:"

    instance = queue.get()
    print instance
    auxQueue.put(instance)
    instanceArrivalTimesCSV=str(int(instance.ArrivalTime))
    instanceExecutionTimesCSV=str(int(instance.PredictedServiceTime))
    instanceMaximumExpectedWaitingTimeCSV=str(int(instance.maximumWaitingTime))
    instanceSolvableCSV=str(int(instance.PredictedSolvable))

    while not queue.empty():
        instance=queue.get()
        print instance
        auxQueue.put(instance)
        instanceArrivalTimesCSV = instanceArrivalTimesCSV+","+str(int(instance.ArrivalTime))
        instanceExecutionTimesCSV = instanceExecutionTimesCSV+","+str(int(instance.PredictedServiceTime))
        instanceMaximumExpectedWaitingTimeCSV = instanceMaximumExpectedWaitingTimeCSV+","+str(int(instance.maximumWaitingTime))
        instanceSolvableCSV = instanceSolvableCSV+","+str(int(instance.PredictedSolvable))

    SolutionsLog = outputFile + "_SolutionsLog.txt"

    cmd = "bash runMIP.sh " + \
          instanceArrivalTimesCSV + " " + \
          instanceExecutionTimesCSV + " " + \
          str(instanceMaximumExpectedWaitingTimeCSV) + " " + \
          str(instanceCapTime) + " " + \
          str(searchTime) + " " + \
          str(GAPsize) + " " + \
          str(int(lastEndTime)) + " " + \
          instanceSolvableCSV + " " + \
          model + " " + \
          "../" + outputFile + " " + " | tee -a " + SolutionsLog
    os.system(cmd)

    MIPsimulationData = pd.read_csv(outputFile + "_Temp.csv")

    #The order of the instances in the *_Temp.csv file is identical to the instance order in the queue
    #If MIP finds an answer, then the arrivals must match, otherwise, the priorities are left as they were initially
    # for index, row in MIPsimulationData.iterrows():
    #     instance = auxQueue.get()
    #     if (row["ArrivalTime"]==instance.ArrivalTime):#If MIP finds a solution for the actual queued instances
    #         instance.priority=row["MIPPredictedTimeServiceBegins"] + ((1 - row["MIPAttended"]) * row["MIPPredictedTimeServiceBegins"] *100)
    #     print instance
    #     finalQueue.put(instance)

    while not auxQueue.empty():
        instance = auxQueue.get()
        row = MIPsimulationData[MIPsimulationData.ArrivalTime == instance.ArrivalTime]
        if len(row)>0:#If MIP finds a solution for the actual queued instances
            instance.priority = int(row["MIPPredictedTimeServiceBegins"])
            simData.loc[instance.ID, "MIPAttended"] =int(row["MIPAttended"])

        print instance
        finalQueue.put(instance)
    return finalQueue



##############################
##############################


def MIPsimulateInstanceArrivals_NaiveStrategy_Regression_Classification(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1"):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0):
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

        #If the queue is not empty after simulation, then put it in queuei. Otherwise attend it
        simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime: # and (ArrivingInstance.PredictedSolvable != 0):
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

        simData.to_csv(outputFile)
        #Execute MIP every groupSize arriving Instances...To update priorities
        if (index % groupSize == 0 and q.qsize()>1):
            #print "index:", index
            vmID = getVMwithSmallestEndTime(VMs)
            q = updatePrioritiesMIP(q, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData, model)



    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
        simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0):
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim

##############################
##############################
def MIPsimulateInstanceArrivals_NaiveStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1"):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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
        simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()

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


        simData.to_csv(outputFile)
        #Execute MIP every groupSize arriving Instances...To update priorities
        if (index % groupSize == 0 and q.qsize()>1):
            #print "index:", index
            vmID = getVMwithSmallestEndTime(VMs)
            q = updatePrioritiesMIP(q, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData, model)



    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
        simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim




##############################
##############################



def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1", stopWhenQueue=2):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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
        simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            q = EvaluateContinueToExecuteMIP1(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue, outputFile, searchTime, GAPsize, model)

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



        simData.to_csv(outputFile)
        # #Execute MIP every groupSize arriving Instances...To update priorities
        if (index % groupSize == 0 and q.qsize()>1):
            #print "index:", index
            vmID = getVMwithSmallestEndTime(VMs)
            q = updatePrioritiesMIP(q, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData, model)



    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
        simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim


##############################
##############################



def MIPsimulateInstanceArrivals_HeuristicStrategy_NotScheduled_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1", stopWhenQueue=2):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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
        simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            q = EvaluateContinueToExecuteMIP3(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue, outputFile, searchTime, GAPsize, model)

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



        simData.to_csv(outputFile)
        # #Execute MIP every groupSize arriving Instances...To update priorities
        if (index % groupSize == 0 and q.qsize()>1):
            #print "index:", index
            vmID = getVMwithSmallestEndTime(VMs)
            q = updatePrioritiesMIP(q, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData, model)



    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
        simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim







##############################
##############################


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1", stopWhenQueue=2):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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
        simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime: # and (ArrivingInstance.PredictedSolvable != 0):
            q.put(ArrivingInstance)
            q = EvaluateContinueToExecuteMIP2(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue,outputFile, searchTime, GAPsize, model)
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



        simData.to_csv(outputFile)

        #Execute MIP every groupSize arriving Instances...To update priorities
        if (index % groupSize == 0 and q.qsize()>1):
            #print "index:", index
            vmID = getVMwithSmallestEndTime(VMs)
            q = updatePrioritiesMIP(q, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData, model)



    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
        simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim

##############################
##############################


def MIPsimulateInstanceArrivals_HeuristicStrategy_NotScheduled_Regression_Classification(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1", stopWhenQueue=2):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    for index, row in simData.iterrows():
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance
        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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
        simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime: # and (ArrivingInstance.PredictedSolvable != 0):
            q.put(ArrivingInstance)
            q = EvaluateContinueToExecuteMIP4(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue,outputFile, searchTime, GAPsize, model)
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



        simData.to_csv(outputFile)

        #Execute MIP every groupSize arriving Instances...To update priorities
        if (index % groupSize == 0 and q.qsize()>1):
            #print "index:", index
            vmID = getVMwithSmallestEndTime(VMs)
            q = updatePrioritiesMIP(q, outputFile, searchTime, GAPsize, instanceCapTime, VMs[vmID].nextEndTime, simData, model)



    #Finish to attend queued instances
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
        simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize()
        simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
        simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
        simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
        simData.loc[QueuedInstance.ID, "VM"] = vmID

        if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
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
    q = Queue.PriorityQueue()
    for index, row in simData.iterrows():

        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy) #Create the instance

        vmID = getVMwithSmallestEndTime(VMs)

        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            QueuedInstance = q.get()
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
        #simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            q = EvaluateContinueToExecute2(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue)
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
        #simData.loc[ArrivingInstance.ID, "Q"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        QueuedInstance = q.get()
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

    sim = simData.sort_values(by=["TimeServiceBegins"], ascending=[True])
    sim.to_csv(outputFile)

    #print "Creating simulation log: " + outputFile + "LOG.csv"
    #simulationSummary(sim, len(VMs), outputFile + "LOG.csv")

    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim
##############################
##############################


def CheckConsistency(simDataDir, instanceCapTime):
    simData = pd.read_csv(simDataDir, index_col=0)
    x = simData.sort_values(by=["VM","TimeServiceBegins"], ascending=[True, True])
    actualVM=0

    myiter= iter(range(1,x.shape[0]))
    for i in myiter:

        if actualVM != x.iloc[i]["VM"]:
            i=next(myiter, None)
            actualVM=actualVM+1

        if x.iloc[i]["TimeServiceBegins"] <= x.iloc[i-1]["TimeServiceEnds"]:
            print "Inconsistency: instance(i)(TimeServiceBegins) <= instance(i-1)(TimeServiceEnds)"
            print x.iloc[i - 1]
            print x.iloc[i]
            return False
        if x.iloc[i]["Solved"] == 1 and x.iloc[i]["RealServiceTime"] >= instanceCapTime:
            print "Inconsistency: unsolved instance marked as solved: "
            print x.iloc[i]
            return False
    return True

