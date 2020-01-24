# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import sys
import t9ek80
import math
import matplotlib.pyplot as plt
import numpy as np

class ek80(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80, self).__init__(argv)
        self.lat  = 10.492231
        self.lon  = 59.375803
        self.count= 0

#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate):
    
        # If single target chirp mode...
        if mtype == "Echogram" and (self.count % desimate) == 0:
            Payload = Payload[3:]
            plt.clf()
            t = np.arange(0.0, len(Payload), 1)
            plt.plot(t,Payload)
            plt.rcParams['axes.unicode_minus'] = True
            plt.title('About as simple as it gets, folks')
            plt.pause(0.05)
            
#            print("------------------------------")
#            print("Echogram");
#            print("Time:    {:s}   Range:   {:f}   RangeStart: {:f} Position: Lat: {:f} Lon: {:f}".format(timenow,Payload[1],Payload[2],self.lat,self.lon))

#            Payload = Payload[3:]
#            print("Bio1: {:f} Bio2: {:f} Bio3: {:f} Bio4: {:f} Bio5: {:f} Bio6: {:f} Bio7: {:f} Bio8: {:f} Bio9: {:f} Bio10: {:f}"\
#                .format(Payload[0],Payload[1],Payload[2],Payload[3],Payload[4],Payload[5],Payload[6],Payload[7],Payload[8],Payload[9]))

        self.count+=1

#----------------------------------------------------------------------------
#    Method       EK80_data
#   Description   The subscription data handler...
#                 Data is parsed according to the XML file...
#-----------------------------------------------------------------------------

    def NMEAdecode(self,data):

        # Only parse position...
        if data[0:6].decode() == "$INGLL":
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
# The main code....
run = ek80(sys.argv)
run.main()
print("Done!")


