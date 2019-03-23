import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
import time
import pigpio
import neopixel

spi = busio.SPI(clock=board.SCK_1, MISO=board.MISO_1, MOSI=board.MOSI_1) #ADCs use second SPI port of RPi
cs = digitalio.DigitalInOut(board.D16)
mcp = MCP.MCP3008(spi, cs)

adcChannel1 = AnalogIn(mcp, MCP.P1) # channels 1 to 5 are measuring windmill voltages
adcChannel2 = AnalogIn(mcp, MCP.P2)
adcChannel3 = AnalogIn(mcp, MCP.P3)
adcChannel4 = AnalogIn(mcp, MCP.P4)
adcChannel5 = AnalogIn(mcp, MCP.P5)
adcChannel7 = AnalogIn(mcp, MCP.P7) #channel 7 is measuring solar panel voltage

windmillDriverPlus = 1 #pins connected to BJT H bridges driving windmills
windmillDriverMinus = 7
pi = pigpio.pi()
pi.set_mode(windmillDriverPlus, pigpio.OUTPUT)
pi.set_mode(windmillDriverMinus, pigpio.OUTPUT)
wid = 0
drivingWindmills = False

num_neopixels = 97
reservoir_range_lower = 0
reservoir_range_upper = 7
city_range_lower = 8
city_range_upper = 94
fuel_cell_range_lower = 95
fuel_cell_range_upper = 96
pixels = neopixel.NeoPixel(board.D12, num_neopixels, auto_write = False)

def driveWindmills(frequency):
    global wid
    global drivingWindmills
    global windmillDriverPlus
    global windmillDriverMinus
    global pi

    halfCyclePeriod = 1/(2 * frequency)
    halfCyclePeriod = halfCyclePeriod  * (10**6) #convert to microseconds
    square = []

    #                          ON       OFF    MICROS
    square.append(pigpio.pulse(1<<windmillDriverPlus, 1<<windmillDriverMinus, halfCyclePeriod))
    square.append(pigpio.pulse(1<<windmillDriverMinus,1<<windmillDriverPlus, halfCyclePeriod))
    pi.wave_add_generic(square)
    wid = pi.wave_create()

    if wid >= 0:
        pi.wave_send_repeat(wid)
        drivingWindmills = True

def stopWindmills():
    global drivingWindmills
    global wid
    global pi

    if drivingWindmills:
        pi.wave_tx_stop()
        pi.wave_delete(wid)
        drivingWindmills = False

def releaseResources():
    global pi
    pi.stop()

def getSolarPanelVoltage():
    global adcChannel7
    return adcChannel7.voltage

def getWindmillVoltages():
    global adcChannel1
    global adcChannel2
    global adcChannel3
    global adcChannel4
    global adcChannel5

    return [adcChannel1.voltage, adcChannel2.voltage, adcChannel3.voltage, adcChannel4.voltage, adcChannel5.voltage]

#LED control code, colour must be inputted as list of three integers between 0 and 255 (i.e. setCityLEDs([255,255,0]))
def setCityLEDs(colour):
        global pixels
        global city_range_lower
        global city_range_upper

        for i in range(city_range_lower, city_range_upper + 1):
                pixels[i] = colour

        pixels.show()

def setReservoirLEDs(colour):
        global pixels
        global reservoir_range_lower
        global reservoir_range_upper

        for i in range(reservoir_range_lower, reservoir_range_upper + 1):
                pixels[i] = colour
        
        pixels.show()

def setFuelCellLEDs(colour):
        global pixels
        global fuel_cell_range_lower
        global fuel_cell_range_upper

        for i in range(fuel_cell_range_lower, fuel_cell_range_upper + 1):
                pixels[i] = colour

        pixels.show()