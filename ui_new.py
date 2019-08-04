import sys
sys.path.append('/home/pi/.local/lib/python3.5/site-packages')

import kivy
kivy.require('1.11.1')

from kivy.core.window import Window
Window.fullscreen = 'auto'

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButtonBehavior

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock

from wattownBoard import WattownBoard
from interactiveMode import InteractiveModeThread
from cycleSim import CycleSimThread

class FieldLabel(Label):
    pass

class TitleLabel(Label):
    pass

class MainScreenManager(ScreenManager):
    pass

class SelectModeScreen(Screen):
    def __init__(self, **kwargs):
        self.board = WattownBoard()
        self.board.start()
        super().__init__(**kwargs)

    def startInteractiveMode(self):
        interactiveModeThread = InteractiveModeThread(self.board)
        self.manager.get_screen('interactiveMode').setSimThread(interactiveModeThread, self.board)
        self.manager.current = 'interactiveMode'
        self.manager.get_screen('interactiveMode').startInteractiveMode()

    def configureCycleMode(self):
        cycleModeThread = CycleSimThread(self.board)
        self.manager.get_screen('cycleModeConfig').setSimThread(cycleModeThread)
        self.manager.current = 'cycleModeConfig'
        
    def __del__(self, **kwargs):
        self.board.join()
        self.board.releaseResources()
        super().__del__(**kwargs)
        


class InteractiveModeScreen(Screen):
    solarPanelStatus = StringProperty('Off')
    numWindmillsOn = NumericProperty(0)
    cityPowered = NumericProperty(0)
    storedEnergy = NumericProperty(0)

    #for testing only
    # def incrementProperties(self):
    #     self.numWindmillsOn += 1
    #     self.cityPowered += 1
    #     self.storedEnergy += 1
    #     if self.solarPanelStatus == "Off":
    #         self.solarPanelStatus = 'On'
    #     else:
    #         self.solarPanelStatus = "Off"

    def setSimThread(self, simThread, board):
        self.interactiveModeThread = simThread
        self.board = board

    def startInteractiveMode(self):
        self.interactiveModeThread.start()
        self.UIUpdatEvent = Clock.schedule_interval(self.UIUpdate, 0.5)
    
    def stopInteractiveMode(self):
        self.interactiveModeThread.join()
        self.board.resetBoard()
        Clock.unschedule(self.UIUpdatEvent)
        self.manager.current = 'selectMode'

    def UIUpdate(self, dt):
        if self.board.solarPanels.areSolarPanelsOn():
            self.solarPanelStatus = 'On'
        else:
            self.solarPanelStatus = 'Off'
        
        self.numWindmillsOn = self.board.windmills.numWindmillsBlown()
        self.cityPowered = self.interactiveModeThread.interactiveModeObj.getCityPoweredPercent()
        self.storedEnergy = self.interactiveModeThread.interactiveModeObj.currentBatteryLevel

class CycleModeConfigScreen(Screen):
    numDaysToSimulate = NumericProperty(1)
    sustainable = BooleanProperty(True)

    def stateToBool(self, state):
        return state == 'down'
    
    def startCycleMode(self):

        sustainable = self.stateToBool(self.ids.sustainableToggleButton.state)
        self.simThread.configure(self.numDaysToSimulate, sustainable)
        self.manager.current = 'cycleMode'
        self.manager.get_screen('cycleMode').startCycleMode(self.simThread)

        print('days to simulate', self.numDaysToSimulate)

    def decrementDaysToSimulate(self):
        self.numDaysToSimulate -= 1

        if self.numDaysToSimulate < 0:
            self.numDaysToSimulate = 0

    def setSimThread(self, simThread):
        self.simThread = simThread

class CycleModeScreen(Screen):
    windPower = NumericProperty(0)
    solarPower = NumericProperty(0)
    hydroPower = NumericProperty(0)
    consumption = NumericProperty(0)
    renewableSupply = NumericProperty(0)
    renewableSurplus = NumericProperty(0)
    batteryEnergy = NumericProperty(0)
    hydroEnergy = NumericProperty(0)
    day = NumericProperty(0)
    hour = NumericProperty(0)


    def setSimThread(self, simThread):
        self.cycleSimThread = simThread
    
    def startCycleMode(self, simThread):
        self.cycleSimThread = simThread
        self.cycleSimThread.start()
        self.UIUPdateEvent =  Clock.schedule_interval(self.UIUpdate, 0.5)
    
    def stopCycleMode(self):
        self.cycleSimThread.join()
        Clock.unschedule(self.UIUPdateEvent)
        self.manager.current = 'selectMode'
    
    def UIUpdate(self, dt):
        UIData = self.cycleSimThread.cycleModeObj.getUIData()
        hydroPowerValueLabel = self.ids.hydroPowerValueLabel
        renewableSupplyLabel = self.ids.renewableSupplyLabel
        surplusValueLabel = self.ids.surplusValueLabel

        self.windPower = round(UIData[0] , 2)
        self.solarPower = round(UIData[1], 2)
        self.hydroPower = round(UIData[2], 2)
        self.consumption = round(UIData[3], 2)
        self.renewableSupply = round(UIData[4], 2)
        self.renewableSurplus = round(self.renewableSupply + self.consumption, 2) # consumption always negative
        self.batteryEnergy = round(UIData[5], 2)
        self.hydroEnergy = round(UIData[6], 2)
        self.day = round(UIData[7], 2)
        self.hour = round(UIData[8], 2)

        if self.hydroPower < 0:
            hydroPowerValueLabel.color = [1,0,0,1] #r, g, b, a
        elif self.hydroPower > 0:
            hydroPowerValueLabel.color = [0,1,0,1] #r, g, b, a
        else:
            hydroPowerValueLabel.color = [1,1,1,1] #r, g, b, a
        
        if self.renewableSupply < 0:
            renewableSupplyLabel.color = [1,0,0,1] #r, g, b, a
        elif self.renewableSupply > 0:
            renewableSupplyLabel.color = [0,1,0,1] #r, g, b, a
        else:
            renewableSupplyLabel.color = [1,1,1,1] #r, g, b, a
        
        if self.renewableSurplus < 0:
            surplusValueLabel.color = [1,0,0,1] #r, g, b, a
        elif self.renewableSupply > 0:
            surplusValueLabel.color = [0,1,0,1] #r, g, b, a
        else:
            surplusValueLabel.color = [1,1,1,1] #r, g, b, a

class SubstationModeConfigScreen(Screen):

    def stateToBool(self, state):
        return state == 'down'
    
    def startSubstationMode(self):

        sustainable = self.stateToBool(self.ids.sustainableToggleButton.state)
        self.simThread.configure(sustainable)
        self.manager.current = 'substationMode'
        self.manager.get_screen('substationMode').startCycleMode(self.simThread)

    def setSimThread(self, simThread):
        self.simThread = simThread

class WattownApp(App):

    def build(self):
        self.mainScreenManager = MainScreenManager()
        return self.mainScreenManager


if __name__ == '__main__':
    w = WattownApp()
    w.run()
    
    
