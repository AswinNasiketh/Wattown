from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import threading
import time
from gameMode import GameMode

class MainWindow(Frame):
    
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.taskRunning = False
        self.initWindow()

    def initWindow(self):

        self.master.title("Wattown Board Controller")

        self.pack(fill=BOTH, expand =1)

        self.statusLabel = Label(self, text = "Status = Idle")
        self.statusLabel.pack(fill = X, expand = 1)

        self.interactiveModeButton = Button(self, text = "Start interactive mode")
        self.interactiveModeButton.pack(fill=X, expand =1)

        self.dailyCycleModeButton = Button(self, text = "Start Daily Cycle Mode")
        self.dailyCycleModeButton.pack(fill = X, expand =1)

        self.gameModeButton = Button(self, text = "Start Game Mode")
        self.gameModeButton.pack(fill = X, expand =1)

        stopButton = Button(self, text = "Stop Current Activity", command = self.stopCurrentActivity)
        stopButton.pack(fill = X, expand =1)

    def setInteractiveBtnCommand(self, interactiveButtonFunction):
        self.interactiveModeButton.configure(command = interactiveButtonFunction)
    
    def setDailyCylceBtnCommand(self, dailyCylcleButtonFunction):
        self.dailyCycleModeButton.configure(command = dailyCylcleButtonFunction)

    def setGameBtnCommand(self, gameButtonCommand):
        self.gameModeButton.configure(command = gameButtonCommand)


    def stopCurrentActivity(self):
        print("stopping activity")
        self.taskRunning = False
        self.statusLabel.configure(text = "Status: Idle")

    def getTaskRunning(self): #TODO: use this as global safety to not run two tasks at the same time
        return self.taskRunning        
    
    def setTaskRunning(self, taskRunning, taskDescription = "Idle"):
        self.taskRunning = taskRunning
        if taskRunning:
            self.statusLabel.configure(text = "Status: Running " + taskDescription)
        else:
            self.statusLabel.configure(text = "Status: Idle")
     
