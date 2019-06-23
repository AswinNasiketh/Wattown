import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import pigpio
import neopixel
import threading
import values

class WattownBoard():
        def __init__(self):
                spi = busio.SPI(clock=board.SCK_1, MISO=board.MISO_1, MOSI=board.MOSI_1) #ADCs use second SPI port of RPi
                cs = digitalio.DigitalInOut(board.D16)
                mcp = MCP.MCP3008(spi, cs)

                self.adcChannel1 = AnalogIn(mcp, MCP.P1) # channels 1 to 5 are measuring windmill voltages
                self.adcChannel2 = AnalogIn(mcp, MCP.P2)
                self.adcChannel3 = AnalogIn(mcp, MCP.P3)
                self.adcChannel4 = AnalogIn(mcp, MCP.P4)
                self.adcChannel5 = AnalogIn(mcp, MCP.P5)
                self.adcChannel7 = AnalogIn(mcp, MCP.P7) #channel 7 is measuring solar panel voltage

                self.windmillDriverPlus = 1 #pins connected to BJT H bridges driving windmills
                self.windmillDriverMinus = 7

                self.pi = pigpio.pi()
                self.pi.set_mode(self.windmillDriverPlus, pigpio.OUTPUT)
                self.pi.set_mode(self.windmillDriverMinus, pigpio.OUTPUT)
                self.pi.write(self.windmillDriverPlus, 0)
                self.pi.write(self.windmillDriverMinus, 0)
                self.wid = 0
                self.drivingWindmills = False
                self.WINDMILL_DRIVE_FREQUENCY = 4

                self.fuelCellPin = 8
                self.pi.set_mode(self.fuelCellPin, pigpio.OUTPUT)
                self.pi.write(self.fuelCellPin, 0)

                self.NUM_NEOPIXELS = 100
                self.RESERVOIR_LEVEL_0_LOWER = 0
                self.RESERVOIR_LEVEL_0_UPPER = 2
                self.RESERVOIR_LEVEL_1_LOWER = 3
                self.RESERVOIR_LEVEL_1_UPPER = 5
                self.RESERVOIR_LEVEL_2_LOWER = 6
                self.RESERVOIR_LEVEL_2_UPPER = 8
                self.RESERVOIR_LEVEL_3_LOWER = 9
                self.RESERVOIR_LEVEL_3_UPPER = 11
                self.CITY_RANGE_LOWER = 12
                self.CITY_RANGE_UPPER = 98
                self.FUEL_CELL_RANGE_LOWER = 99
                self.FUEL_CELL_RANGE_UPPER = 100         

                #city LED ranges
                self.CITY_BLOCK_1_LOWER = 12
                self.CITY_BLOCK_1_UPPER = 32
                self.CITY_BLOCK_2_LOWER = 33
                self.CITY_BLOCK_2_UPPER = 61
                self.CITY_BLOCK_3_LOWER = 62
                self.CITY_BLOCK_3_UPPER = 98
                
                self.pixels = neopixel.NeoPixel(board.D12, self.NUM_NEOPIXELS, auto_write = False)

        def driveWindmills(self):
                if self.drivingWindmills:
                        self.stopWindmills()
                
                self.drivingWindmills = True
                self.windmillDriverThread = WindmillDriveThread()
                self.windmillDriverThread.daemon = True
                self.windmillDriverThread.setDriveFrequency(self.WINDMILL_DRIVE_FREQUENCY)
                self.windmillDriverThread.setDrivePins(self.windmillDriverPlus, self.windmillDriverMinus)
                self.windmillDriverThread.setPiGPIOHandle(self.pi)
                self.windmillDriverThread.start()

        def stopWindmills(self):
                if self.drivingWindmills:
                        self.windmillDriverThread.stopDriving()
                        self.windmillDriverThread.join()
                        self.drivingWindmills = False

        def releaseResources(self):
                self.pi.stop()

        def getSolarPanelVoltage(self):    
                return self.adcChannel7.voltage

        def getWindmillVoltages(self):
                return [self.adcChannel1.voltage, self.adcChannel2.voltage, self.adcChannel3.voltage, self.adcChannel4.voltage, self.adcChannel5.voltage]

        #LED control code, colour must be inputted as tuple of three integers between 0 and 255 (i.e. setCityLEDs((255,255,0))
        def setCityLEDs(self, colour, rangeLower = 8, rangeUpper = 94):
                for i in range(self.CITY_BLOCK_1_LOWER, self.CITY_BLOCK_3_UPPER + 1):
                        self.pixels[i] = (0,0,0)
                
                for i in range(rangeLower, rangeUpper + 1):
                        self.pixels[i] = colour

                self.pixels.show()

        def setReservoirLEDs(self, level0Colour, level1Colour, level2Colour, level3Colour):

                for i in range(self.RESERVOIR_LEVEL_0_LOWER, self.RESERVOIR_LEVEL_0_UPPER + 1):
                        self.pixels[i] = level0Colour

                for i in range(self.RESERVOIR_LEVEL_1_LOWER, self.RESERVOIR_LEVEL_1_UPPER + 1):
                        self.pixels[i] = level1Colour

                for i in range(self.RESERVOIR_LEVEL_2_LOWER, self.RESERVOIR_LEVEL_2_UPPER + 1):
                        self.pixels[i] = level2Colour

                for i in range(self.RESERVOIR_LEVEL_3_LOWER, self.RESERVOIR_LEVEL_3_UPPER + 1):
                        self.pixels[i] = level3Colour      
                
                self.pixels.show()

        def setFuelCellLEDs(self, colour):

                for i in range(self.FUEL_CELL_RANGE_LOWER, self.FUEL_CELL_RANGE_UPPER + 1):
                        self.pixels[i] = colour

                self.pixels.show()

        def turnOnFuelCell(self):
               self.pi.write(self.fuelCellPin, 1)

        def turnOffFuelCell(self):
               self.pi.write(self.fuelCellPin, 0)

        def pulseFuelCell(self):
                pulseThread = FuelCellPulseThread()
                pulseThread.daemon = True
                pulseThread.setPiGPIOHandle(self.pi)
                pulseThread.setFuelCellPin(self.fuelCellPin)
                pulseThread.start()

        def resetBoard(self):
                self.pixels.fill((0,0,0))
                self.pixels.show()
                self.stopWindmills()
                self.turnOffFuelCell()

        def areWindmillsOn(self):
                return self.drivingWindmills

        def lightCityBlocks(self, cityLightsCoefficient):
                if cityLightsCoefficient == 0:
                        self.setCityLEDs(values.LED_RED_DIM)
                elif cityLightsCoefficient > 0 and cityLightsCoefficient <= 0.33:
                        self.setCityLEDs(values.LED_CITY_LIGHTS_YELLOW, self.CITY_BLOCK_1_LOWER, self.CITY_BLOCK_1_UPPER)
                elif cityLightsCoefficient > 0.33 and cityLightsCoefficient <= 0.66:
                        self.setCityLEDs(values.LED_CITY_LIGHTS_YELLOW, self.CITY_BLOCK_1_LOWER, self.CITY_BLOCK_2_UPPER)
                elif cityLightsCoefficient > 0.66:
                        self.setCityLEDs(values.LED_CITY_LIGHTS_YELLOW)

        def lightReservoir(self, reservoirLevel):
                if reservoirLevel == 0:
                        level0Colour = (0,0,0)
                        level1Colour = (0,0,0)
                        level2Colour = (0,0,0)
                        level3Colour = (0,0,0)
                elif reservoirLevel > 0 and reservoirLevel < 25:
                        level0Colour = values.LED_WATER_BLUE
                        level1Colour = (0,0,0)
                        level2Colour = (0,0,0)
                        level3Colour = (0,0,0)
                elif reservoirLevel >= 25 and reservoirLevel < 50:
                        level0Colour = values.LED_WATER_BLUE
                        level1Colour = values.LED_WATER_BLUE
                        level2Colour = (0,0,0)
                        level3Colour = (0,0,0)
                elif reservoirLevel >= 50 and reservoirLevel < 75:
                        level0Colour = values.LED_WATER_BLUE
                        level1Colour = values.LED_WATER_BLUE
                        level2Colour = values.LED_WATER_BLUE
                        level3Colour = (0,0,0)
                elif reservoirLevel >= 75:
                        level0Colour = values.LED_WATER_BLUE
                        level1Colour = values.LED_WATER_BLUE
                        level2Colour = values.LED_WATER_BLUE
                        level3Colour = values.LED_WATER_BLUE

                self.setReservoirLEDs(level0Colour,level1Colour,level2Colour,level3Colour)

