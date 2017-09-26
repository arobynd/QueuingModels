class Instance:
    def __init__(self, ID, RealServiceTime, PredictedServiceTime, ArrivalTime, RealSolvable, PredictedSolvable, maximumWaitingTime, priority):
        self.ID = ID
        self.RealServiceTime = RealServiceTime
        self.PredictedServiceTime = PredictedServiceTime
        self.ArrivalTime = ArrivalTime
        self.RealSolvable = RealSolvable
        self.PredictedSolvable = PredictedSolvable
        self.maximumWaitingTime = maximumWaitingTime
        self.priority = priority


    #This method lets a queue sort instances by default in ascending order by a given priority
    # (from lowest to highest value)
    def __cmp__(self, other):
        return self.priority > other.priority

    def __str__(self):
        return "instance(ID:" + str(self.ID) + \
               ", realServiceTime:" + str(self.RealServiceTime) + \
               ", predictedTime:" + str(self.PredictedServiceTime) + \
               ", arrivalTime:" + str(self.ArrivalTime) + \
               ", RealSolvable:" + str(self.RealSolvable) + \
               ", PredictedSolvable:" + str(self.PredictedSolvable) + \
               ", maximumWaitingTime:" + str(self.maximumWaitingTime) + \
               ", priority:" + str(self.priority) + \
               ")"



#Usage Sample:
# When an instance is queued, then it's automatically ordered according to the given priority because of
# the method __cmp___. In this case, they are queued from lowest to highest value.


#
# import Queue
#
#
# def updatePrioritiesMIP(queue):
#     auxQueue = Queue.PriorityQueue()
#     while not queue.empty():
#         instance=queue.get()
#         print instance
#         auxQueue.put(instance)
#     return auxQueue
#
# q = Queue.PriorityQueue()
# q.put(Instance(0,0,0,0,0,0,0,10))
# q.put(Instance(0, 0, 0, 0,0,0,0, -5))
# q.put(Instance(0, 0, 0, 0,0,0,0, -15))
# q.put(Instance(0, 0, 0, 0,0,0,0, -7))
# q.put(Instance(0, 0, 0, 0,0,0,0, 7))
# q.put(Instance(0, 0, 0, 0,0,0,0, 7))
# print q.qsize()
# q=updatePrioritiesMIP(q)
# print q.qsize()




