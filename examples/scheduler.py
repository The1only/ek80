# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import sys
import glob
import shutil
import time
import os
import datetime as dt

from t9ek80 import t9ek80 as ek

src = r'/mnt/z/*.*'
dest_dir = '/mnt/c/edge/in/EK80Raw'
#-----------------------------------------------------------------------------
class ek80(ek.t9ek80):
    def __init__(self, argv):
        super(ek80, self).__init__(argv)

    # Override the function getDebug, defaut if no overide is False. 
    def getDebug(self):
        return False #True

#-----------------------------------------------------------------------------
print('Scheduler running...')

while 1:
    # For every 4 hour....
    print('Waiting for next run...')
    while (dt.datetime.now().hour % 4) != 0:
        time.sleep(30)
        
    run = ek80(['','startrecording.xml','0'])
    run.main()
    
    print('Recording...')
    # Record for 10 minutes...
    time.sleep(60*10)

    run = ek80(['','stoprecording.xml','0'])
    run.main()

    # Copy and remove files (we need the files comming from another computer to be stored on the local one-drive).
    for file in glob.glob(src): 
        print(file)
        shutil.copy(file, dest_dir)
        os.remove(file)

    print('Getting ready for next run...')
    while (dt.datetime.now().hour % 4) == 0:
        time.sleep(30)
