import pigpio

pi = pigpio.pi()
#setting windmill driver pins to digital low
pi.set_mode(1, pigpio.OUTPUT)
pi.set_mode(7, pigpio.OUTPUT)
pi.write(1, 0)
pi.write(7, 0)

#setting fuel cell driver pin to digital low
pi.set_mode(8, pigpio.OUTPUT)
pi.write(8, 0)

#release resources so demo code can have control over pins
pi.stop()