class CycleModeControlsWindow(Frame):

    def __init__(self, master, simulation, mainWindow):
        Frame.__init__(self, master)
        self.master = master
        self.simulation = simulation
        self.mainWindow = mainWindow
        self.initWindow()
        
    def initWindow(self):
        self.master.title("Cycle parameters")

        self.pack(fill=BOTH, expand = 1)

        self.addWindControls()
        self.addSolarControls()
        
        numLoopsEntryContainer = Frame(self)
        
        numLoopsLabel = Label(numLoopsEntryContainer, text="Number of days: ")
        numLoopsLabel.pack(side = LEFT)
        
        self.numLoops = StringVar()        
        numLoopsEntry = Entry(numLoopsEntryContainer, textvariable = self.numLoops)
        numLoopsEntry.pack(side = LEFT)
        
        numLoopsEntryContainer.pack(padx = 8, pady = 8)

        startBtn = Button(self, text = "Start Simulation", command = self.startSimBtnCallback)
        startBtn.pack(padx= 8, pady = 8)
    
    def addSolarControls(self):

        solarControlContainer = Frame(self)

        Label(solarControlContainer, text="Sunlight control").pack()

        typeOfDayContainer = Frame(solarControlContainer)

        typeOfDayLabel = Label(typeOfDayContainer, text="Type of Day: ")
        typeOfDayLabel.pack(side=LEFT)

        typeOfDayOptions = ["Sunny", "Cloudy"]
        self.typeOfDaySelected = StringVar()

        typeOfDayDropdown = Combobox(typeOfDayContainer, textvariable=self.typeOfDaySelected, values = typeOfDayOptions)
        typeOfDayDropdown.pack(side = LEFT)

        typeOfDayContainer.pack(pady = 4)

        daylightHoursContainer = Frame(solarControlContainer)

        daylightHoursLabel = Label(daylightHoursContainer, text = "Daylight hours (<23)")
        daylightHoursLabel.pack(side = LEFT)

        self.daylightHoursVar = StringVar()
        self.daylightHoursVar.set("12")

        daylightHoursEntry = Entry(daylightHoursContainer, textvariable=self.daylightHoursVar)
        daylightHoursEntry.pack(side = LEFT)

        daylightHoursContainer.pack(pady=4)

        solarControlContainer.pack(pady= 8, padx = 8)

    def addWindControls(self):
        windControlsContainer = Frame(self)

        Label(windControlsContainer, text="Wind control").pack()

        windPresentContainer = Frame(windControlsContainer)      

        self.windPresentCheck = IntVar()
        windPresentLabel = Label(windPresentContainer, text = "Wind Present?:")
        windPresentLabel.pack( side=LEFT)

        windPresentCheckBox = Checkbutton(windPresentContainer, variable=self.windPresentCheck)
        windPresentCheckBox.pack(side=LEFT)

        windPresentContainer.pack(pady = 4)

        windmillSwitchingPeriodContainer = Frame(windControlsContainer)

        windmillTimeLabel = Label(windmillSwitchingPeriodContainer, text="Wind changes every: ")
        windmillTimeLabel.pack(side = LEFT)

        self.windSwitchingPeriod = StringVar()
        self.windSwitchingPeriod.set("1")

        windSwitchingEntry = Entry(windmillSwitchingPeriodContainer, textvariable=self.windSwitchingPeriod)
        windSwitchingEntry.pack(side = LEFT)

        windSwitchingUnitsLabel = Label(windmillSwitchingPeriodContainer, text=" Hours")
        windSwitchingUnitsLabel.pack(side = LEFT)     

        windmillSwitchingPeriodContainer.pack(pady=4)
        

        windAmplitudeContainer = Frame(windControlsContainer)

        windAmplitudeLabel = Label(windAmplitudeContainer, text="Wind Amplitdue:")
        windAmplitudeLabel.pack(side = LEFT)
        
        self.windAmplitude = IntVar()
        self.windAmplitude.set(0)
        windAmplitudeScale = Scale(windAmplitudeContainer, orient= HORIZONTAL, from_=0, to=10, variable=self.windAmplitude, command= self.updateWindAmplitudeLabel)
        windAmplitudeScale.pack(side = LEFT)
        self.currentWindAmplitudeLabel = Label(windAmplitudeContainer, text = "0")
        self.currentWindAmplitudeLabel.pack(side = LEFT)   

        windAmplitudeContainer.pack(pady=4)

        windControlsContainer.pack(pady = 8, padx = 8)

    def updateWindAmplitudeLabel(self, currentVal):
        roundedVal = round(float(currentVal), 2)      
        self.currentWindAmplitudeLabel.configure(text= str(roundedVal))

    def startSimBtnCallback(self):

        typeOfDay = self.typeOfDaySelected.get() #string
        daylightHours = self.daylightHoursVar.get() #string

        windPresent = self.windPresentCheck.get() #integer representing boolean
        windSwitchingPeriod = self.windSwitchingPeriod.get() #string
        windAmplitude = self.windAmplitude.get() #int
        numLoops = self.numLoops.get()
        
        windPresent = bool(windPresent)
        windSwitchingPeriod = int(windSwitchingPeriod)
        windAmplitude = int(windAmplitude)
        daylightHours = int(daylightHours)
        numLoops = int(numLoops)

        print("Type of day:", typeOfDay)
        print("Daylight Hours:", daylightHours)
        print("Wind Present:", str(windPresent))
        print("Wind switching period: every", str(windSwitchingPeriod), "hours")
        print("Wind Amplitude:", str(windAmplitude))
        print("Number of loops:", numLoops)
        validated = True

        if windSwitchingPeriod < 0 or windSwitchingPeriod > 23:
            print("Invalid wind switching period")
            validated = False
        
        if daylightHours < 0 or daylightHours > 22:
            print ("Invalid daylight hours")
            validated = False
            
        if typeOfDay != "Sunny" and typeOfDay != "Cloudy":
            print("Invalid type of day")
            validated = False
            
        if numLoops <=0 :
                print("Invalid number of loops")
                validated = False        

        if validated:
            self.mainWindow.setTaskRunning(True, "Cycle mode")
            self.simulation.configure(typeOfDay, daylightHours, windPresent, windSwitchingPeriod, windAmplitude, numLoops)
            cycleSimulationThread = threading.Thread(target=self.simulation.cycleModeLoop)
            cycleSimulationThread.daemon = True
            cycleSimulationThread.start()
            
            self.master.destroy()
            
