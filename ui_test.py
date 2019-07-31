
import kivy
kivy.require('1.11.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.togglebutton import ToggleButtonBehavior

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock


class TestScreenManager(ScreenManager):
    pass

class SelectModeScreen(Screen):
    pass

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

class TestApp(App):

    def build(self):
        return TestScreenManager()

if __name__ == '__main__':
    TestApp().run()