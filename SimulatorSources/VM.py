class VM:
    """A class that defines virtual machine characteristics"""

    def __init__(self, ID, processingInstanceID, nextEndTime):
        self.ID = ID
        self.processingInstanceID = processingInstanceID
        self.nextEndTime = nextEndTime

    def __str__(self):
        return "VM(ID: " + str(self.ID) + ", nextEndTime: " + str(self.nextEndTime) + ", processingInstance: " + str(
            self.processingInstanceID) + ")"



###################################################
##
##class VM:
##    """A simple class that defines virtual machine characteristics"""
##    class_counter= 0
##    def __init__(self, processingInstanceID, nextEndTime):
##        self.ID= VM.class_counter
##        VM.class_counter += 1
##        self.processingInstanceID = processingInstanceID
##        self.nextEndTime = nextEndTime
##
##    def __str__(self):
##        return  "VM(ID: " + str(self.ID) + ", nextEndTime: " + str(self.nextEndTime) + ", processingInstance: " + str(self.processingInstanceID) + ")"

