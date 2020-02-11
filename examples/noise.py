# ----------------------------------------------------------------------------
#    Method       EK80 generic v1.0
#    Description  Subscribes to EK80 data depending on the config.xml file and report data.
#                 Comunicate with the EK80/EK60/EK15
#    By:          Kongsberg Maritime AS, Terje Nilsen 2020
#-----------------------------------------------------------------------------
import sys
import t9ek80
import matplotlib.pyplot as plt
import numpy as np

class ek80(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80, self).__init__(argv)
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
        # If NoiseSpectrum mode...
        if mtype == "NoiseSpectrum":
            plt.clf()
            t = np.arange(0.0, len(Payload)-1, 1)
            plt.plot(t,Payload[1:])
            plt.rcParams['axes.unicode_minus'] = True
            plt.title('About as simple as it gets, folks')
            plt.pause(0.05)
            
#----------------------------------------------------------------------------
# The main code....
run = ek80(sys.argv)
run.main()


