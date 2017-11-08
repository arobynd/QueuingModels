import Queue
from SimulatorSources.Instance import Instance
from SimulatorCommon import *
import os
import time
import math
import pandas as pd
import numpy as np

##############################
##############################
# def HeuristicDeleteWhenNotScheduledMIP(queue, Time, simData, vmID, dequeueWhenNotScheduledMIP=0):
#
#     # The instance is put in the queue if dequeueWhenNotScheduledMIP is disabled (i.e., 0 ) or when the instance is determined
#     # not to be scheduled for execution less than (dequeueWhenNotScheduledMIP) times
#
#     auxQueue = Queue.PriorityQueue()
#     while not queue.empty():
#         instance = queue.get()
#         if (dequeueWhenNotScheduledMIP!=0 and simData.loc[instance.ID, "MIPnotScheduled"] >= dequeueWhenNotScheduledMIP):
#             simData.loc[instance.ID, "TimeServiceBegins"] = Time
#             simData.loc[instance.ID, "TimeServiceEnds"] = Time
#             simData.loc[instance.ID, "Attended"] = 0
#             simData.loc[instance.ID, "Solved"] = 0
#             simData.loc[instance.ID, "Stopped"] = 0
#             simData.loc[instance.ID, "WaitingTimeInQueue"] = Time - instance.ArrivalTime
#             simData.loc[instance.ID, "IdleTimeOfServer"] = 0
#             simData.loc[instance.ID, "VM"] = vmID
#             simData.loc[instance.ID, "TimeInstanceInSystem"] = Time - instance.ArrivalTime
#             simData.loc[instance.ID, "QueuedInstances"] = queue.qsize() + 1
#         else:
#             auxQueue.put(instance)
#
#     return auxQueue

##############################
##############################

def HeuristicEvaluateContinueToExecuteMIP_1Queue(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, heuristicH, useClassification = False):
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
        if (simData.loc[OldInstanceID, "TimeServiceEnds"] != simData.loc[OldInstanceID, "TimeServiceBegins"]) and (ArrivingInstanceTime >=simData.loc[OldInstanceID, "TimeServiceBegins"]):
            simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
            simData.loc[OldInstanceID, "Attended"] = 1
            simData.loc[OldInstanceID, "Solved"] = 0
            simData.loc[OldInstanceID, "Stopped"] = 1
            simData.loc[OldInstanceID, "TimeInstanceInSystem"] = ArrivingInstanceTime - simData.loc[OldInstanceID, "ArrivalTime"]
            VMs[vmID].nextEndTime  = ArrivingInstanceTime

        processing = False
        while (not queue.empty()) and processing == False:
            QueuedInstance = queue.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            PredictedSolvable=True
            if useClassification == True:
                PredictedSolvable = (QueuedInstance.PredictedSolvable != 0)

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0 and PredictedSolvable):
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


def HeuristicEvaluateContinueToExecuteMIP_2Queues(executionQueue, arrivingQueue, simData, VMs, ArrivingInstanceTime, instanceCapTime, heuristicH, useClassification = False):

    vmID = getVMwithSmallestEndTime(VMs)
    totalQueue = mergeQueues(copyOfQueue(arrivingQueue),copyOfQueue(executionQueue))
    counter = 0
    while not totalQueue.empty():
        instance = totalQueue.get()
        if VMs[vmID].nextEndTime > (instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1


    if counter>= heuristicH:
        OldInstanceID = VMs[vmID].processingInstanceID
        # If the instance is being attended, then it can be stopped, otherwise the end time could be smaller than the start time
        if (simData.loc[OldInstanceID, "TimeServiceEnds"] != simData.loc[OldInstanceID, "TimeServiceBegins"]) and (ArrivingInstanceTime >=simData.loc[OldInstanceID, "TimeServiceBegins"]):
            simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
            simData.loc[OldInstanceID, "Attended"] = 1
            simData.loc[OldInstanceID, "Solved"] = 0
            simData.loc[OldInstanceID, "Stopped"] = 1
            simData.loc[OldInstanceID, "TimeInstanceInSystem"] = ArrivingInstanceTime - simData.loc[OldInstanceID, "ArrivalTime"]
            VMs[vmID].nextEndTime  = ArrivingInstanceTime

        #Getting the next instance from the executionQueue
        processing = False
        while (not executionQueue.empty()) and processing == False:
            QueuedInstance = executionQueue.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            PredictedSolvable=True
            if useClassification == True:
                PredictedSolvable = (QueuedInstance.PredictedSolvable != 0)

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0 and PredictedSolvable):
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

        # Getting the next instance from the arrivingQueue if the attempt from executionQueue failed
        while (not arrivingQueue.empty()) and processing == False:
            QueuedInstance = arrivingQueue.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[
                                                                       vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            PredictedSolvable = True
            if useClassification == True:
                PredictedSolvable = (QueuedInstance.PredictedSolvable != 0)

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0 and PredictedSolvable):
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


