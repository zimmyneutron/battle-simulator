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
        height=.1 #how high above the ground the gun is held

        inherentSpread=0.01 #spread from where you're aiming
        recoilSpread=1.25 #the maximum recoil attained by a gun as you fire endlessly
        recoilBase=.5 #how quickly the gun reaches its maximum recoil

        #maxDistance=1800 #don't check anything beyond this distance

        #damage stuff
        falloffBuffer=.8 #this determines how long bullet will go before starting falloff
        maxDamage=.4 #damage when you're standing right in front of the gun
        minDamage=.18 #damage when the gun is beyond its max range... ie at terminal velocity
        dropOff=500 #every x meters, the damage done by the gun is halved
        multiKillDamage=.07 #if it hits someone and deals at least this much damage, hit the next person and deal this much less damage

        def getDamage(distance): #damage based on how far away the target is... kill after 1 damage
            return np

    global SEAL
    class SEAL(Soldier):

        weapon=M240
