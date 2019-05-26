import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import pigpio
import neopixel

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

                self.fuelCellPin = 8
                self.pi.set_mode(self.fuelCellPin, pigpio.OUTPUT)
                self.pi.write(self.fuelCellPin, 0)

                self.num_neopixels = 97
                self.reservoir_level_0 = 0
                self.reservoir_level_1_lower = 1
                self.reservoir_level_1_upper = 2
                self.reservoir_level_2_lower = 3
                self.reservoir_level_2_upper = 4
                self.reservoir_level_3_lower = 5
                self.reservoir_level_3_upper = 7
                self.city_range_lower = 8
                self.city_range_upper = 94
                self.fuel_cell_range_lower = 95
                self.fuel_cell_range_upper = 96
                
                self.pixels = neopixel.NeoPixel(board.D12, self.num_neopixels, auto_write = False)


        def driveWindmills(self, frequency):
                print("Drive windmills called")
                print("currently driving windmills?:", str(self.drivingWindmills))
                if self.drivingWindmills:
                        self.stopWindmills()

                halfCyclePeriod = 1/(2 * frequency)
                halfCyclePeriod = int(halfCyclePeriod  * (10**6)) #convert to microseconds
                square = []

                print("Square wave half cycle period:", str(halfCyclePeriod), "us")

                #                          ON       OFF    MICROS
                square.append(pigpio.pulse(1<<self.windmillDriverPlus, 1<<self.windmillDriverMinus, halfCyclePeriod))
                square.append(pigpio.pulse(1<<self.windmillDriverMinus,1<<self.windmillDriverPlus, halfCyclePeriod))
                self.pi.wave_add_generic(square)
                self.wid = self.pi.wave_create()
                
                print("Wave ID: ", str(self.wid))

                if self.wid >= 0:
                        self.pi.wave_send_repeat(self.wid)
                        self.drivingWindmills = True

        def stopWindmills(self): 
                print("Stop windmills called")
                print("currently driving windmills?:", str(self.drivingWindmills))    
                
                if self.drivingWindmills:
                        print("Stopping Wave ID: ", str(self.wid))
                        self.pi.wave_tx_stop()
                        self.pi.wave_delete(self.wid)
                        self.drivingWindmills = False
                        self.pi.write(self.windmillDriverPlus, 0)
                        self.pi.write(self.windmillDriverMinus, 0)

        def releaseResources(self):
                self.pi.stop()

        def getSolarPanelVoltage(self):    
                return self.adcChannel7.voltage

        def getWindmillVoltages(self):
                return [self.adcChannel1.voltage, self.adcChannel2.voltage, self.adcChannel3.voltage, self.adcChannel4.voltage, self.adcChannel5.voltage]

        #LED control code, colour must be inputted as tuple of three integers between 0 and 255 (i.e. setCityLEDs((255,255,0))
        def setCityLEDs(self, colour):
                for i in range(self.city_range_lower, self.city_range_upper + 1):
                        self.pixels[i] = colour

                self.pixels.show()

        def setReservoirLEDs(self, level0Colour, level1Colour, level2Colour, level3Colour):

                self.pixels[self.reservoir_level_0] = level0Colour

                for i in range(self.reservoir_level_1_lower, self.reservoir_level_1_upper + 1):
                        self.pixels[i] = level1Colour

                for i in range(self.reservoir_level_2_lower, self.reservoir_level_2_upper + 1):
                        self.pixels[i] = level2Colour

                for i in range(self.reservoir_level_3_lower, self.reservoir_level_3_upper + 1):
                        self.pixels[i] = level3Colour      
                
                self.pixels.show()

        def setFuelCellLEDs(self, colour):

                for i in range(self.fuel_cell_range_lower, self.fuel_cell_range_upper + 1):
                        self.pixels[i] = colour

                self.pixels.show()

        def turnOnFuelCell(self):
               self.pi.write(self.fuelCellPin, 1)

        def turnOffFuelCell(self):
               self.pi.write(self.fuelCellPin, 0)

        def resetBoard(self):
                self.pixels.fill((0,0,0))
                self.stopWindmills()
                self.turnOffFuelCell()
