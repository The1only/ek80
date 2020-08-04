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
import multiprocessing as mp

class ek80(t9ek80.t9ek80):
    def __init__(self, argv):
        super(ek80, self).__init__(argv)
        
        self.plot_pipe, plotter_pipe = mp.Pipe()
        self.plotter = ProcessPlotter()
        self.plot_process = mp.Process(
            target=self.plotter, args=(plotter_pipe,), daemon=True)
        self.plot_process.start()
    
    def getDebug(self):
        return False
    
#----------------------------------------------------------------------------
#   Method       report
#   Description  User defined REPORT function, this is to be adapter to individual needs.
#                It receives a list for parameters and meta data to process...
#-----------------------------------------------------------------------------
    def report(self, Payload, Decode, timenow, mtype, desimate):
        # If NoiseSpectrum mode...
        if mtype == "NoiseSpectrum":
            send = self.plot_pipe.send
            t = np.arange(0.0, len(Payload)-1, 1)
            send([t,Payload[1:]])

#----------------------------------------------------------------------------

# As we now are in a different process we must do this trick to be alowed to plot...
class ProcessPlotter(object):
    def __init__(self):
        self.x = []
        self.y = []

    def terminate(self):
        plt.close('all')

    def call_back(self):
        while self.pipe.poll():
            command = self.pipe.recv()
            if command is None:
                self.terminate()
                return False
            else:
                self.x = command[0]
                self.y = command[1]
                self.ax.clear()
                self.ax.plot(self.x, self.y) #, 'ro')
        self.fig.canvas.draw()
        return True

    def __call__(self, pipe):
        self.pipe = pipe
        self.fig, self.ax = plt.subplots()
        timer = self.fig.canvas.new_timer(interval=100)
        timer.add_callback(self.call_back)
        timer.start()
        plt.show()

#----------------------------------------------------------------------------
# The main code....
#if plt.get_backend() == "MacOSX":
#    mp.set_start_method("forkserver")
run = ek80(sys.argv)
run.main()