class GameModeParametersWindow(Frame):

    def __init__(self, master, board , mainWindow, root):
        Frame.__init__(self, master)
        self.master = master
        self.board = board
        self.mainWindow = mainWindow
        self.rootTK = root
        self.initWindow()
        
    def initWindow(self):
        self.master.title("Game mode parameters")

        self.pack(fill=BOTH, expand = 1)

        self.addWindControls()
        self.addSolarControls()
        

        startBtn = Button(self, text = "Start Game Mode", command = self.startSimBtnCallback)
        startBtn.pack(padx= 8, pady = 8)
    
    def addSolarControls(self):

        solarControlContainer = Frame(self)

        Label(solarControlContainer, text="Sunlight control").pack()

        typeOfDayContainer = Frame(solarControlContainer)

        typeOfDayLabel = Label(typeOfDayContainer, text="Type of Day: ")
        typeOfDayLabel.pack(side=LEFT)

        typeOfDayOptions = ["Sunny", "Cloudy"]
        self.typeOfDaySelected = StringVar()

        typeOfDayDropdown = Combobox(typeOfDayContainer, textvariable=self.typeOfDaySelected, values = typeOfDayOptions)
        typeOfDayDropdown.pack(side = LEFT)

        typeOfDayContainer.pack(pady = 4)

        daylightHoursContainer = Frame(solarControlContainer)

        daylightHoursLabel = Label(daylightHoursContainer, text = "Daylight hours (<23)")
        daylightHoursLabel.pack(side = LEFT)

        self.daylightHoursVar = StringVar()
        self.daylightHoursVar.set("12")

        daylightHoursEntry = Entry(daylightHoursContainer, textvariable=self.daylightHoursVar)
        daylightHoursEntry.pack(side = LEFT)

        daylightHoursContainer.pack(pady=4)

        solarControlContainer.pack(pady= 8, padx = 8)

    def addWindControls(self):
        windControlsContainer = Frame(self)

        Label(windControlsContainer, text="Wind control").pack()    

        randomiseWindContainer = Frame(windControlsContainer)      

        self.randomiseWindCheck = IntVar()
        randomiseWindLabel = Label(randomiseWindContainer, text = "Randomise wind:")
        randomiseWindLabel.pack(side=LEFT)

        randomiseCheckBox = Checkbutton(randomiseWindContainer, variable=self.randomiseWindCheck, command = self.onCheckRandomise)
        randomiseCheckBox.pack(side=LEFT)

        randomiseWindContainer.pack(pady = 4)

        windmillSwitchingPeriodContainer = Frame(windControlsContainer)

        windmillTimeLabel = Label(windmillSwitchingPeriodContainer, text="Wind changes every: ")
        windmillTimeLabel.pack(side = LEFT)

        self.windSwitchingPeriod = StringVar()
        self.windSwitchingPeriod.set("1")

        self.windSwitchingEntry = Entry(windmillSwitchingPeriodContainer, textvariable=self.windSwitchingPeriod)
        self.windSwitchingEntry.pack(side = LEFT)

        windSwitchingUnitsLabel = Label(windmillSwitchingPeriodContainer, text=" Hours")
        windSwitchingUnitsLabel.pack(side = LEFT)     

        windmillSwitchingPeriodContainer.pack(pady=4)
        

        windAmplitudeContainer = Frame(windControlsContainer)

        windAmplitudeLabel = Label(windAmplitudeContainer, text="Wind Amplitdue:")
        windAmplitudeLabel.pack(side = LEFT)
        
        self.windAmplitude = IntVar()
        self.windAmplitude.set(0)
        self.windAmplitudeScale = Scale(windAmplitudeContainer, orient= HORIZONTAL, from_=0, to=10, variable=self.windAmplitude, command= self.updateWindAmplitudeLabel)
        self.windAmplitudeScale.pack(side = LEFT)
        self.currentWindAmplitudeLabel = Label(windAmplitudeContainer, text = "0")
        self.currentWindAmplitudeLabel.pack(side = LEFT)   

        windAmplitudeContainer.pack(pady=4)

        windControlsContainer.pack(pady = 8, padx = 8)

    def updateWindAmplitudeLabel(self, currentVal):
        roundedVal = round(float(currentVal), 2)      
        self.currentWindAmplitudeLabel.configure(text= str(roundedVal))

    def startSimBtnCallback(self):

        typeOfDay = self.typeOfDaySelected.get() #string
        daylightHours = self.daylightHoursVar.get() #string

        windSwitchingPeriod = self.windSwitchingPeriod.get() #string
        windAmplitude = self.windAmplitude.get() #int

        randomiseWind = self.randomiseWindCheck.get()

        randomiseWind = bool(randomiseWind)        
        windSwitchingPeriod = int(windSwitchingPeriod)
        windAmplitude = int(windAmplitude)
        daylightHours = int(daylightHours)

        print("Type of day:", typeOfDay)
        print("Daylight Hours:", daylightHours)
        print("Randomise wind", randomiseWind)
        print("Wind switching period: every", str(windSwitchingPeriod), "hours")
        print("Wind Amplitude:", str(windAmplitude))
        validated = True

        if windSwitchingPeriod < 0 or windSwitchingPeriod > 23:
            print("Invalid wind switching period")
            validated = False
        
        if daylightHours < 0 or daylightHours > 22:
            print ("Invalid daylight hours")
            validated = False
            
        if typeOfDay != "Sunny" and typeOfDay != "Cloudy":
            print("Invalid type of day")
            validated = False
                  

        if validated:
            self.mainWindow.setTaskRunning(True, "Game mode")

            newWindow = Toplevel(self.rootTK)
            gameWindow = GameWindow(newWindow)

            self.gameModeObj = GameMode(gameWindow, self.mainWindow, self.board)
            self.gameModeObj.configure(typeOfDay, daylightHours, windSwitchingPeriod, windAmplitude)
            
            gameModeThread = threading.Thread(target=self.gameModeObj.mainLoop)
            gameModeThread.daemon = True
            gameModeThread.start()
            
            self.master.destroy()

    def onCheckRandomise(self, event):
        if self.randomiseWindCheck.get() == 1:
            self.windSwitchingEntry.config(state=DISABLED)
            self.windAmplitudeScale.config(state=DISABLED)
        else:
            self.windSwitchingEntry.config(state=NORMAL)
            self.windAmplitudeScale.config(state=NORMAL)