class WindmillDriveThread(threading.Thread):

        def setPiGPIOHandle(self, handle):
                self.pi = handle

        def setDrivePins(self, plus, minus):
                self.drivePlusPin = plus
                self.driveMinusPin = minus

        def setDriveFrequency(self, driveFrequency):
                driveTimePeriod = 1/driveFrequency
                self.halfPeriod = round(driveTimePeriod / 2, 3)

        def stopDriving(self):
                self.keepDriving = False

        def run(self):
                self.keepDriving = True
                while self.keepDriving:
                        self.pi.write(self.driveMinusPin, 0)
                        self.pi.write(self.drivePlusPin, 1)                        
                        time.sleep(self.halfPeriod)
                        self.pi.write(self.drivePlusPin, 0)
                        self.pi.write(self.driveMinusPin, 1)
                        time.sleep(self.halfPeriod)
                
                self.pi.write(self.driveMinusPin, 0)
                self.pi.write(self.drivePlusPin, 0)

class FuelCellPulseThread(threading.Thread):

        def setPiGPIOHandle(self, handle):
                self.pi = handle
        
        def setFuelCellPin(self, pin):
                self.fuelCellPin = pin

        def run(self):
                self.pi.write(self.fuelCellPin, 1)
                time.sleep(0.5)
                self.pi.write(self.fuelCellPin, 0)