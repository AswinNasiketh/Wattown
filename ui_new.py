import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock


class MainScreenManager(ScreenManager):
    pass

class SelectModeScreen(Screen):
    pass


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


class WattownApp(App):

    def build(self):
        self.mainScreenManager = MainScreenManager()
        return self.mainScreenManager

    def UIUpdateClockCallback(self, dt):
        self.mainScreenManager.get_screen('interactiveMode').incrementProperties()


if __name__ == '__main__':
    w = WattownApp()
    w.run()
    
    
