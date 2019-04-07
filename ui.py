from tkinter import *
from tkinter.ttk import *

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

    def __init__(self, master, simulation):
        Frame.__init__(self, master)
        self.master = master
        self.simulation = simulation
        self.initWindow()
        
    def initWindow(self):
        self.master.title("Cycle parameters")

        self.pack(fill=BOTH, expand = 1)

        self.addWindControls()
        self.addSolarControls()

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

        daylightHoursLabel = Label(daylightHoursContainer, text = "Daylight hours (<24)")
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

        windFrequencyContainer = Frame(windControlsContainer)

        windFrequencyLabel = Label(windFrequencyContainer, text="Wind Frequency (Hz) :")
        windFrequencyLabel.pack(side = LEFT)

        self.windFrequency = DoubleVar()
        windFrequencyScale = Scale(windFrequencyContainer, orient= HORIZONTAL, from_=0.033, to=0.25, variable=self.windFrequency, command= self.updateWindFrequencyLabel)
        windFrequencyScale.pack(side = LEFT)
        self.currentWindFrequencyLabel = Label(windFrequencyContainer, text = str(0.033) + " Hz")
        self.currentWindFrequencyLabel.pack(side = LEFT)        

        windFrequencyContainer.pack(pady=4)
        

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
        self.currentWindFrequencyLabel.configure(text= str(roundedVal) + " Hz")

    def updateWindAmplitudeLabel(self, currentVal):
        roundedVal = round(float(currentVal), 2)      
        self.currentWindAmplitudeLabel.configure(text= str(roundedVal))

    def startSimBtnCallback(self):

        typeOfDay = self.typeOfDaySelected.get() #string
        daylightHours = self.daylightHoursVar.get() #string

        windPresent = self.windPresentCheck.get() #integer representing boolean
        windFrequency = self.windFrequency.get() #double
        windAmplitude = self.windAmplitude.get() #int

        #TODO: perform validation

        print("Type of day:", typeOfDay)
        print("Daylight Hours:", daylightHours)
        print("Wind Present:", str(windPresent))
        print("Wind Frequency:", str(windFrequency))
        print("Wind Amplitude:", str(windAmplitude))

        #TODO: apply these retrieved values to simulation object