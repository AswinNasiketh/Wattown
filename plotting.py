import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading

class PowerGraph():

    def __init__(self):
        self.solarPower = 0
        self.windPower = 0
        self.hydroPower = 0
        self.indicies = [1, 2, 3]
        self.barLabels = ["Solar Power", "Wind Power", "Hydro Power"]
        self.xlabel = "Power Source"
        self.ylabel = "Power Generated/Consumed this hour (GW)"
        self.title = "Renewable Energy Generation"

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


    def setupFigure(self, figure):
        self.fig = figure
        self.ax = self.fig.add_subplot(3,1,1)
        self.ax.set_ylim([self.minPower,self.maxPower])

        self.bars = self.ax.bar(self.indicies, [self.solarPower, self.windPower, self.hydroPower])
        self.ax.set_xticks(self.indicies)
        self.ax.set_xticklabels(self.barLabels)
        self.ax.set_xlabel(self.xlabel)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.title)
        

    def setPowers(self, solarPower, windPower, hydroPower):
        self.solarPower = solarPower
        self.windPower = windPower
        self.hydroPower = hydroPower


class ConsumptionSupplyGraph():
    
    def __init__(self):
        self.consumption = 0
        self.renewableSupply = 0
        self.renewableSurplus = 0
        self.indicies = [1, 2, 3]
        self.barLabels = ["City Consumption", "Renewable Supply ", "Renewable Surplus"]
        self.ylabel = "Power (GW)"
        self.title = "Supply and Demand"

    def configure(self, maxPower, minPower):
        self.maxPower = maxPower
        self.minPower = minPower

    def setupFigure(self, figure):
        self.fig = figure
        self.ax = self.fig.add_subplot(3,1,2)
        self.ax.set_ylim([self.minPower,self.maxPower])

        self.bars = self.ax.bar(self.indicies, [self.consumption, self.renewableSupply, self.renewableSurplus])
        self.bars[0].set_color('r')
        self.ax.set_xticks(self.indicies)
        self.ax.set_xticklabels(self.barLabels)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.title)

    def animate(self):
        self.renewableSurplus = self.renewableSupply + self.consumption #consumption is negative always
        self.bars[0].set_height(self.consumption)
        self.bars[1].set_height(self.renewableSupply)
        self.bars[2].set_height(self.renewableSurplus)

        if self.renewableSurplus < 0:
            self.bars[2].set_color('r')
        else:
            self.bars[2].set_color('g')

      

    def setConsumption(self, consumption):
        self.consumption = -consumption

    def setRenewableSupply(self, supply):
        self.renewableSupply = supply

class StoredEnergyGraph():

    def __init__(self):
        self.reservoirEnergy = 0
        self.batteryEnergy = 0

        self.barLabels = ["Battery", "Reservoir"]
        self.xlabel = "Energy Storage System"
        self.ylabel = "Energy Remaining (GWh)"
        self.title = "Energy Storage"

        self.indicies = [1,2]

    def setupFigure(self, figure):
        self.fig = figure
        self.ax = self.fig.add_subplot(3,1,3)

    #different to others because we don't know the maximum reservoir energy
    def animate(self):
        self.ax.clear()
        self.bars = self.ax.bar(self.indicies, [self.batteryEnergy, self.reservoirEnergy])
        self.bars[0].set_color('b')
        self.bars[1].set_color('y')
        self.ax.set_xticks(self.indicies)
        self.ax.set_xticklabels(self.barLabels)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.title)


    def setRemainingEnergies(self, batteryEnergy, reservoirEnergy):
        self.batteryEnergy = batteryEnergy
        self.reservoirEnergy = reservoirEnergy