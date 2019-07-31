import sys
sys.path.append('/home/pi/.local/lib/python3.5/site-packages')

import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButtonBehavior

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

from wattownBoard import WattownBoard
from interactiveMode import InteractiveModeThread


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
        
    def __del__(self, **kwargs):
        self.board.join()
        self.board.releaseResources()
        super().__del__(**kwargs)
        


class InteractiveModeScreen(Screen):
    solarPanelStatus = StringProperty('Off')
    numWindmillsOn = NumericProperty(0)
    cityPowered = NumericProperty(0)
    storedEnergy = NumericProperty(0)

    def incrementProperties(self):
        self.numWindmillsOn += 1
        self.cityPowered += 1
        self.storedEnergy += 1
        if self.solarPanelStatus == "Off":
            self.solarPanelStatus = 'On'
        else:
            self.solarPanelStatus = "Off"

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
        self.interactiveModeThread.interactiveModeObj.getCityPoweredPercent()
        self.interactiveModeThread.interactiveModeObj.currentBatteryLevel

class CycleModeConfigScreen(Screen):
    daylightHours = NumericProperty(12)
    numDaysToSimulate = NumericProperty(1)

    def stateToBool(self, state):
        return state == 'down'
    
    def startCycleMode(self):
        windPresent = self.stateToBool(self.ids.windPresentYesButton.state)
        randomiseWind = self.stateToBool(self.ids.randomiseWindYesButton.state)
        sunny = self.stateToBool(self.ids.sunnyButton.state)

        print("wind present?", str(windPresent))
        print('randomise wind?', str(randomiseWind))
        print('sunny?', str(sunny))

        print('daylight horus', self.daylightHours)
        print('days to simulate', self.numDaysToSimulate)

    def incrementDaylightHours(self):
        self.daylightHours += 1
        if self.daylightHours > 24:
            self.daylightHours = 0
    
    def decrementDaylightHours(self):
        self.daylightHours -= 1
        
        if self.daylightHours < 0:
            self.daylightHours = 24

    def decrementDaysToSimulate(self):
        self.numDaysToSimulate -= 1

        if self.numDaysToSimulate < 0:
            self.numDaysToSimulate = 0


class WattownApp(App):

    def build(self):
        self.mainScreenManager = MainScreenManager()
        return self.mainScreenManager

    def UIUpdateClockCallback(self, dt):
        self.mainScreenManager.get_screen('interactiveMode').incrementProperties()


if __name__ == '__main__':
    w = WattownApp()
    w.run()
    
    