##############################
##############################


def HeuristicEvaluateContinueToExecuteMIP_3Queues(executionQueue, arrivingQueue, stoppedQueue, simData, VMs,ArrivingInstanceTime, instanceCapTime, heuristicH,useClassification=False):

    vmID = getVMwithSmallestEndTime(VMs)
    totalQueue = mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue))
    counter = 0
    while not totalQueue.empty():
        instance = totalQueue.get()
        if VMs[vmID].nextEndTime > (
                instance.ArrivalTime + instance.PredictedServiceTime + instance.maximumWaitingTime):
            counter = counter + 1

    if counter >= heuristicH:
        OldInstanceID = VMs[vmID].processingInstanceID
        # If the instance is being attended, then it can be stopped, otherwise the end time could be smaller than the start time
        if (simData.loc[OldInstanceID, "TimeServiceEnds"] != simData.loc[
            OldInstanceID, "TimeServiceBegins"]) and (
            ArrivingInstanceTime >= simData.loc[OldInstanceID, "TimeServiceBegins"]):
            simData.loc[OldInstanceID, "TimeServiceEnds"] = ArrivingInstanceTime
            simData.loc[OldInstanceID, "Attended"] = 1
            simData.loc[OldInstanceID, "Solved"] = 0
            simData.loc[OldInstanceID, "Stopped"] = 1
            simData.loc[OldInstanceID, "TimeInstanceInSystem"] = ArrivingInstanceTime - simData.loc[
                OldInstanceID, "ArrivalTime"]
            VMs[vmID].nextEndTime = ArrivingInstanceTime
            auxOldInstance = assignPriorityForScheduling(OldInstanceID, simData.loc[OldInstanceID], "SJF", VMs[vmID].nextEndTime +1)
            stoppedQueue.put(auxOldInstance)

        # Getting the next instance from the executionQueue
        processing = False
        while (not executionQueue.empty()) and processing == False:
            QueuedInstance = executionQueue.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[
                                                                       vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            PredictedSolvable = True
            if useClassification == True:
                PredictedSolvable = (QueuedInstance.PredictedSolvable != 0)

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[
                QueuedInstance.ID, "maximumWaitingTime"]) and (
                    simData.loc[QueuedInstance.ID, "MIPAttended"] != 0 and PredictedSolvable):
                processing = True
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

            simData.loc[QueuedInstance.ID, "TimeInstanceInSystem"] = simData.loc[
                                                                         QueuedInstance.ID, "TimeServiceEnds"] - \
                                                                     simData.loc[
                                                                         QueuedInstance.ID, "ArrivalTime"]
            VMs[vmID].processingInstanceID = QueuedInstance.ID
            VMs[vmID].nextEndTime = simData.loc[QueuedInstance.ID, "TimeServiceEnds"]

        # Getting the next instance from the arrivingQueue if the attempt from executionQueue failed
        while (not arrivingQueue.empty()) and processing == False:
            QueuedInstance = arrivingQueue.get()
            simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1
            simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[
                                                                       vmID].nextEndTime + 1 - QueuedInstance.ArrivalTime
            simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
            simData.loc[QueuedInstance.ID, "VM"] = vmID

            PredictedSolvable = True
            if useClassification == True:
                PredictedSolvable = (QueuedInstance.PredictedSolvable != 0)

            if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[
                QueuedInstance.ID, "maximumWaitingTime"]) and (
                    simData.loc[QueuedInstance.ID, "MIPAttended"] != 0 and PredictedSolvable):
                processing = True
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

            simData.loc[QueuedInstance.ID, "TimeInstanceInSystem"] = simData.loc[
                                                                         QueuedInstance.ID, "TimeServiceEnds"] - \
                                                                     simData.loc[
                                                                         QueuedInstance.ID, "ArrivalTime"]
            VMs[vmID].processingInstanceID = QueuedInstance.ID
            VMs[vmID].nextEndTime = simData.loc[QueuedInstance.ID, "TimeServiceEnds"]


