######################################
# Generic Logging class
# Author: Bilal Al-Shahwany
# Date: 2016-05-02
#
import time
import inspect
import Constants

class Log:
    def __init__(self, writeFlag):
        constants = Constants.Constants()
        fileName=constants.LOGPATH
        self.logObj = open(fileName, writeFlag)
        self.printToConsole=True

    def __del__ (self):
        self.logObj.close()

    def OpenFile(self, fileName, writeFlag):
        self.logObj = open(fileName,writeFlag)
        
    def Debug(self, logLine):
        self.logObj.write("DEBUG "+time.strftime("%Y-%m-%d %H:%M:%S")+":" + inspect.stack()[1][3] + "," + str(inspect.stack()[1][2]) + "::" + logLine+'\n' ) 
        self.logObj.flush()
        if self.printToConsole:
            print ("DEBUG "+time.strftime("%Y-%m-%d %H:%M:%S")+":" + inspect.stack()[1][3] + "," + str(inspect.stack()[1][2]) + "::" + logLine)
        
    def Error(self, logLine):
        self.logObj.write("ERROR "+time.strftime("%Y-%m-%d %H:%M:%S")+":" + inspect.stack()[1][3] + "," + str(inspect.stack()[1][2]) + "::" + logLine+'\n' )
        for st in inspect.stack():
            self.logObj.write("Called From "+st[1] + ", Method:" +st[3] + ", Line:" + str(st[2])+"\n") 
        self.logObj.flush()
        if self.printToConsole:
            print ("ERROR "+time.strftime("%Y-%m-%d %H:%M:%S")+":" + inspect.stack()[1][3] + "," + str(inspect.stack()[1][2]) + "::" + logLine)
