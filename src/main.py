#main for running the battle

import params #the numbers you want for everything
import resources #the  base classes for everything in the battle
import custom #user defined weapons, soldiers, etc that rely on resources


battlefield=resources.Battlefield() #initialize the battlefield
custom.initSoldiers() #load up the soldiers as defined in custom.py

battlefield.saveFrame(0)
for i in range(1,10):
    battlefield.runFrame()
    battlefield.saveFrame(i)
