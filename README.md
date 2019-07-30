# Wattown
Program for Raspberry Pi on Wattown Energy demonstrator written in Python

The board uses Neopixels, 'Blowlight' light up toy windmills, photovoltaic panels and a water electrolyser. These are used to model a city of the future made up of a hydroelectric dam, windmills, solar panels, a 'fuel cell' and many city buildings.

The board is represented by the WattownBoard class in the Python program which contains objects representing each of the city components above. The WattownBoard class additionally provides some extra methods for the simulations to use as well as inherting the python Thread class in order to run 'animations' on the board. Any component which needs to be animated on the board must provide an update() method which can be called by the WattownBoard class.
