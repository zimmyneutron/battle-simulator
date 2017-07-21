#resources for defining battle mechanics, etc

import numpy as np
import params

X=np.array([1,0,0])
Y=np.array([0,1,0])
Z=np.array([0,0,1])

def gauss(std): #sample gaussian distribution with standard deviation std
    if std<=0:
        return  0
    return np.random.normal(0,std)

class Soldier(object): #any soldier

    weapon=None #the static weapon class defining stats
    size=np.array([0,0],dtype=np.float) #radius, height 
    health=1 #default 1 hp
    distanceacc = 1e-4 #inaccuracy due to distance
    maxRecoil = 10
    #maxDeviation = 2

    color=(0,0,0)

    def __init__(self,coords,faction):

        self.coords=np.array(coords)
        self.faction=faction

        self.hp=self.health
        self.recoil = 0

    def update(self):
        if(self.recoil != 0):
            self.recoil -= 1

    def findEnemy():
        pass

    def shoot(self, target):
        distanceDeviation = np.power(np.linalg.norm(target.coords-self.coords),1) * self.distanceacc
        dAcc = gauss(distanceDeviation); #inaccuracy due to distance
        dTheta = np.random.uniform(0, 2 * np.pi)

        recoilDeviation = -self.weapon.recoilSpread * np.power(self.weapon.recoilBase, self.recoil) + self.weapon.recoilSpread

        mAcc = gauss(self.weapon.inherentSpread * recoilDeviation); #inaccuracy due to mechanical details
        mTheta = np.random.uniform(0, 2 * np.pi)
        rAcc = gauss(recoilDeviation)
        rTheta = np.random.uniform(0, 2 * np.pi)

        #now calculate the vectors

        displacementVector = target.coords - self.coords
        initialUnitVector = displacementVector / np.linalg.norm(displacementVector)

        azimuth=np.arctan2(initialUnitVector[1],initialUnitVector[0])+np.pi/2 #the x,y angle of the initialUnitVector vector
        refX=np.array([X[0]*np.cos(azimuth)-X[1]*np.sin(azimuth),X[0]*np.sin(azimuth)+X[1]*np.cos(azimuth),0]) #the x axis rotated along the initialUnitVectoration
        refY=np.cross(initialUnitVector,refX) #the y axis rotated up to the initialUnitVectoration

        aimVector = initialUnitVector + dAcc*(np.cos(dTheta)*refX+np.sin(dTheta)*refY) + mAcc*(np.cos(mTheta)*refX+np.sin(mTheta)*refY) + rAcc*(np.cos(rTheta)*refX+np.sin(rTheta)*refY)
        aimUnitVector = aimVector / np.linalg.norm(aimVector)
        #print(aimUnitVector)
        self.weapon.shootAt(self.coords, aimUnitVector, self.faction) #also pass in your faction so you don't shoot an ally (or yourself)
        self.recoil += 2
        if(self.recoil > self.maxRecoil):
            self.recoil = self.maxRecoil

    def inHitbox(self,offset2d): #check whether the 2d offset vector is inside your hitbox or not
        return offset2d[0]<=self.size[0] and offset2d[1]<=self.size[1] #that's all it should take because we're checking radius, not displacement

    def damage(self,d): #deal damage to the soldier (ignore if negative)
        if d>0:
            self.hp-=d

