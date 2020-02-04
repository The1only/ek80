# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import sys
import t9ek80
import math

class ek80(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80, self).__init__(argv)
        self.lat  = 0.0
        self.lon  = 0.0
        self.nmea = False

#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate, transponder, unit, product):
        # If biomass mode and we got our position...
        if mtype == "Biomass" and self.nmea == True:
            print("Product: {:s} Unit: {:s} Transponder: {:s} Bimass: {:f} at time: {:s} at location: lat: {:f} lon: {:f}".format(product, unit, transponder, Payload[1],timenow, self.lat,self.lon))

#----------------------------------------------------------------------------
#    Method       EK80_data
#   Description   The NMEA subscription data handler...
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
# The main code....
run = ek80(sys.argv)
run.main()
print("Done!")


