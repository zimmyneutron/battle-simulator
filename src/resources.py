#resources for defining battle mechanics, etc

import numpy as np
import params

class Soldier(object): #any soldier

    weapon=None #the static weapon class defining stats
    size=np.array([]) #height,width
    health=1 #default 1 hp

    color=(0,0,0)

    def __init__(self,coords,faction):

        self.coords=np.array(coords)
        self.faction=faction

        self.hp=self.health

class DeadBody(object): #a dead body lying on the battlefield

    radius=0 #if you're within this radius of the body, you have to slow down to avoid it
    slowFactor=0 #for each body you have to jump over, you lose this much speed

    color=(0,0,0)

    def __init__(self,coords):
        self.coords=np.array(coords)

    def getSlowFactor(self): #for convenience, because you multiply by this not the raw factor
        return 1-self.slowFactor

    def collide(self,coords): #determine whether coords are within radius of this
        dr=coords-self.coords
        return np.sqrt(np.dot(dr,dr))<=self.radius

class Weapon(object): #base weapon class..make it static

    fireRate=0 #Hz
    inherentSpread=0 #radians of spread from where you're aiming
    kickSpread=0 #radians of spread that results from rapid fire (added to inherent)
    
    def getDamage(distance): #calculate damage based on the distance from the target
        return 0

    def getMultiKill(distance): #if it can kill multiple people with one shot, define it here
        return 1 #how many people it can kill at this distance


class Faction(object): #basically a number telling you which side you're on..not much to it

    id=-1 #give it an id number
    ally=[] #list of allied factions
    enemy=[] #list of enemy factions

    @classmethod
    def isEnemyFaction(self,fac):
        if (fac is not None) and (self.enemy.count(fac.id) or fac.enemy.count(self.id)):
            return True
        return False

    @classmethod
    def isEnemySoldier(self,soldier):
        return self.isEnemyFaction(soldier.faction)

    @classmethod
    def isAlliedFaction(self,fac):
        if (fac is not None) and (self.id==fac.id or self.ally.count(fac.id) or fac.ally.count(self.id)):
            return True
        return  False

    @classmethod
    def isAlliedSoldier(self,soldier):
        return self.isAlliedFaction(soldier.faction)

class Battlefield(object): #this is the operating are for all the soldiers


    def __init__(self):
        
        self.terrain=None #maybe later add a terrain for varrying gradients and travel speeds?
        self.soldiers=dict() #positional map of soldier positions
        self.dead=dict()  #positional map of dead bodies

    
    def getIndex(self,coords): #get the positional map index by coords
        return tuple(coords[i]-coords[i]%params.gridSize for i in range(2))

    def countDeadBodies(self,coords): #count dead bodies at coords
        block=self.dead.get(self.getIndex(coords))
        if block is None:
            return 0
        n=0
        for body in block: #this is a list of bodies
            if body.collide(coords):
               n+=1

        return n






    
