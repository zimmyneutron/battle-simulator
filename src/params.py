#this sets all the parameters for the battle
import numpy as np

#cool stuff you can edit
bodySlowFactor=.2 #each body you have to climb/jump over slows you by this percent


#technical stuff for controlling gameflow
gridSize=50 #how large each grid square is for the positional maps (small=less soldiers/square, more squares; large=more soldiers in fewer squares)
maxBulletDistance=1800 #how long to track a bullet before giving up
maxBulletHeight=5 #meters height before giving up
minBulletHeight=0 #meters height before hitting the ground

#classes for soldiers, guns, etc.  Do it inside initClasses()
def initClasses():

    global M240
    class M240(Weapon):
        fireRate=16 #Hz
        inherentSpread=.01 #spread from the design of the gun

        def getDamage(distance): #damage based on how far away the target is... kill after 1 damage
            return np

    global SEAL
    class SEAL(Soldier):

        weapon=M240
