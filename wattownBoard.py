import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
import time
import pigpio
import neopixel
import threading
import time

import values


from reservoir import Reservoir
from windmills import Windmills
from solarPanels import SolarPanels
from city import City
from fuelcell import FuelCell
from distributionLines import DistributionLine
from transmissionLines import TransmissionLines
from wattownSign import WattownSign
from substation import Substation


class WattownBoard(threading.Thread):
        def __init__(self):
                spi = busio.SPI(clock=board.SCK_1, MISO=board.MISO_1, MOSI=board.MOSI_1) #ADCs use second SPI port of RPi
                cs = digitalio.DigitalInOut(board.D16)
                mcp = MCP.MCP3008(spi, cs)               
                self.pi = pigpio.pi()       

                self.NUM_NEOPIXELS = 118    
                self.pixels = neopixel.NeoPixel(board.D12, self.NUM_NEOPIXELS, auto_write = False)

                self.reservoir = Reservoir(self.pixels)
                self.windmills = Windmills(self.pi, mcp)
                self.solarPanels = SolarPanels(mcp)
                self.city = City(self.pixels)
                self.fuelCell = FuelCell(self.pixels, self.pi)
                self.distributionMiddle = DistributionLine(self.pixels, 101, 4)
                self.distributionRight = DistributionLine(self.pixels, 105, 5, True)
                self.transmissionLine = TransmissionLines(self.pixels)
                self.wattownSign = WattownSign(self.pixels)
                self.substation = Substation(self.pixels)

                self.stopEvent = threading.Event()
                self.stopEvent.clear()

                super().__init__()

        def join(self, timeout = None):
                self.stopEvent.set()           
                self.resetBoard()
                threading.Thread.join(self, timeout)

        def run(self):
                while not self.stopEvent.wait(0.1): # provides delay as well instead of sleep
                        currentTime = self.getTimeMilliseconds()
                        self.pixels.show()
                        self.windmills.update(currentTime)
                        self.fuelCell.update(currentTime)
                        self.distributionMiddle.update(currentTime)
                        self.distributionRight.update(currentTime)

        def releaseResources(self):
                self.pi.stop()

        def resetBoard(self):
                self.pixels.fill((0,0,0))
                self.windmills.stopWindmills()
                self.fuelCell.stopPulsing()
                self.distributionMiddle.stopPowerFlow()
                self.distributionRight.stopPowerFlow()

                self.pixels.show()
                self.windmills.update(0)
                self.fuelCell.update(0)
                self.distributionMiddle.update(0)
                self.distributionRight.update(0)

        #provides interface with city lights coefficient 
        def lightCityBlocks(self, cityLightsCoefficient, supplyTripped = False, offColourBlack = False):
                numBlocksToLight = round(cityLightsCoefficient * 3)
                self.city.lightCityBlocks(numBlocksToLight, supplyTripped, offColourBlack)

        def lightReservoir(self, reservoirLevel):
              levelsToLight = round(reservoirLevel/25)
              
              self.reservoir.setWaterLevel(levelsToLight)

        def getTimeMilliseconds(self):
                return int(round(time.time() * 1000))