##############################
##############################
##############################
##############################


def MIPupdateSchedule(queue, outputFile, searchTime, GAPsize, instanceCapTime, nextEndTimeCSV, simData, model="model1", machines=1, nextEndTime=0):
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
    #print instanceArrivalTimesCSV
    SolutionsLog = outputFile + "_SolutionsLog.txt"

    #Create file in case CPLEX - MIP model fails to create it. The file will contain temporal solution with
    #(PredictedServiceTime, ArrivalTime, MIPPredictedTimeServiceBegins, MIPPredictedTimeServiceEnds, MIPWaitingTimeInQueue, MIPAttended, MIPVM)
    cmd = "touch " + outputFile + "_Temp.csv"
    os.system(cmd)
    # Create file in case CPLEX - MIP model fails to create it. The file will contain (ObjectiveValue,BestRelaxation,Gap)
    cmd = "touch " + outputFile + "_Obj.csv"
    os.system(cmd)
    cmd = "echo -n >> " + outputFile + "_Obj.csv" #delete file content
    os.system(cmd)
    cmd = "echo 'ObjectiveValue,BestRelaxation,Gap' >> " + outputFile + "_Obj.csv"
    os.system(cmd)
    cmd = "echo '0,0,"+str(GAPsize+1)+"' >> " + outputFile + "_Obj.csv" #add line with unwanted Gap. If Cplex finds an answer, it will be updated
    os.system(cmd)

    #Command to execute MIP model
    cmd = "bash runMIP.sh " + \
          instanceArrivalTimesCSV + " " + \
          instanceExecutionTimesCSV + " " + \
          str(instanceMaximumExpectedWaitingTimeCSV) + " " + \
          str(instanceCapTime) + " " + \
          str(searchTime) + " " + \
          str(GAPsize) + " " + \
          str(nextEndTimeCSV) + " " + \
          instanceSolvableCSV + " " + \
          model + " " + \
          "../" + outputFile + " " + \
          str(machines) + " | tee -a " + SolutionsLog
    os.system(cmd)

    MIPsimulationData = pd.read_csv(outputFile + "_Temp.csv") #Read Cplex solution

    MIPobjectiveData = pd.read_csv(outputFile + "_Obj.csv") #Read Objective and Gap data
    rowObjective = MIPobjectiveData.tail(1) #Read the last Gap
    value = float(rowObjective["Gap"].replace(",", ".")) # Get the last Gap Value

    if (value >= (GAPsize * -1)) and (value <= (GAPsize)): # If MIP finds an answer within (+-) the GAPsize
        print "Solution fulfills the GAP....Wanted Gap (+/-): " + str(GAPsize) + "....CPLEX Gap: " + str(value)
        print "MIP plicy will be applied"
        while not auxQueue.empty():
            instance = auxQueue.get()
            row = MIPsimulationData[MIPsimulationData.ArrivalTime == instance.ArrivalTime] #If MIP finds an answer, then there must be a match for each arrival
            if len(row)>0:#If MIP finds a solution for the actual queued instances
                instance.priority = int(row["MIPPredictedTimeServiceBegins"])
                simData.loc[instance.ID, "MIPAttended"] =int(row["MIPAttended"])
                if ( int(row["MIPAttended"]) == 0 ):
                    simData.loc[instance.ID, "MIPnotScheduled"] = simData.loc[instance.ID, "MIPnotScheduled"] + 1
            print instance
            finalQueue.put(instance)
    else: #update priorities to FCFS
        print "Solution does not fulfill the GAP....Wanted Gap (+/-): " + str(GAPsize) + "....CPLEX Gap: " + str(value)
        print "SJF plicy will be applied"
        while not auxQueue.empty():
            instance = auxQueue.get()
            instance.priority = instance.PredictedServiceTime #+ nextEndTime
            finalQueue.put(instance)

    return finalQueue


##############################
##############################
##############################
##############################

def findLastMIPRunTime(outputFile):
    SolutionsLog = outputFile + "_SolutionsLog.txt"
    #cmd = "grep 'Total (root+branch&cut) =' " + SolutionsLog + " | tail -1"
    #result = str(os.system(cmd))
    result = os.popen("grep 'Total (root+branch&cut) =' " + SolutionsLog + " | tail -1").readlines()
    x = result[0]
    value1 = x.split()
    value2 = value1[3]
    value3 = value2.replace(",",".")
    return float(value3)



