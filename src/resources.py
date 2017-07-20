#resources for defining battle mechanics, etc

import numpy as np
import params

X=np.array([1,0,0])
Y=np.array([0,1,0])
Z=np.array([0,0,1])

class Soldier(object): #any soldier

    weapon=None #the static weapon class defining stats
    size=np.array([0,0],dtype=np.float) #height,width
    health=1 #default 1 hp
    distanceacc = .0005 #inaccuracy due to distance
    maxRecoil = 10
    #maxDeviation = 2

    color=(0,0,0)

    def __init__(self,coords,faction):

        self.coords=np.array(coords)
        self.faction=faction

        self.hp=self.health
        self.recoil = 0

    def update(self):
        if(recoil != 0):
            self.recoil -= 1

    def findEnemy():
        pass

    def shoot(self, target):
        distanceDeviation = np.power(np.linalg.norm(target.coords-self.coords),2) * self.distanceacc
        dAcc = np.random.normal(0, distanceDeviation); #inaccuracy due to distance
        dTheta = np.random.uniform(0, 2 * np.pi)

        recoilDeviation = -self.weapon.recoilSpread * np.power(self.weapon.recoilBase, self.recoil) + self.weapon.recoilSpread

        mAcc = np.random.normal(0, self.weapon.inherentSpread * recoilDeviation); #inaccuracy due to mechanical details
        mTheta = np.random.uniform(0, 2 * np.pi)
        rAcc = np.random.normal(0, recoilDeviation)
        rTheta = np.random.uniform(0, 2 * np.pi)

        #now calculate the vectors

        displacementVector = target.coords - self.coords
        initialUnitVector = displacementVector / np.linalg.norm(displacementVector)

        azimuth=np.arctan2(initialUnitVector[1],initialUnitVector[0])+np.pi/2 #the x,y angle of the initialUnitVector vector
        refX=np.array([X[0]*np.cos(azimuth)-X[1]*np.sin(azimuth),X[0]*np.sin(azimuth)+X[1]*np.cos(azimuth),0]) #the x axis rotated along the initialUnitVectoration
        refY=np.cross(initialUnitVector,refX) #the y axis rotated up to the initialUnitVectoration

        aimVector += dAcc*(np.cos(dTheta)*refX+np.sin(dTheta)*refY) + mAcc*(np.cos(mTheta)*refX+np.sin(mTheta)*refY) + rAcc*(np.cos(rTheta)*refX+np.sin(rTheta)*refY)
        aimUnitVector = aimVector / np.linalg.norm(aimVector)

        self.weapon.shootAt(self.coords, aimUnitVector)
        self.recoil += 2
        if(recoil > maxRecoil):
            recoil = maxRecoil

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
    inherentSpread=0 #spread from where you're aiming
    distanceSpread=0 #spread as a function of distnace squared (should be very small... ie 10e-7
    recoilSpread=0 #the maximum recoil attained by a gun as you fire endlessly
    recoilBase=.5 #how quickly the gun reaches its maximum recoil

    #damage stuff
    pointBlankDamage=0 #how much damage it does at 0 range (make this more than maxDamage..the greater it is, the further out the gun will deal max damage)
    maxDamage=0 #damage when you're standing right in front of the gun
    minDamage=0 #damage when the gun is beyond its max range... ie at terminal velocity
    dropOff=0 #every x meters, the damage done by the gun is halved
    multiKillDamage=0 #if it hits someone and deals at least this much damage, hit the next person and deal this much less damage

    @classmethod
    def getDamage(self,distance,multiKill=0): #get the damage dealt to a person when shot from a ceratain distance
        d=self.pointBlankDamage*np.exp2(-distance/self.dropOff)+self.minDamage-multiKill
        if d>self.maxDamage:
            return self.maxDamage
        return d

    @classmethod
    def shootAt(self,source,direction): #shoot from source (your soldier's coords) in direction (with recoil included)
        flatTrajectory=direction[:2] #direction is 3d, but this is the trajectory along the flat map (no z component)

        

    #def expDamage(maxDamage,dropOff,distance): #do damage that halves every dropOff, with maxDamage at a range of 0 meters
    #    return maxDamage*np.exp2(-distance/dropOff)

    #def getMultiKill(distance): #if it can kill multiple people with one shot, define it here
    #    return 1 #how many people it can kill at this distance


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

    size=((-2000,2000),(-2000,2000)) #

    def __init__(self):

        self.terrain=None #maybe later add a terrain for varrying gradients and travel speeds?

        self.soldiersList=list() #list of the soldiers for looping
        self.deadList=list() #list of bodies for looping
        self.soldiersMap=dict() #positional map of soldier positions
        self.deadMap=dict()  #positional map of dead bodies


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