class GameWindow(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master

        self.RESERVOIR_NO_ACTIVITY = 0
        self.RESERVOIR_GATE_OPENING = 1
        self.RESERVOIR_GATE_OPEN = 2
        self.RESRVOIR_GATE_CLOSING = 3
        self.RESERVOIR_PUMP_TURNING_ON = 4
        self.RESERVOIR_PUMP_ON = 5
        self.RESERVOIR_PUMP_TURNING_OFF = 6

        self.RESERVOIR_MAX_OUTPUT_POWER = 4
        self.RESERVOIR_MAX_INPUT_POWER = -2

        self.DRAIN_START_STOP_RATE = 2 # must ensure max output power is divisible by this rate
        self.PUMP_START_STOP_RATE = 1  # must ensure max input power is divisible by this rate

        self.initWindow()        

    def initWindow(self):
        self.master.title("Game Mode")

        self.pack(fill=BOTH, expand =1)

        currentDayContainer = Frame(self)
        currentDayLabel = Label(currentDayContainer, text= "Day ")
        currentDayLabel.pack(side=LEFT)
        self.currentDayValueLabel = Label(currentDayContainer, text = "1")
        self.currentDayValueLabel.pack(side = LEFT)
        currentDayContainer.pack(padx = 4, pady = 4)

        currentHourContainer = Frame(self)
        currentHourLabel = Label(currentHourContainer, text= "Hour ")
        currentHourLabel.pack(side=LEFT)
        self.currentHourValueLabel = Label(currentHourContainer, text = "0")
        self.currentHourValueLabel.pack(side = LEFT)
        currentHourContainer.pack(padx = 4, pady = 4)

        reservoirStateContainer = Frame(self)
        reservoirStateLabel = Label(reservoirStateContainer, text= "Reservoir status: ")
        reservoirStateLabel.pack(side=LEFT)
        self.reservoirStateValueLabel = Label(reservoirStateContainer, text = "No Activity")
        self.reservoirStateValueLabel.pack(side = LEFT)
        reservoirStateContainer.pack(padx = 4, pady = 4)

        batteryEnergyContainer = Frame(self)
        batteryEnergyLabel = Label(batteryEnergyContainer, text= "Stored Battery Energy: ")
        batteryEnergyLabel.pack(side=LEFT)
        self.currentBatteryValueLabel = Label(batteryEnergyContainer, text = "0")
        self.currentBatteryValueLabel.pack(side = LEFT)
        batteryEnergyUnitsLabel = Label(batteryEnergyContainer, text = " GWh")
        batteryEnergyUnitsLabel.pack(side=LEFT)
        batteryEnergyContainer.pack(padx = 4, pady = 4)

        reservoirEnergyContainer = Frame(self)
        reservoirEnergyLabel = Label(reservoirEnergyContainer, text= "Stored Reservoir Energy: ")
        reservoirEnergyLabel.pack(side=LEFT)
        self.currentReservoirValueLabel = Label(reservoirEnergyContainer, text = "0")
        self.currentReservoirValueLabel.pack(side = LEFT)
        reservoirEnergyUnitsLabel = Label(reservoirEnergyContainer, text = " GWh")
        reservoirEnergyUnitsLabel.pack(side=LEFT)
        reservoirEnergyContainer.pack(padx = 4, pady = 4)

        windPowerContainer = Frame(self)
        windPowerGenerationLabel = Label(windPowerContainer, text= "Wind Power Generation: ")
        windPowerGenerationLabel.pack(side=LEFT)
        self.windPowerGenerationValueLabel = Label(windPowerContainer, text = "0")
        self.windPowerGenerationValueLabel.pack(side = LEFT)
        powerUnitsLabel = Label(windPowerContainer, text = " GW")
        powerUnitsLabel.pack(side=LEFT)
        windPowerContainer.pack(padx = 4, pady = 4)

        solarPowerContainer = Frame(self)
        solarPowerGenerationLabel = Label(solarPowerContainer, text= "Solar Power Generation: ")
        solarPowerGenerationLabel.pack(side=LEFT)
        self.solarPowerGenerationValueLabel = Label(solarPowerContainer, text = "0")
        self.solarPowerGenerationValueLabel.pack(side = LEFT)
        powerUnitsLabel = Label(solarPowerContainer, text = " GW")
        powerUnitsLabel.pack(side=LEFT)
        solarPowerContainer.pack(padx = 4, pady = 4)

        hydroPowerContainer = Frame(self)
        hydroPowerGenerationLabel = Label(hydroPowerContainer, text= "Reservoir Power: ")
        hydroPowerGenerationLabel.pack(side=LEFT)
        self.hydroPowerGenerationValueLabel = Label(hydroPowerContainer, text = "0")
        self.hydroPowerGenerationValueLabel.pack(side = LEFT)
        powerUnitsLabel = Label(hydroPowerContainer, text = " GW")
        powerUnitsLabel.pack(side=LEFT)
        hydroPowerContainer.pack(padx = 4, pady = 4)

        currentConsumptionContainer = Frame(self)
        currentConsumptionLabel = Label(currentConsumptionContainer, text= "City Energy Consumption: ")
        currentConsumptionLabel.pack(side=LEFT)
        self.currentConsumptionValueLabel = Label(currentConsumptionContainer, text = "0")
        self.currentConsumptionValueLabel.pack(side = LEFT)
        powerUnitsLabel = Label(currentConsumptionContainer, text = " GW")
        powerUnitsLabel.pack(side=LEFT)
        currentConsumptionContainer.pack(padx = 4, pady = 4)

        renewableSurplusContainer = Frame(self)
        renewableSurplusLabel = Label(renewableSurplusContainer, text= "Renewable Power Surplus: ")
        renewableSurplusLabel.pack(side=LEFT)
        self.renewableSurplusValueLabel = Label(renewableSurplusContainer, text = "0")
        self.renewableSurplusValueLabel.pack(side = LEFT)
        powerUnitsLabel = Label(renewableSurplusContainer, text = " GW")
        powerUnitsLabel.pack(side=LEFT)
        renewableSurplusContainer.pack(padx = 4, pady = 4)

        renewableShortageContainer = Frame(self)
        renewableShortageLabel = Label(renewableShortageContainer, text= "Renewable Power Shortage: ")
        renewableShortageLabel.pack(side=LEFT)
        self.renewableShortageValueLabel = Label(renewableShortageContainer, text = "0")
        self.renewableShortageValueLabel.pack(side = LEFT)
        powerUnitsLabel = Label(renewableShortageContainer, text = " GW")
        powerUnitsLabel.pack(side=LEFT)
        renewableShortageContainer.pack(padx = 4, pady = 4)


        wastedEnergyContainer = Frame(self)
        wastedEnergyLabel = Label(wastedEnergyContainer, text= "Wasted Energy: ")
        wastedEnergyLabel.pack(side=LEFT)
        self.wastedEnergyValueLabel = Label(wastedEnergyContainer, text = "0")
        self.wastedEnergyValueLabel.pack(side = LEFT)
        energyUnitsLabel = Label(wastedEnergyContainer, text = " GWh")
        energyUnitsLabel.pack(side=LEFT)
        wastedEnergyContainer.pack(padx = 4, pady = 4)

        demandNotMetContainer = Frame(self)
        demandNotMetLabel = Label(demandNotMetContainer, text= "Demand Not Met: ")
        demandNotMetLabel.pack(side=LEFT)
        self.demandNotMetValueLabel = Label(demandNotMetContainer, text = "0")
        self.demandNotMetValueLabel.pack(side = LEFT)
        energyUnitsLabel = Label(demandNotMetContainer, text = " GWh")
        energyUnitsLabel.pack(side=LEFT)
        demandNotMetContainer.pack(padx = 4, pady = 4)

        
        reservoirButtonContainer = Frame(self)
        self.drainReservoirButton = Button(reservoirButtonContainer, text = "Drain Reservoir", command = self.onClickDrainReservoir)
        self.drainReservoirButton.pack(side = LEFT)
        self.stopDrainingButton = Button(reservoirButtonContainer, text = "Stop Draining", command = self.onClickStopDrainingReservoir, state = DISABLED)
        self.stopDrainingButton.pack(side = LEFT)
        self.pumpReservoirButton = Button(reservoirButtonContainer, text = "Pump water to reservoir", command = self.onClickPumpWaterToReservoir)
        self.pumpReservoirButton.pack(side = LEFT)
        self.stopPumpingButton = Button(reservoirButtonContainer, text = "Stop pumping water", command = self.onClickStopPumpingWater, state = DISABLED)
        self.stopPumpingButton.pack(side = LEFT)
        reservoirButtonContainer.pack(pady = 8, padx = 4)

        quitButton = Button(self, text = "Quit Game Mode", command = self.onClickQuit)
        quitButton.pack(pady = 8)

    def updateDisplayedTime(self, day, hour):
        self.currentDayValueLabel.configure(text = str(day))
        self.currentHourValueLabel.configure(text = str(hour))

    def updateReservoirStateDisplay(self, state):
        if state == self.RESERVOIR_NO_ACTIVITY:
            self.reservoirStateValueLabel.configure(text = "No activity")
            self.drainReservoirButton.config(state=NORMAL)
            self.stopDrainingButton.config(state=DISABLED)
            self.pumpReservoirButton.config(state=NORMAL)
            self.stopPumpingButton.config(state=DISABLED)
        elif state == self.RESERVOIR_GATE_OPENING:
            self.reservoirStateValueLabel.configure(text = "Starting to Drain")
            self.drainReservoirButton.config(state=DISABLED)
            self.stopDrainingButton.config(state=DISABLED)
            self.pumpReservoirButton.config(state=DISABLED)
            self.stopPumpingButton.config(state=DISABLED)
        elif state == self.RESERVOIR_GATE_OPEN:
            self.reservoirStateValueLabel.configure(text = "Reservoir Draining")
            self.drainReservoirButton.config(state=DISABLED)
            self.stopDrainingButton.config(state=NORMAL)
            self.pumpReservoirButton.config(state=DISABLED)
            self.stopPumpingButton.config(state=DISABLED)
        elif state == self.RESRVOIR_GATE_CLOSING:
            self.reservoirStateValueLabel.configure(text = "Closing Drain")
            self.drainReservoirButton.config(state=DISABLED)
            self.stopDrainingButton.config(state=DISABLED)
            self.pumpReservoirButton.config(state=DISABLED)
            self.stopPumpingButton.config(state=DISABLED)
        elif state == self.RESERVOIR_PUMP_TURNING_ON:
            self.reservoirStateValueLabel.configure(text = "Pump turning on")
            self.drainReservoirButton.config(state=DISABLED)
            self.stopDrainingButton.config(state=DISABLED)
            self.pumpReservoirButton.config(state=DISABLED)
            self.stopPumpingButton.config(state=DISABLED)
        elif state == self.RESERVOIR_PUMP_ON:
            self.reservoirStateValueLabel.configure(text = "Pump on")
            self.drainReservoirButton.config(state=DISABLED)
            self.stopDrainingButton.config(state=DISABLED)
            self.pumpReservoirButton.config(state=DISABLED)
            self.stopPumpingButton.config(state=NORMAL)
        elif state == self.RESERVOIR_PUMP_TURNING_OFF:
            self.reservoirStateValueLabel.configure(text = "Pump turning off")
            self.drainReservoirButton.config(state=DISABLED)
            self.stopDrainingButton.config(state=DISABLED)
            self.pumpReservoirButton.config(state=DISABLED)
            self.stopPumpingButton.config(state=DISABLED)

    def updateEnergyDisplays(self, batteryEnergy, reservoirEnergy):
        self.currentBatteryValueLabel.configure(text = str(round(batteryEnergy, 2)))
        self.currentReservoirValueLabel.configure(text = str(round(reservoirEnergy, 2)))

        if reservoirEnergy == 0 :
            self.drainReservoirButton.config(state=DISABLED)
            self.stopDrainingButton.config(state=DISABLED)
        
        if batteryEnergy == 0:
            self.pumpReservoirButton.config(state=DISABLED)
            self.stopPumpingButton.config(state=DISABLED)


    def updatePowerDisplays(self, solarPower, windPower, reservoirPower, consumption):
        self.hydroPowerGenerationValueLabel.configure(text = str(reservoirPower))
        self.solarPowerGenerationValueLabel.configure(text = str(solarPower))
        self.windPowerGenerationValueLabel.configure(text = str(windPower))
        self.currentConsumptionValueLabel.configure(text = str(consumption))

    def updateSurplusShortageDisplays(self, surplus, shortage):
        self.renewableSurplusValueLabel.configure(text = str(round(surplus, 2)))
        self.renewableShortageValueLabel.configure(text = str(round(shortage, 2)))

    def updateWastedDemandNotMetDisplay(self, wastedEnergy, demandNotMet):
        self.wastedEnergyValueLabel.configure(text = str(round(wastedEnergy, 2)))
        self.demandNotMetValueLabel.configure(text = str(round(demandNotMet, 2)))

    def onClickDrainReservoir(self):
        t = threading.Thread(target=self.drainReservoir)
        t.daemon = True
        t.start()

    def onClickStopDrainingReservoir(self):
        t = threading.Thread(target=self.stopDraining)
        t.daemon = True
        t.start()
    
    def onClickPumpWaterToReservoir(self):
        t = threading.Thread(target=self.pumpWater)
        t.daemon = True
        t.start()
    
    def onClickStopPumpingWater(self):
        t = threading.Thread(target=self.stopPump)
        t.daemon = True
        t.start()

    def drainReservoir(self):
        self.gameModeObj.setReservoirState(self.RESERVOIR_GATE_OPENING)
        self.drainReservoirButton.config(state=DISABLED)
        self.stopDrainingButton.config(state=DISABLED)
        self.pumpReservoirButton.config(state=DISABLED)
        self.stopPumpingButton.config(state=DISABLED)

        reservoirPower = self.gameModeObj.getReservoirPower()

        while reservoirPower < self.RESERVOIR_MAX_OUTPUT_POWER:
            self.gameModeObj.setReservoirPower(reservoirPower + 1)
            reservoirPower += self.DRAIN_START_STOP_RATE
            time.sleep(2.5)
        
        self.stopDrainingButton.config(state=NORMAL)
        self.gameModeObj.setReservoirState(self.RESERVOIR_GATE_OPEN)

    def stopDraining(self):
        self.gameModeObj.setReservoirState(self.RESRVOIR_GATE_CLOSING)
        self.drainReservoirButton.config(state=DISABLED)
        self.stopDrainingButton.config(state=DISABLED)
        self.pumpReservoirButton.config(state=DISABLED)
        self.stopPumpingButton.config(state=DISABLED)

        reservoirPower = self.gameModeObj.getReservoirPower()

        while reservoirPower > 0:
            self.gameModeObj.setReservoirPower(reservoirPower - 1)
            reservoirPower -= self.DRAIN_START_STOP_RATE
            time.sleep(2.5)
        
        self.drainReservoirButton.config(state=NORMAL)
        self.pumpReservoirButton.config(state=NORMAL)
        self.gameModeObj.setReservoirState(self.RESERVOIR_NO_ACTIVITY)

    def pumpWater(self):
        self.gameModeObj.setReservoirState(self.RESERVOIR_PUMP_TURNING_ON)
        self.drainReservoirButton.config(state=DISABLED)
        self.stopDrainingButton.config(state=DISABLED)
        self.pumpReservoirButton.config(state=DISABLED)
        self.stopPumpingButton.config(state=DISABLED)

        reservoirPower = self.gameModeObj.getReservoirPower()

        while reservoirPower > self.RESERVOIR_MAX_INPUT_POWER:
            self.gameModeObj.setReservoirPower(reservoirPower - 1)
            reservoirPower -= self.PUMP_START_STOP_RATE
            time.sleep(2.5)
        
        self.stopPumpingButton.config(state=NORMAL)
        self.gameModeObj.setReservoirState(self.RESERVOIR_PUMP_ON)

    def stopPump(self):
        self.gameModeObj.setReservoirState(self.RESERVOIR_PUMP_TURNING_OFF)
        self.drainReservoirButton.config(state=DISABLED)
        self.stopDrainingButton.config(state=DISABLED)
        self.pumpReservoirButton.config(state=DISABLED)
        self.stopPumpingButton.config(state=DISABLED)

        reservoirPower = self.gameModeObj.getReservoirPower()

        while reservoirPower < 0:
            self.gameModeObj.setReservoirPower(reservoirPower + 1)
            reservoirPower += self.PUMP_START_STOP_RATE
            time.sleep(2.5)
        
        self.drainReservoirButton.config(state=NORMAL)
        self.pumpReservoirButton.config(state=NORMAL)
        self.gameModeObj.setReservoirState(self.RESERVOIR_NO_ACTIVITY)

    def disableDrainStartButton(self):
        self.drainReservoirButton.config(state = DISABLED)
    
    def enableDrainStartButton(self):
        self.drainReservoirButton.config(state = NORMAL)

    def setGameModeObj(self, gameModeObj):
        self.gameModeObj = gameModeObj

    def onClickQuit(self):
        self.gameModeObj.stopGameMode()
        self.master.destroy()

    def gameLost(self):
        messagebox.showinfo("Game Over!", "You failed to meet the demand or wasted too much energy!")