##############################
##############################
##############################
##############################


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_3Queues(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, searchTime=120, GAPsize=0.1, model="model1", heuristicH=2, dequeueWhenNotScheduledMIP=0, KqueueSize=4):
    simData = pd.read_csv(inputData, index_col=0)
    arrivingQueue = Queue.PriorityQueue()
    executionQueue = Queue.PriorityQueue()
    stoppedQueue = Queue.PriorityQueue()
    k=KqueueSize #Maximum size of the executionQueue

    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    simData["MIPnotScheduled"] = 0
    simData["MIPRunTime"] = 0
    simData["QueuedInstances"] = 0

    for index, row in simData.iterrows():

        vmID = getVMwithSmallestEndTime(VMs)
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy, VMs[vmID].nextEndTime + 1) #Create the instance
        MIPRunTime = 0

        # There are 4 possibilities:
        # Option 1: arrivingQueue has instances     executionQueue has instances    -> instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
        # Option 2: arrivingQueue is empty          executionQueue has instances    -> instances from executionQueue need to continue to run,
        # Option 3: arrivingQueue has instances     executionQueue is empty         -> at most k instances need to be moved from arrivingQueue to executionQueue
        # Option 4: arrivingQueue is empty          executionQueue is empty         -> The system is Idle, put the instance in executionQueue

        # Attend queued instances until the actual instance arrival
        #while there are instances in the system that finish processing before the present arrival time
        while  (not mergeQueues(copyOfQueue(arrivingQueue),copyOfQueue(executionQueue)).empty()) and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:

            arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
            executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
            stoppedQueue = deleteTimedOutInstances(stoppedQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

            # If there are instances after deleting timedout instances
            if (not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty()):

                modifiedFlag = False
                # Option 1: instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
                if (not arrivingQueue.empty()) and (not executionQueue.empty()):
                    if smallestInstanceRuntime(copyOfQueue(arrivingQueue)) < largestInstanceRuntime(copyOfQueue(executionQueue)):
                        modifiedFlag = True
                        AuxQueue = mergeQueues(executionQueue, arrivingQueue) #After merging, executionQueue and arrivingQueue become empty because they are sent by reference
                        while (executionQueue.qsize() < k) and (not AuxQueue .empty()):
                            auxInstance = AuxQueue.get()
                            executionQueue.put(auxInstance)
                        while  (not AuxQueue.empty()):
                            auxInstance = AuxQueue.get()
                            arrivingQueue.put(auxInstance)

                # Option 2:
                elif (arrivingQueue.empty()) and (not executionQueue.empty()):
                    modifiedFlag = False

                # Option 3:
                elif (not arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = True
                    while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
                        auxInstance = arrivingQueue.get()
                        executionQueue.put(auxInstance)

                # Option 4:
                elif (arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = False

                ###########
                if modifiedFlag == True and executionQueue.qsize()>1:
                    executionQueue = sortBySJF(executionQueue)
                    executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0

                if not executionQueue.empty():
                    QueuedInstance = executionQueue.get()
                    VMs = MIPbeginToProcessInstance_R(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)
                    vmID = getVMwithSmallestEndTime(VMs)
            elif (arrivingQueue.empty()) and (executionQueue.empty()) and (not stoppedQueue.empty()):# Option 4:
                stoppedQueue = sortBySJF(stoppedQueue)
                stoppedInstance = stoppedQueue.get()
                executionQueue.put(stoppedInstance )
                print "Stopped instance added to execution queue:"
                print stoppedInstance

        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it because the system is idle
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            arrivingQueue.put(ArrivingInstance)
            if heuristicH > 0:
                HeuristicEvaluateContinueToExecuteMIP_3Queues(executionQueue, arrivingQueue, stoppedQueue, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH, useClassification = False)
        else:
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)

        simData.to_csv(outputFile)


    #Finish to attend queued instances
    MIPRunTime = 0
    while not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty():
        vmID = getVMwithSmallestEndTime(VMs)
        arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
        executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
        stoppedQueue = deleteTimedOutInstances(stoppedQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

        modifiedFlag = False
        while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
            modifiedFlag = True
            auxInstance = arrivingQueue.get()
            executionQueue.put(auxInstance)

        if modifiedFlag == True and executionQueue.qsize()>1:
            executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
            MIPRunTime = findLastMIPRunTime(outputFile)

        if not executionQueue.empty():
            QueuedInstance = executionQueue.get()
            VMs = MIPbeginToProcessInstance_R(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime,MIPRunTime)


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


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification_3Queues(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, searchTime=120, GAPsize=0.1, model="model1", heuristicH=2, dequeueWhenNotScheduledMIP=0, KqueueSize=4):
    simData = pd.read_csv(inputData, index_col=0)
    arrivingQueue = Queue.PriorityQueue()
    executionQueue = Queue.PriorityQueue()
    stoppedQueue = Queue.PriorityQueue()
    k=KqueueSize #Maximum size of the executionQueue

    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    simData["MIPnotScheduled"] = 0
    simData["MIPRunTime"] = 0
    simData["QueuedInstances"] = 0

    for index, row in simData.iterrows():
        vmID = getVMwithSmallestEndTime(VMs)
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy, VMs[vmID].nextEndTime + 1)  # Create the instance
        MIPRunTime = 0

        # There are 4 possibilities:
        # Option 1: arrivingQueue has instances     executionQueue has instances    -> instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
        # Option 2: arrivingQueue is empty          executionQueue has instances    -> instances from executionQueue need to continue to run,
        # Option 3: arrivingQueue has instances     executionQueue is empty         -> at most k instances need to be moved from arrivingQueue to executionQueue
        # Option 4: arrivingQueue is empty          executionQueue is empty         -> The system is Idle, put the instance in executionQueue

        # Attend queued instances until the actual instance arrival
        #while there are instances in the system that finish processing before the present arrival time
        while (not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty()) and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:

            ###########
            arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
            executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
            stoppedQueue = deleteTimedOutInstances(stoppedQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

            # If there are instances after deleting timedout instances
            if (not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty()):

                modifiedFlag = False
                # Option 1: instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
                if (not arrivingQueue.empty()) and (not executionQueue.empty()):
                    if smallestInstanceRuntime(copyOfQueue(arrivingQueue)) < largestInstanceRuntime(copyOfQueue(executionQueue)):
                        modifiedFlag = True
                        AuxQueue = mergeQueues(executionQueue, arrivingQueue) #After merging, executionQueue and arrivingQueue become empty because they are sent by reference
                        while (executionQueue.qsize() < k) and (not AuxQueue .empty()):
                            auxInstance = AuxQueue.get()
                            executionQueue.put(auxInstance)
                        while  (not AuxQueue.empty()):
                            auxInstance = AuxQueue.get()
                            arrivingQueue.put(auxInstance)

                # Option 2:
                elif (arrivingQueue.empty()) and (not executionQueue.empty()):
                    modifiedFlag = False

                # Option 3:
                elif (not arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = True
                    while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
                        auxInstance = arrivingQueue.get()
                        executionQueue.put(auxInstance)

                # Option 4:
                elif (arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = False

                ###########
                if modifiedFlag == True and executionQueue.qsize()>1:
                    executionQueue = sortBySJF(executionQueue)
                    executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0

                if not executionQueue.empty():
                    QueuedInstance = executionQueue.get()
                    VMs = MIPbeginToProcessInstance_R_C(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)
                    vmID = getVMwithSmallestEndTime(VMs)

            elif (arrivingQueue.empty()) and (executionQueue.empty()) and (not stoppedQueue.empty()):  # Option 4:
                stoppedQueue = sortBySJF(stoppedQueue)
                stoppedInstance = stoppedQueue.get()
                executionQueue.put(stoppedInstance)
                print stoppedInstance
        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it only if predicted solvable
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime: # and (ArrivingInstance.PredictedSolvable != 0):
            arrivingQueue.put(ArrivingInstance)
            if heuristicH > 0:
                HeuristicEvaluateContinueToExecuteMIP_3Queues(executionQueue, arrivingQueue,  stoppedQueue, simData, VMs,ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH,useClassification=False)
        elif (ArrivingInstance.PredictedSolvable != 0):
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)
        else:
            VMs = doNotProcessInstance(VMs, vmID, ArrivingInstance, simData)
        simData.to_csv(outputFile)


    #Finish to attend queued instances
    MIPRunTime = 0
    while not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty():
        vmID = getVMwithSmallestEndTime(VMs)
        arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
        executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
        stoppedQueue = deleteTimedOutInstances(stoppedQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

        modifiedFlag = False
        while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
            modifiedFlag = True
            auxInstance = arrivingQueue.get()
            executionQueue.put(auxInstance)

        if modifiedFlag == True and executionQueue.qsize() > 1:
            executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime,getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
            MIPRunTime = findLastMIPRunTime(outputFile)

        if not executionQueue.empty():
            QueuedInstance = executionQueue.get()
            VMs = MIPbeginToProcessInstance_R_C(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime,MIPRunTime)

    sim = simData.sort_values(by=["TimeServiceBegins","TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim


##############################
##############################


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_2Queues(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, searchTime=120, GAPsize=0.1, model="model1", heuristicH=2, dequeueWhenNotScheduledMIP=0, KqueueSize=4):
    simData = pd.read_csv(inputData, index_col=0)
    arrivingQueue = Queue.PriorityQueue()
    executionQueue = Queue.PriorityQueue()
    k=KqueueSize #Maximum size of the executionQueue

    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    simData["MIPnotScheduled"] = 0
    simData["MIPRunTime"] = 0
    simData["QueuedInstances"] = 0

    for index, row in simData.iterrows():

        vmID = getVMwithSmallestEndTime(VMs)
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy, VMs[vmID].nextEndTime + 1) #Create the instance
        MIPRunTime = 0

        # There are 4 possibilities:
        # Option 1: arrivingQueue has instances     executionQueue has instances    -> instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
        # Option 2: arrivingQueue is empty          executionQueue has instances    -> instances from executionQueue need to continue to run,
        # Option 3: arrivingQueue has instances     executionQueue is empty         -> at most k instances need to be moved from arrivingQueue to executionQueue
        # Option 4: arrivingQueue is empty          executionQueue is empty         -> The system is Idle, put the instance in executionQueue

        # Attend queued instances until the actual instance arrival
        #while there are instances in the system that finish processing before the present arrival time
        while  (not mergeQueues(copyOfQueue(arrivingQueue),copyOfQueue(executionQueue)).empty()) and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:

            arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
            executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

            # If there are instances after deleting timedout instances
            if (not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty()):

                modifiedFlag = False
                # Option 1: instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
                if (not arrivingQueue.empty()) and (not executionQueue.empty()):
                    if smallestInstanceRuntime(copyOfQueue(arrivingQueue)) < largestInstanceRuntime(copyOfQueue(executionQueue)):
                        modifiedFlag = True
                        AuxQueue = mergeQueues(executionQueue, arrivingQueue) #After merging, executionQueue and arrivingQueue become empty because they are sent by reference
                        while (executionQueue.qsize() < k) and (not AuxQueue .empty()):
                            auxInstance = AuxQueue.get()
                            executionQueue.put(auxInstance)
                        while  (not AuxQueue.empty()):
                            auxInstance = AuxQueue.get()
                            arrivingQueue.put(auxInstance)

                # Option 2:
                elif (arrivingQueue.empty()) and (not executionQueue.empty()):
                    modifiedFlag = False

                # Option 3:
                elif (not arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = True
                    while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
                        auxInstance = arrivingQueue.get()
                        executionQueue.put(auxInstance)

                # Option 4:
                elif (arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = False

                ###########
                if modifiedFlag == True and executionQueue.qsize()>1:
                    executionQueue = sortBySJF(executionQueue)
                    executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0

                if not executionQueue.empty():
                    QueuedInstance = executionQueue.get()
                    VMs = MIPbeginToProcessInstance_R(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)
                    vmID = getVMwithSmallestEndTime(VMs)


        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it because the system is idle
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            arrivingQueue.put(ArrivingInstance)
            if heuristicH > 0:
                HeuristicEvaluateContinueToExecuteMIP_2Queues(executionQueue, arrivingQueue,simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH, useClassification = False)
        else:
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)

        simData.to_csv(outputFile)


    #Finish to attend queued instances
    MIPRunTime = 0
    while not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty():
        vmID = getVMwithSmallestEndTime(VMs)
        arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
        executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

        modifiedFlag = False
        while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
            modifiedFlag = True
            auxInstance = arrivingQueue.get()
            executionQueue.put(auxInstance)

        if modifiedFlag == True and executionQueue.qsize()>1:
            executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
            MIPRunTime = findLastMIPRunTime(outputFile)

        if not executionQueue.empty():
            QueuedInstance = executionQueue.get()
            VMs = MIPbeginToProcessInstance_R(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime,MIPRunTime)


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


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification_2Queues(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, searchTime=120, GAPsize=0.1, model="model1", heuristicH=2, dequeueWhenNotScheduledMIP=0, KqueueSize=4):
    simData = pd.read_csv(inputData, index_col=0)
    arrivingQueue = Queue.PriorityQueue()
    executionQueue = Queue.PriorityQueue()
    k=KqueueSize #Maximum size of the executionQueue

    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    simData["MIPnotScheduled"] = 0
    simData["MIPRunTime"] = 0
    simData["QueuedInstances"] = 0

    for index, row in simData.iterrows():
        vmID = getVMwithSmallestEndTime(VMs)
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy, VMs[vmID].nextEndTime + 1)  # Create the instance
        MIPRunTime = 0

        # There are 4 possibilities:
        # Option 1: arrivingQueue has instances     executionQueue has instances    -> instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
        # Option 2: arrivingQueue is empty          executionQueue has instances    -> instances from executionQueue need to continue to run,
        # Option 3: arrivingQueue has instances     executionQueue is empty         -> at most k instances need to be moved from arrivingQueue to executionQueue
        # Option 4: arrivingQueue is empty          executionQueue is empty         -> The system is Idle, put the instance in executionQueue

        # Attend queued instances until the actual instance arrival
        #while there are instances in the system that finish processing before the present arrival time
        while (not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty()) and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:

            ###########
            arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
            executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

            # If there are instances after deleting timedout instances
            if (not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty()):

                modifiedFlag = False
                # Option 1: instances from executionQueue need to continue to run, check if new instances have to be moved to executionQueue
                if (not arrivingQueue.empty()) and (not executionQueue.empty()):
                    if smallestInstanceRuntime(copyOfQueue(arrivingQueue)) < largestInstanceRuntime(copyOfQueue(executionQueue)):
                        modifiedFlag = True
                        AuxQueue = mergeQueues(executionQueue, arrivingQueue) #After merging, executionQueue and arrivingQueue become empty because they are sent by reference
                        while (executionQueue.qsize() < k) and (not AuxQueue .empty()):
                            auxInstance = AuxQueue.get()
                            executionQueue.put(auxInstance)
                        while  (not AuxQueue.empty()):
                            auxInstance = AuxQueue.get()
                            arrivingQueue.put(auxInstance)

                # Option 2:
                elif (arrivingQueue.empty()) and (not executionQueue.empty()):
                    modifiedFlag = False

                # Option 3:
                elif (not arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = True
                    while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
                        auxInstance = arrivingQueue.get()
                        executionQueue.put(auxInstance)

                # Option 4:
                elif (arrivingQueue.empty()) and (executionQueue.empty()):
                    modifiedFlag = False

                ###########
                if modifiedFlag == True and executionQueue.qsize()>1:
                    executionQueue = sortBySJF(executionQueue)
                    executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0

                if not executionQueue.empty():
                    QueuedInstance = executionQueue.get()
                    VMs = MIPbeginToProcessInstance_R_C(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)
                    vmID = getVMwithSmallestEndTime(VMs)

        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it only if predicted solvable
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime: # and (ArrivingInstance.PredictedSolvable != 0):
            arrivingQueue.put(ArrivingInstance)
            if heuristicH > 0:
                HeuristicEvaluateContinueToExecuteMIP_2Queues(executionQueue, arrivingQueue, simData, VMs,ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH,useClassification=False)
        elif (ArrivingInstance.PredictedSolvable != 0):
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)
        else:
            VMs = doNotProcessInstance(VMs, vmID, ArrivingInstance, simData)
        simData.to_csv(outputFile)


    #Finish to attend queued instances
    MIPRunTime = 0
    while not mergeQueues(copyOfQueue(arrivingQueue), copyOfQueue(executionQueue)).empty():
        vmID = getVMwithSmallestEndTime(VMs)
        arrivingQueue = deleteTimedOutInstances(arrivingQueue, VMs[vmID].nextEndTime + 1, simData, vmID)
        executionQueue = deleteTimedOutInstances(executionQueue, VMs[vmID].nextEndTime + 1, simData, vmID)

        modifiedFlag = False
        while (executionQueue.qsize() < k) and (not arrivingQueue.empty()):
            modifiedFlag = True
            auxInstance = arrivingQueue.get()
            executionQueue.put(auxInstance)

        if modifiedFlag == True and executionQueue.qsize() > 1:
            executionQueue = MIPupdateSchedule(executionQueue, outputFile, searchTime, GAPsize, instanceCapTime,getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
            MIPRunTime = findLastMIPRunTime(outputFile)

        if not executionQueue.empty():
            QueuedInstance = executionQueue.get()
            VMs = MIPbeginToProcessInstance_R_C(executionQueue, QueuedInstance, simData, VMs, vmID, instanceCapTime,MIPRunTime)

    sim = simData.sort_values(by=["TimeServiceBegins","TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim


##############################
##############################


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_1Queue(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, searchTime=120, GAPsize=0.1, model="model1", heuristicH=2, dequeueWhenNotScheduledMIP=0):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    simData["MIPnotScheduled"] = 0
    simData["MIPRunTime"] = 0
    simData["QueuedInstances"] = 0

    for index, row in simData.iterrows():

        vmID = getVMwithSmallestEndTime(VMs)
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy, VMs[vmID].nextEndTime + 1) #Create the instance
        MIPRunTime = 0
        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            ###########
            q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
            if not q.empty():
                if(q.qsize() > 1):
                    q = sortBySJF(q)
                    q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0
                ###########
                #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1+ round(MIPRunTime), simData, vmID, dequeueWhenNotScheduledMIP)
                if not q.empty():
                    QueuedInstance = q.get()
                    VMs = MIPbeginToProcessInstance_R(q, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)
                    vmID = getVMwithSmallestEndTime(VMs)

        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it because the system is idle
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            if heuristicH > 0:
                q = HeuristicEvaluateContinueToExecuteMIP_1Queue(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH, useClassification = False)
        else:
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)
        simData.to_csv(outputFile)
    #Finish to attend queued instances
    MIPRunTime = 0
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            if (q.qsize() > 1):
                q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                MIPRunTime = findLastMIPRunTime(outputFile)
            else:
                MIPRunTime = 0
            ###########
            #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1 + round(MIPRunTime), simData, vmID, dequeueWhenNotScheduledMIP)

            if not q.empty():
                QueuedInstance = q.get()
                VMs = MIPbeginToProcessInstance_R(q, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)

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


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification_1Queue(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, searchTime=120, GAPsize=0.1, model="model1", heuristicH=2, dequeueWhenNotScheduledMIP=0):
    simData = pd.read_csv(inputData, index_col=0)
    q = Queue.PriorityQueue()
    simData["MIPAttended"]=-1
    simData["Stopped"] = 0
    simData["MIPnotScheduled"] = 0
    simData["MIPRunTime"] = 0
    simData["QueuedInstances"] = 0

    for index, row in simData.iterrows():
        vmID = getVMwithSmallestEndTime(VMs)
        ArrivingInstance = assignPriorityForScheduling(index, row, schedulingPolicy, VMs[vmID].nextEndTime + 1)  # Create the instance
        MIPRunTime = 0
        # Attend queued instances until the actual instance arrival
        while not q.empty() and VMs[vmID].nextEndTime < ArrivingInstance.ArrivalTime:
            ###########
            q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
            if not q.empty():
                if (q.qsize() > 1):
                    q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0
                ###########
                #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1, simData, vmID, dequeueWhenNotScheduledMIP)

                if not q.empty():
                    QueuedInstance = q.get()
                    VMs = MIPbeginToProcessInstance_R_C(q, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)
                    vmID = getVMwithSmallestEndTime(VMs)
        # If the queue is not empty after simulation, then put the instance in the queue. Otherwise attend it only if predicted solvable
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime: # and (ArrivingInstance.PredictedSolvable != 0):
            q.put(ArrivingInstance)
            if heuristicH > 0:
                q = HeuristicEvaluateContinueToExecuteMIP_1Queue(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, heuristicH, useClassification = True)
        elif (ArrivingInstance.PredictedSolvable != 0):
            VMs = beginToProcessInstanceSystemIsIDLE(VMs, vmID, ArrivingInstance, simData, instanceCapTime)
        else:
            VMs = doNotProcessInstance(VMs, vmID, ArrivingInstance, simData)
        simData.to_csv(outputFile)
    #Finish to attend queued instances
    MIPRunTime = 0
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            if (q.qsize() > 1):
                q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData,model, len(VMs), VMs[vmID].nextEndTime + 1)
                MIPRunTime = findLastMIPRunTime(outputFile)
            else:
                MIPRunTime = 0
            ###########
            #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1 + round(MIPRunTime), simData, vmID, dequeueWhenNotScheduledMIP)

            if not q.empty():
                QueuedInstance = q.get()
                VMs = MIPbeginToProcessInstance_R_C(q, QueuedInstance, simData, VMs, vmID, instanceCapTime, MIPRunTime)

    sim = simData.sort_values(by=["TimeServiceBegins","TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim
