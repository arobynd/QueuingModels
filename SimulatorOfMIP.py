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

def HeuristicEvaluateContinueToExecuteMIP(queue, simData, VMs, ArrivingInstanceTime, instanceCapTime, stopWhenQueue, useClassification = False):
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
            #instance.priority = instance.PredictedServiceTime + nextEndTime
            instance.priority = instance.PredictedServiceTime + nextEndTime + instance.maximumWaitingTime
            #fix priorities according to the next end time and predicted service times
            #xxxxxxxxxxxxxxxxxxxx utilizar informacion sobre el tiempo de llegada....el tiempo de llegada y el tiempo maximo de espera y el tiempo actual
            #dan una buena idea de cuanto puede esperar una instancia
            #utilizar como ordenamiento la instancia que tenga menor tiempo para timeout
            finalQueue.put(instance)

    return finalQueue


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




def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1", stopWhenQueue=2, dequeueWhenNotScheduledMIP=0):
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

                #Execute MIP every groupSize arriving Instances...To update priorities
                if (index % groupSize == 0):
                    if(q.qsize() > 1):
                        q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                        MIPRunTime = findLastMIPRunTime(outputFile)
                    else:
                        MIPRunTime = 0
                    ###########
                    #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1+ round(MIPRunTime), simData, vmID, dequeueWhenNotScheduledMIP)
                else:
                    MIPRunTime = 0


                if not q.empty():
                    QueuedInstance = q.get()
                    simData.loc[QueuedInstance.ID, "MIPRunTime"] = MIPRunTime
                    simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                    simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime)
                    simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) - QueuedInstance.ArrivalTime
                    simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                    simData.loc[QueuedInstance.ID, "VM"] = vmID


                    if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
                        simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) + QueuedInstance.RealServiceTime
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
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()
        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime:
            q.put(ArrivingInstance)
            ###########
            q = HeuristicEvaluateContinueToExecuteMIP(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue, useClassification = False)

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


    #Finish to attend queued instances
    MIPRunTime = 0
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            # Execute MIP every groupSize arriving Instances...To update priorities
            if (index % groupSize == 0):
                if (q.qsize() > 1):
                    q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0
                ###########
                #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1 + round(MIPRunTime), simData, vmID, dequeueWhenNotScheduledMIP)
            else:
                MIPRunTime = 0

            if not q.empty():
                QueuedInstance = q.get()
                simData.loc[QueuedInstance.ID, "MIPRunTime"] = MIPRunTime
                simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime)
                simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) - QueuedInstance.ArrivalTime
                simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                simData.loc[QueuedInstance.ID, "VM"] = vmID

                if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
                    simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) + QueuedInstance.RealServiceTime
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


def MIPsimulateInstanceArrivals_HeuristicStrategy_Regression_Classification(inputData, outputFile, VMs, schedulingPolicy, instanceCapTime, groupSize=5, searchTime=120, GAPsize=0.1, model="model1", stopWhenQueue=2, dequeueWhenNotScheduledMIP=0):
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

                #Execute MIP every groupSize arriving Instances...To update priorities
                if (index % groupSize == 0):
                    if (q.qsize() > 1):
                        q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData, model, len(VMs), VMs[vmID].nextEndTime + 1)
                        MIPRunTime = findLastMIPRunTime(outputFile)
                    else:
                        MIPRunTime = 0
                    ###########
                    #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1, simData, vmID, dequeueWhenNotScheduledMIP)
                else:
                    MIPRunTime = 0

                if not q.empty():

                    QueuedInstance = q.get()
                    simData.loc[QueuedInstance.ID, "MIPRunTime"] = MIPRunTime
                    simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                    simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime)
                    simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) - QueuedInstance.ArrivalTime
                    simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                    simData.loc[QueuedInstance.ID, "VM"] = vmID

                    if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
                        simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) + QueuedInstance.RealServiceTime
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
        #simData.loc[ArrivingInstance.ID, "QueuedInstances"] = q.qsize()

        vmID = getVMwithSmallestEndTime(VMs)
        if VMs[vmID].nextEndTime >= ArrivingInstance.ArrivalTime: # and (ArrivingInstance.PredictedSolvable != 0):
            q.put(ArrivingInstance)
            q = HeuristicEvaluateContinueToExecuteMIP(q, simData, VMs, ArrivingInstance.ArrivalTime, instanceCapTime, stopWhenQueue, useClassification = True)
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

    #Finish to attend queued instances
    MIPRunTime = 0
    while not q.empty():
        vmID = getVMwithSmallestEndTime(VMs)
        q = deleteTimedOutInstances(q, VMs[vmID].nextEndTime + 1, simData, vmID)
        if not q.empty():
            # Execute MIP every groupSize arriving Instances...To update priorities
            if (index % groupSize == 0):
                if (q.qsize() > 1):
                    q = MIPupdateSchedule(q, outputFile, searchTime, GAPsize, instanceCapTime, getVM_CSV(VMs), simData,model, len(VMs), VMs[vmID].nextEndTime + 1)
                    MIPRunTime = findLastMIPRunTime(outputFile)
                else:
                    MIPRunTime = 0
                ###########
                #q = HeuristicDeleteWhenNotScheduledMIP(q, VMs[vmID].nextEndTime + 1 + round(MIPRunTime), simData, vmID, dequeueWhenNotScheduledMIP)
            else:
                MIPRunTime = 0

            if not q.empty():
                QueuedInstance = q.get()
                simData.loc[QueuedInstance.ID, "MIPRunTime"] = MIPRunTime
                simData.loc[QueuedInstance.ID, "QueuedInstances"] = q.qsize() + 1
                simData.loc[QueuedInstance.ID, "TimeServiceBegins"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime)
                simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) - QueuedInstance.ArrivalTime
                simData.loc[QueuedInstance.ID, "IdleTimeOfServer"] = 0
                simData.loc[QueuedInstance.ID, "VM"] = vmID

                if (simData.loc[QueuedInstance.ID, "WaitingTimeInQueue"] < simData.loc[QueuedInstance.ID, "maximumWaitingTime"]) and (QueuedInstance.PredictedSolvable != 0) and (simData.loc[QueuedInstance.ID, "MIPAttended"] != 0):
                    simData.loc[QueuedInstance.ID, "TimeServiceEnds"] = VMs[vmID].nextEndTime + 1 + round(MIPRunTime) + QueuedInstance.RealServiceTime
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

    sim = simData.sort_values(by=["TimeServiceBegins","TimeServiceEnds"], ascending=[True, True])
    sim.to_csv(outputFile)
    print "\nChecking for solution consistency"
    if CheckConsistency(outputFile, instanceCapTime):
        print "Consistent solution"
    else:
        print "Inconsistent solution"

    return sim
