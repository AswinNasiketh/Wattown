import matplotlib as mpl
import matplotlib.pyplot as plt
import multiprocessing as mp

class GraphsProcessManager():
    def __init__(self):
        self.powerDataPipeIn, self.powerDataPipeOut = mp.Pipe()
        self.consDataPipeIn, self.consDataPipeOut = mp.Pipe()
        self.storageDataPipeIn, self.storageDataPipeOut = mp.Pipe()
        self.controlDataPipeIn, self.controlDataPipeOut = mp.Pipe()

        self.plotProcessObj = GraphsProcess()

    def configure(self, maxPower, minPower, maxCons, minCons):
        self.plotProcessObj.configure(maxPower, minPower, maxCons, minCons)
    
    def startPlotting(self):
        self.plotProcess = mp.Process(
            target = self.plotProcessObj,
            args=(self.powerDataPipeOut, self.consDataPipeOut, self.storageDataPipeOut, self.controlDataPipeOut),
            daemon = True
        )
        self.plotProcess.start()

    def setSupplyDemand(self, renewableSupply, consumption):
        self.consDataPipeIn.send((consumption, renewableSupply))

    def setRenewablePowers(self, solar, wind, hydro):
        self.powerDataPipeIn.send((solar, wind, hydro))

    def setStoredEnergy(self, battery, reservoir):
        self.storageDataPipeIn.send((battery, reservoir))

    def stopPlotting(self):
        self.controlDataPipeIn.send(1)
        self.plotProcess.terminate()
        self.plotProcess.join(timeout = 1.0)

    def hidePlots(self):
        self.controlDataPipeIn.send(2)

    def showPlots(self):
        self.controlDataPipeIn.send(3)

class GraphsProcess():

    def __init__(self):
        self.powerPlotter  = PowerGraph()
        self.consPlotter = ConsumptionSupplyGraph()
        self.storagePlotter = StoredEnergyGraph()
        self.plotVisible = True

    def configure(self, maxPower, minPower, maxCons, minCons):
        self.powerPlotter.configure(maxPower, minPower)
        self.consPlotter.configure(maxCons, minCons)

    def __call__(self, powerDataPipe, consDataPipe, storageDataPipe, controlDataPipe):
        print("starting Graphs Process")
        self.powerDataPipe = powerDataPipe
        self.consDataPipe = consDataPipe
        self.storageDataPipe = storageDataPipe
        self.controlDataPipe = controlDataPipe


        self.fig = plt.figure(figsize=(8, 9), dpi=80)
        plt.subplots_adjust(hspace=0.4)

        self.powerPlotter.setupFigure(self.fig)
        self.consPlotter.setupFigure(self.fig)
        self.storagePlotter.setupFigure(self.fig)

        timer = self.fig.canvas.new_timer(interval = 250)
        timer.add_callback(self.timerCallback)
        timer.start()

        plt.show()

    def terminate(self):
        plt.close('all')

    def timerCallback(self):

        if self.controlDataPipe.poll():
            command = self.controlDataPipe.recv()
            if command == 1:
                self.terminate()
                return False
            elif command == 2:
                self.plotVisible = False
                self.fig.set_visible(False)
            elif command == 3:
                self.plotVisible = True
                self.fig.set_visible(True)

            if not self.plotVisible:
                return True

        if self.powerDataPipe.poll():
            solarPower, windPower, hydroPower = self.powerDataPipe.recv()
            self.powerPlotter.setPowers(solarPower, windPower, hydroPower)
        
        if self.consDataPipe.poll():
            consumption, renewableSupply = self.consDataPipe.recv()
            self.consPlotter.setConsumption(consumption)
            self.consPlotter.setRenewableSupply(renewableSupply)
        
        if self.storageDataPipe.poll():
            batteryEnergy, reservoirEnergy = self.storageDataPipe.recv()
            self.storagePlotter.setRemainingEnergies(batteryEnergy, reservoirEnergy)

        self.powerPlotter.animate()
        self.consPlotter.animate()
        self.storagePlotter.animate()

        self.fig.canvas.draw()
        return True

class PowerGraph():

    def __init__(self):
        self.solarPower = 0
        self.windPower = 0
        self.hydroPower = 0
        self.indicies = [1, 2, 3]
        self.barLabels = ["Solar Power", "Wind Power", "Hydro Power"]
        self.ylabel = "Power Generated/Consumed (GW)"
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
        self.barLabels = ["City Consumption", "Renewable Supply ", "Renewable Surplus/Shortage"]
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
        self.bars[0].set_color('y')
        self.bars[1].set_color('b')
        self.ax.set_xticks(self.indicies)
        self.ax.set_xticklabels(self.barLabels)
        self.ax.set_ylabel(self.ylabel)
        self.ax.set_title(self.title)


    def setRemainingEnergies(self, batteryEnergy, reservoirEnergy):
        self.batteryEnergy = batteryEnergy
        self.reservoirEnergy = reservoirEnergy