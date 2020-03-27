# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import sys
import t9ek80

class ek80(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80, self).__init__(argv)

#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate, transponder, unit, product):
        print(Payload)
        if mtype == "Set_Param" and self.nmea == True:
            print("Set_Param: {:f} at time: {:s} at location: lat: {:d} lon: {:d}".format(Payload[1],timenow, self.lat,self.lon))
            
#-----------------------------------------------------------------------------
# The main code....
run = ek80(sys.argv)
run.main()
print("Done!")


