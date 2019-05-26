import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
spi = busio.SPI(clock=board.SCK_1, MISO=board.MISO_1, MOSI=board.MOSI_1)
cs = digitalio.DigitalInOut(board.D16)
mcp = MCP.MCP3008(spi, cs)

channel = AnalogIn(mcp, MCP.P0)

import time
while True:
    print('Raw ADC Value: ', channel.value)
    print('ADC Voltage: ' + str(channel.voltage) + 'V')
    time.sleep(0.5)