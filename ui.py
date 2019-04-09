from tkinter import *
from tkinter.ttk import *
import threading

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

        windmillTimeContainer = Frame(windControlsContainer)

        windmillTimeLabel = Label(windmillTimeContainer, text="Time windmills are on per 'hour' (s):")
        windmillTimeLabel.pack(side = LEFT)

        self.windmillTime = DoubleVar()
        windmillTimeScale = Scale(windmillTimeContainer, orient= HORIZONTAL, from_=2, to=15, variable=self.windmillTime, command= self.updateWindFrequencyLabel)
        windmillTimeScale.pack(side = LEFT)
        self.currentWindmillTimeLabel = Label(windmillTimeContainer, text = "2 s")
        self.currentWindmillTimeLabel.pack(side = LEFT)        

        windmillTimeContainer.pack(pady=4)
        

        windAmplitudeContainer = Frame(windControlsContainer)

        windAmplitudeLabel = Label(windAmplitudeContainer, text="Wind Amplitdue:")
        windAmplitudeLabel.pack(side = LEFT)
        
        self.windAmplitude = IntVar()
        windAmplitudeScale = Scale(windAmplitudeContainer, orient= HORIZONTAL, from_=0, to=14, variable=self.windAmplitude, command= self.updateWindAmplitudeLabel)
        windAmplitudeScale.pack(side = LEFT)
        self.currentWindAmplitudeLabel = Label(windAmplitudeContainer, text = "0")
        self.currentWindAmplitudeLabel.pack(side = LEFT)   

        windAmplitudeContainer.pack(pady=4)

        windControlsContainer.pack(pady = 8, padx = 8)

    def updateWindFrequencyLabel(self, currentVal):
        roundedVal = round(float(currentVal), 3)
        self.currentWindmillTimeLabel.configure(text= str(roundedVal) + " s")

    def updateWindAmplitudeLabel(self, currentVal):
        roundedVal = round(float(currentVal), 2)      
        self.currentWindAmplitudeLabel.configure(text= str(roundedVal))

    def startSimBtnCallback(self):

        typeOfDay = self.typeOfDaySelected.get() #string
        daylightHours = self.daylightHoursVar.get() #string

        windPresent = self.windPresentCheck.get() #integer representing boolean
        windmillTime = self.windmillTime.get() #double
        windAmplitude = self.windAmplitude.get() #int
        numLoops = self.numLoops.get()
        
        windPresent = bool(windPresent)
        windmillTime = int(windmillTime)
        windAmplitude = int(windAmplitude)
        daylightHours = int(daylightHours)
        numLoops = int(numLoops)

        print("Type of day:", typeOfDay)
        print("Daylight Hours:", daylightHours)
        print("Wind Present:", str(windPresent))
        print("Windmill Time:", str(windmillTime))
        print("Wind Amplitude:", str(windAmplitude))
        print("Number of loops:", numLoops)
        validated = True

        
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
            self.simulation.configure(typeOfDay, daylightHours, windPresent, windmillTime, windAmplitude, numLoops)
            cycleSimulationThread = threading.Thread(target=self.simulation.cycleModeLoop)
            cycleSimulationThread.daemon = True
            cycleSimulationThread.start()
            
            self.master.destroy()
            
