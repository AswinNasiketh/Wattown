#module to store simulation parameters and LED colour values

#1GW = 0.1 units
SUNNY_DAY_SOLAR_GENERATION = 1.28 #UK solar power capacity = 12.8GW
CLOUDY_DAY_SOLAR_GENERATION = 0.64 #half max capacity for cloudy day
MAX_WIND_POWER_GENERATION = 2 #UK wind power capacity = 20.7GW

MAX_CONSUMPTION = 3.4 #UK max power demand on 06/04/19 was 34GW
MIN_CONSUMPTION = 2.46 #UK min power demand on 06/04/19 was 24.6GW http://gridwatch.co.uk/

SIM_WAKEUP_TIME = 6 #6AM
SIM_SLEEP_TIME = 20 #8PM

RESERVOIR_RECHARGE_RATE = 5

LED_WATER_BLUE = (94,155,255)
LED_CITY_LIGHTS_YELLOW = (163, 145, 44)
LED_RED_DIM = (100, 0 , 0)
LED_YELLOW_MAX = (130, 130, 66)
LED_BLUE_MAX = (94, 193, 255)
LED_GREEN_BRIGHT = (97, 255, 94)