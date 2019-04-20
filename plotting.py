import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

class PowerGraphs():

    def __init__(self):
        self.solarPower = 0
        self.windPower = 0
        self.hydroPower = 0
        self.indicies = [1, 2, 3]
        self.labels = ["Solar Power", "Wind Power", "Hydro Power"]

    def configure(self, maxPower, minPower):
        self.maxPower = maxPower
        self.minPower = minPower

    def animate(self):
        self.bars[0].set_height(self.solarPower)
        self.bars[1].set_height(self.windPower)
        self.bars[2].set_height(self.hydroPower)

        if self.hydroPower < 0:
            self.bars[2].set_color('r')
        else:
            self.bars[2].set_color('b')

        plt.pause(0.001)

    def setupFigure(self):
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(1,1,1)
        self.ax.set_ylim([self.minPower,self.maxPower])

        self.bars = self.ax.bar(self.indicies, [self.solarPower, self.windPower, self.hydroPower])
        self.ax.set_xticks(self.indicies)
        self.ax.set_xticklabels(self.labels)
        self.ax.set_xlabel("Power Source")
        self.ax.set_ylabel("Power Generation this hour (GW)")
        

    def setPowers(self, solarPower, windPower, hydroPower):
        self.solarPower = solarPower
        self.windPower = windPower
        self.hydroPower = hydroPower