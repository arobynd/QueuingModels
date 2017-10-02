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

def getVM_CSV(VMs):
    CSV = str(int(VMs[0].nextEndTime))
    if len(VMs) > 1:
        for i in range(1, len(VMs)):
            CSV = CSV+","+str(int(VMs[i].nextEndTime))
    return CSV
##############################
##############################


def assignPriorityForScheduling(index, row, schedulingPolicy, nextEndTime=0):
    # Returns an object Instance(ID, RealServiceTime, PredictedServiceTime, ArrivalTime, priority)

    if schedulingPolicy == "FCFS":  # The priority is the arrival time
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["ArrivalTime"])

    elif schedulingPolicy == "SJF":  # (SJF -Shortest Job First) The priority is the predicted service time
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["PredictedServiceTime"])

    elif schedulingPolicy == "MIP": #The priority is the predicted start time after running MIP using estimated service times
        #return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        #row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["PredictedServiceTime"]*row["ArrivalTime"])#row["MIPPredictedTimeServiceBegins"])
        #return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
        #                row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["PredictedServiceTime"]+nextEndTime + row["maximumWaitingTime"])
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"], row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["PredictedServiceTime"])
    else:
        print "Unknown policy, default arrival time will be used as queuing priority"
        return Instance(index, row["RealServiceTime"], row["PredictedServiceTime"], row["ArrivalTime"],
                        row["RealSolvable"], row["PredictedSolvable"], row["maximumWaitingTime"], row["ArrivalTime"])

##############################
##############################



def CheckConsistency(simDataDir, instanceCapTime):
    simData = pd.read_csv(simDataDir, index_col=0)
    x = simData.sort_values(by=["VM","TimeServiceBegins","TimeServiceEnds"], ascending=[True, True, True])
    actualVM=0

    myiter= iter(range(1,x.shape[0]))
    for i in myiter:

        if actualVM != x.iloc[i]["VM"]:
            i=next(myiter, None)
            actualVM=actualVM+1

        if x.iloc[i]["TimeServiceBegins"] < x.iloc[i-1]["TimeServiceEnds"]:
            print "Instance ", i , " - Inconsistency: instance(i)(TimeServiceBegins) >= instance(i-1)(TimeServiceEnds)"
            print x.iloc[i - 1]
            print x.iloc[i]
            return False
        if x.iloc[i]["TimeServiceBegins"] > x.iloc[i]["TimeServiceEnds"]:
            print "Instance ", i , " - Inconsistency: instance(i)(TimeServiceBegins) <= instance(i)(TimeServiceEnds)"
            print x.iloc[i - 1]
            print x.iloc[i]
            return False
        if x.iloc[i]["Solved"] == 1 and x.iloc[i]["RealServiceTime"] >= instanceCapTime:
            print "Instance ", i , " - Inconsistency: unsolved instance marked as solved: "
            print x.iloc[i]
            return False
    return True

##############################
##############################


def deleteTimedOutInstances(queue, Time, simData, vmID):
    auxQueue = Queue.PriorityQueue()
    while not queue.empty():
        instance = queue.get()
        if (Time - instance.ArrivalTime > instance.maximumWaitingTime ):
            simData.loc[instance.ID, "TimeServiceBegins"] = Time
            simData.loc[instance.ID, "TimeServiceEnds"] = Time
            simData.loc[instance.ID, "Attended"] = 0
            simData.loc[instance.ID, "Solved"] = 0
            #simData.loc[instance.ID, "Stopped"] = 0
            simData.loc[instance.ID, "WaitingTimeInQueue"] = Time - instance.ArrivalTime
            simData.loc[instance.ID, "IdleTimeOfServer"] = 0
            simData.loc[instance.ID, "VM"] = vmID
            simData.loc[instance.ID, "TimeInstanceInSystem"] = Time - instance.ArrivalTime
            simData.loc[instance.ID, "QueuedInstances"] = queue.qsize() + 1
        else:
            auxQueue.put(instance)

    return auxQueue

##############################
##############################


def beginToProcessInstance_R(q, QueuedInstance, simData, VMs, vmID, instanceCapTime):
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
    return VMs

##############################
##############################


def beginToProcessInstance_R_C(q, QueuedInstance, simData, VMs, vmID, instanceCapTime):
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

    return VMs

##############################
##############################


def beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime):
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

    return VMs


##############################
##############################

def doNotProcessInstance(VMs, vmID, ArrivingInstance, simData):
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

    return VMs