class DeadBody(object): #a dead body lying on the battlefield

    radius=0 #if you're within this radius of the body, you have to slow down to avoid it
    slowFactor=params.bodySlowFactor #for each body you have to jump over, you lose this much speed

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
    height=np.array((0,0,0)) #how high above the ground the gun is held
    
    inherentSpread=0 #spread from where you're aiming
    distanceSpread=0 #spread as a function of distnace squared (should be very small... ie 10e-7
    recoilSpread=0 #the maximum recoil attained by a gun as you fire endlessly
    recoilBase=.5 #how quickly the gun reaches its maximum recoil

    #maxDistance=1800 #don't check anything beyond this distance

    #damage stuff
    pointBlankDamage=0 #how much damage it does at 0 range (make this more than maxDamage..the greater it is, the further out the gun will deal max damage)
    maxDamage=0 #damage when you're standing right in front of the gun
    minDamage=0 #damage when the gun is beyond its max range... ie at terminal velocity
    dropOff=0 #every x meters, the damage done by the gun is halved
    multiKillDamage=0 #if it hits someone and deals at least this much damage, hit the next person and deal this much less damage
                        #quick side note: if multiKillDamage is 0, the bullet will hit every single person in a line 

    @classmethod
    def getDamage(self,distance,multiKill=0): #get the damage dealt to a person when shot from a ceratain distance
        d=self.pointBlankDamage*np.exp2(-distance/self.dropOff)#+self.minDamage-multiKill
        if d<self.minDamage:
            d=self.minDamage
        #d-=multiKill #if activated here, this will ALLOW massive collats at close range
        if d>self.maxDamage:
            return self.maxDamage
        d-=multiKill #if activated here, this will PREVENT massive close range collats 
        return d

    @classmethod
    def shootAt(self,source,direction,faction): #shoot from source (your soldier's coords) in direction (with recoil included)

        #first loop through the grid and if it's occupied, check the soldiers inside
        flatTrajectory=direction[:2] #direction is 3d, but this is the trajectory along the flat map (no z component)
        start=source#+np.array([0,0,self.height]) #start at their feet plus the weapon height

        #split up the hashes between x2-x1 and y2-y1 
        hashes=set() #each t value for which the bullet passes into a new grid box
        
        for i in range(2):
            m=(direction[i])#*params.maxBulletDistance/params.gridSize)
            for coord in range(Battlefield.gridify(start[i]),Battlefield.gridify(start[i]+direction[i]*params.maxBulletDistance),params.gridSize): 
                hashes.add((coord-start[i])/m )
                
        hashes=list(hashes)
        hashes.sort()

        #now duplicate the starting and ending spots 
        if hashes[0]!=hashes[1]: #don't double count the first one
            hashes.insert(0,hashes[0])


        multiKill=0 #track the number of people hit
        for t in hashes: #now visit each grid
            z=start[2]+direction[2]*t #the z height upon entering this block
            if not (params.minBulletHeight<=z<=params.maxBulletHeight) and t!= hashes[0]: #dont check backwards
                break #exit the loop, forget the bullet

            #else check for collisions inside the grid box
            gridBox=Battlefield.main.soldiersMap.get(Battlefield.main.getIndex(start+direction*t))
            if gridBox: #if it's occupied
                gridBox.sort(key=lambda soldier: np.linalg.norm(soldier.coords-start)) #sort the list from closest to furthest 
                for s in gridBox: #for each soldier inside
                    if faction.isEnemySoldier(s): #don't shoot an ally or yourself
                        displacelent=s.coords-start
                        displacementDotDirection=np.dot(displacement,direction)
                        offsetVector=direction-displacementDotDirection/np.dot(displacement,displacement)*displacement #this is the shortest distance between the direction and displacement vectors
                        offset3d=offsetVector/np.linalg.norm(offsetVector)*np.linalg.norm(displacement)**2*np.linalg.norm(offsetVector)/displacementDotDirection #the 3d offset relative to soldier's feet
                        offset2d=(np.sqrt(offset3d[0]**2+offset3d[1]**2),offset3d[2])#the 2d offset of radius, height instead of x y z
                        if s.inHitbox(offset2d): #if it hits the soldier
                            damage=self.getDamage(np.linalg.norm(s.coords-start),multiKill) #calculate the damage, based on how many targets have already been hit by bullet
                            s.damage(damage) #deal damage to the soldier
                            if damage>self.multiKillDamage: #if it deals enough damage to hit another person
                                multiKill+=self.multiKillDamage
                            else:
                                return None #exit the loop if it can't hit another person
                            
                            
            

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

    size=((-2000,2000),(-2000,2000)) #bounds of the battlefield
    main=None #the battlefield reference

    def __init__(self):

        self.terrain=None #maybe later add a terrain for varrying gradients and travel speeds?

        self.soldiersList=list() #list of the soldiers for looping
        self.deadList=list() #list of bodies for looping
        self.soldiersMap=dict() #positional map of soldier positions
        self.deadMap=dict()  #positional map of dead bodies

        self.__class__.main=self

    @classmethod
    def getIndex(self,coords): #get the positional map index by coords
        return tuple(self.gridify(coords[i]) for i in range(2))

    @staticmethod
    def gridify(num):
        return int(num-num%params.gridSize)

    def countDeadBodies(self,coords): #count dead bodies at coords
        block=self.dead.get(self.getIndex(coords))
        if block is None:
            return 0
        n=0
        for body in block: #this is a list of bodies
            if body.collide(coords):
               n+=1

        return n

def test():
    s=Soldier((0,0,0),0)
    b=Soldier((10,0,0),1)
    s.weapon=Weapon
    s.shoot(b)
