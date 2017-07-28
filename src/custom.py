#define class definitions here for custom weapons, soldiers, and factions
#also define how to intialize soldiers in here

import numpy as np
import resources

def initSoldiers(): #define here how you'd like to initialize both armies
    resources.Battlefield.main.initLine(Seal,100,[0,0,0],[0,1,0])
    resources.Battlefield.main.initLine(Redcoat,300000,[500,0,0],[1,0,0],500)

class M240(resources.Weapon):
    fireRate=16 #Hz
    height=np.array((0,0,.7)) #how high above the ground the gun is held

    inherentSpread=0.00125 #spread from where you're aiming (estimated from article)
    recoilSpread=0.002 #the maximum recoil attained by a gun as you fire endlessly
    recoilBase=.5 #how quickly the gun reaches its maximum recoil

    maxRange=2000 #don't try to shoot beyond this range
    averageSpeed=650 #this should be slightly slower than muzzle velocity
                #THIS DOESNT AFFECT DAMAGE AT ALL

    #damage stuff
    falloffBuffer=.5 #this determines how long bullet will go before starting falloff
    maxDamage=.4 #damage when you're standing right in front of the gun
    minDamage=.15 #damage when the gun is beyond its max range... ie at terminal velocity
    dropOff=1500 #every x meters, the damage done by the gun is halved
    multiKillDamage=.18 #if it hits someone and deals at least this much damage, hit the next person and deal this much less damage

class SniperRifle(resources.Weapon):
    fireRate=1 #Hz
    height=np.array((0,0,.7)) #how high above the ground the gun is held

    inherentSpread=0.0001 #spread from where you're aiming (estimated from article)
    recoilSpread=0#0.005 #the maximum recoil attained by a gun as you fire endlessly
    recoilBase=.5 #how quickly the gun reaches its maximum recoil

    maxRange=5000 #don't try to shoot beyond this range
    averageSpeed=1500 #this should be slightly slower than muzzle velocity
                #THIS DOESNT AFFECT DAMAGE AT ALL

    #damage stuff
    falloffBuffer=2 #this determines how long bullet will go before starting falloff
    maxDamage=2 #damage when you're standing right in front of the gun
    minDamage=.5 #damage when the gun is beyond its max range... ie at terminal velocity
    dropOff=1500 #every x meters, the damage done by the gun is halved
    multiKillDamage=.2 #if it hits someone and deals at least this much damage, hit the next person and deal this much less damage


class Musket(resources.Weapon):
    fireRate=1/15 #one shot per 15 seconds
    height=np.array((0,0,.7))

    inherentSpread=0.0136986301369863 #this is what i estimated based on some articles about the musket
    recoilSpread=0 #umm for the brits, they have such low fire rate that recoil isnt an issue
    recoilBase=.5 #does nothing when recoilSpread is 0

    maxRange=120 #i think this is what david said was the max range?
    averageSpeed=200

    falloffBuffer=1.2
    maxDamage=1
    minDamage=.1
    dropOff=100
    multiKillDamage=2 #this weapon can't multikill because the bullet breaks up on impact


class SealFaction(resources.Faction):
    id=0

    enemy=[1]


class BritFaction(resources.Faction):
    id=1

    enemy=[0]


class Seal(resources.Soldier):

    weapon=M240
    color=np.array((-1,-1,255),dtype=np.int32)*15/255 #color *alpha

    def __init__(self,coords):
        super().__init__(coords,SealFaction)

class SealSniper(Seal):

    weapon=SniperRifle
    distanceacc=0


class Redcoat(resources.Soldier):
    
    weapon=Musket
    color=np.array((255,-3,-3),dtype=np.int32)*5/255
    #health=.1

    def __init__(self,coords):
        super().__init__(coords,BritFaction)
