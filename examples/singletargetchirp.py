# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import sys
import t9ek80

class ek80(t9ek80.t9ek80):
    def __init__(self):
        super(ek80, self).__init__()

#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate):
    
        # If single target chirp mode...
        if mtype == "SingleTargetChirp":
            print("------------------------------")
            print("SingleTargetChirp");
            for element in Payload:
                print("Time:    {:s}   Depth:   {:f}   Forward: {:f}   Side:    {:f}   Sa:      {:f}"\
                    .format(timenow,element[0],element[3],element[4],element[5]))

#----------------------------------------------------------------------------
# The main code....
run = ek80()
run.main(sys.argv)


