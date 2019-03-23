import time

import pigpio

GPIO_plus = 1
GPIO_minus = 7

square = []

#                          ON       OFF    MICROS
square.append(pigpio.pulse(1<<GPIO_plus, 1<<GPIO_minus, 125000))
square.append(pigpio.pulse(1<<GPIO_minus,1<<GPIO_plus, 125000))

pi = pigpio.pi() # connect to local Pi

pi.set_mode(GPIO, pigpio.OUTPUT)

pi.wave_add_generic(square)

wid = pi.wave_create()

if wid >= 0:
   pi.wave_send_repeat(wid)
   time.sleep(60)
   pi.wave_tx_stop()
   pi.wave_delete(wid)

pi.stop()