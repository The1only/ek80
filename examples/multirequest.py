# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import sys
import t9ek80
import math
#import matplotlib.pyplot as plt
import numpy as np
import threading
import time

#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class ek80(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80, self).__init__(argv)
        self.biomas = 0
        
#-----------------------------------------------------------------------------
# Override the function getDebug, defaut if no overide is False. 
    def getDebug(self):
        return False
#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate, transponder, unit, product):
        # If biomass mode and we got our position...
        if mtype == "Integration":
            self.biomas = Payload[1]
 #           print("Product: {:s} Unit: {:s} Transponder: {:s} Bimass: {:f} at time: {:s} at location: lat: {:f} lon: {:f}".format(product, unit, transponder, Payload[1],timenow, self.lat,self.lon))
            
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class ek80_1(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80_1, self).__init__(argv)
        self.depth = 0
        
#-----------------------------------------------------------------------------
# Override the function getDebug, defaut if no overide is False. 
    def getDebug(self):
        return False
#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate, transponder, unit, product):
        # If biomass mode and we got our position...
        if mtype == "BottomDetection":
            self.depth = Payload[1]
 #           print("Product: {:s} Unit: {:s} Transponder: {:s} Bimass: {:f} at time: {:s} at location: lat: {:f} lon: {:f}".format(product, unit, transponder, Payload[1],timenow, self.lat,self.lon))
            
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------

class ek80_2(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80_2, self).__init__(argv)
        self.lat  = 0.0
        self.lon  = 0.0
        self.count= 0
        self.nmea = False
        self.biomas = 0
        self.depth = 0

#-----------------------------------------------------------------------------
# Override the function getDebug, defaut if no overide is False. 
    def getDebug(self):
        return False

#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate, transponder, unit, product):
    
        # If single target chirp mode...
        if desimate == 0: desimate = 1  # Avoid divide by zero...
        if mtype == "Echogram" and (self.count % desimate) == 0 and self.nmea == True:
            
            # Payload = Payload[3:]
            # plt.clf()
            # t = np.arange(0.0, len(Payload), 1)
            # plt.plot(t,Payload)
            # plt.rcParams['axes.unicode_minus'] = True
            # plt.title('About as simple as it gets, folks')
            # plt.pause(0.05)
            
            print("------------------------------")
            print("Product: {:s} Unit: {:s} Transponder: {:s}".format(product, unit, transponder))
            print("Bimass:  {:f}".format(self.biomas))
            print("Depth:   {:f}".format(self.depth))
            print("Time:    {:s}   Range:   {:f}   RangeStart: {:f} Position: Lat: {:f} Lon: {:f}".format(timenow,Payload[1],Payload[2],self.lat,self.lon))

            print("\nEchogram");
            Payload = Payload[3:]
            print("Bio1: {:f} Bio2: {:f} Bio3: {:f} Bio4: {:f} Bio5: {:f} Bio6: {:f} Bio7: {:f} Bio8: {:f} Bio9: {:f} Bio10: {:f}"\
               .format(Payload[0],Payload[1],Payload[2],Payload[3],Payload[4],Payload[5],Payload[6],Payload[7],Payload[8],Payload[9]))

            print("------------------------------")

        self.count+=1

#----------------------------------------------------------------------------
#    Method       EK80_data
#   Description   The subscription data handler...
#                 Data is parsed according to the XML file...
#-----------------------------------------------------------------------------

    def NMEAdecode(self,data):

      # Only parse position...
        if data[0:6].decode() == "$INGLL":
            self.nmea = True
            info = data.decode().split(",")
            
            x = float(info[1])
            d = math.floor(x / 100)
            m = ( math.floor(x)-(d*100))/60
            s = (x-math.floor(x))/60
            self.lon = d+m+s

            y = float(info[3])
            d = math.floor(y / 100)
            m = ( math.floor(y)-(d*100))/60
            s = (y-math.floor(y))/60
            self.lat = d+m+s
            
#-----------------------------------------------------------------------------
#-----------------------------------------------------------------------------
# PS: Remember that if you use NMEA, then every instance of t9ek80 will take one port eatch...
# Normally set NMEA port to 0 for Biomass and Bottom, and 20001 for Echogram in this test...

print(sys.argv)
# The main code....

# if len(sys.argv) >= 5:
    # r1 = [sys.argv[0]]+[sys.argv[1]]+[sys.argv[4]]
    # r2 = [sys.argv[0]]+[sys.argv[2]]+[sys.argv[4]]
    # r3 = [sys.argv[0]]+[sys.argv[3]]+[sys.argv[4]]
# elif len(sys.argv) >= 4:
    # r1 = [sys.argv[0]]+[sys.argv[1]]
    # r2 = [sys.argv[0]]+[sys.argv[2]]
    # r3 = [sys.argv[0]]+[sys.argv[3]]
# else:
    # print("Usage: python3 multuirequest.py file1.xml file2.xml [Transponder]")
    # print("Example: python3 multirequest.py bimoas.xml echogram.xml 0")

r1 = ['multirequest','biomass.xml','0']
r2 = ['multirequest','bottom.xml','0']
r3 = ['multirequest','echogram.xml','0']


run = ek80(r1)
run_1 = ek80_1(r2)
run_2 = ek80_2(r3)

thread1= threading.Thread(target = run.main)
thread1.start()

thread2= threading.Thread(target = run_1.main)
thread2.start()

thread3= threading.Thread(target = run_2.main)
thread3.start()

while thread1.isAlive():
    run_2.biomas = run.biomas
    run_2.depth = run_1.depth
    time.sleep(0.1)
    
while thread2.isAlive():
    time.sleep(5)

print("Done!")


