#resources for defining battle mechanics, etc

import numpy as np
import params
import pygame #for graphics
import os

import random

pygame.init()

X=np.array([1,0,0])
Y=np.array([0,1,0])
Z=np.array([0,0,1])

def gauss(std): #sample gaussian distribution with standard deviation std
    if std<=0:
        return  0
    return np.random.normal(0,std)

class Soldier(object): #any soldier

    weapon=None #the static weapon class defining stats
    size=np.array([.25,1.5],dtype=np.float) #radius, height
    health=1 #default 1 hp
    distanceacc = 1e-5 #inaccuracy due to distance
    maxRecoil = 20
    #maxDeviation = 2

    color=(0,0,0,0) #rgba

    def __init__(self,coords,faction):

        self.coords=np.array(coords)
        self.faction=faction #make sure this is a Faction class, not an int ID number

        Battlefield.main.addSoldier(self)

        self.hp=self.health
        self.recoil = 0
        self.timesHit=0

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

        mAcc = gauss(self.weapon.inherentSpread); #inaccuracy due to mechanical details
        mTheta = np.random.uniform(0, 2 * np.pi)
        rAcc = gauss(recoilDeviation)
        rTheta = np.random.uniform(0, 2 * np.pi)

        #now calculate the vectors
        
        displacementVector = (target.coords + target.weapon.height) - (self.coords + self.weapon.height) #initial aim vector
        gravityDeflection = np.array((0,0,params.gravitationalAcceleration/2*(np.linalg.norm(displacementVector)/self.weapon.averageSpeed)**2)) #how much the bullet is defelected by gravity
        print(gravityDeflection)
        displacementVector -= gravityDeflection #shoot downward to mimic gravitational parabolic trajectory
        initialUnitVector = displacementVector / np.linalg.norm(displacementVector)

        azimuth=np.arctan2(initialUnitVector[1],initialUnitVector[0])+np.pi/2 #the x,y angle of the initialUnitVector vector
        refX=np.array([X[0]*np.cos(azimuth)-X[1]*np.sin(azimuth),X[0]*np.sin(azimuth)+X[1]*np.cos(azimuth),0]) #the x axis rotated along the initialUnitVectoration
        refY=np.cross(initialUnitVector,refX) #the y axis rotated up to the initialUnitVectoration

        aimVector = initialUnitVector + dAcc*(np.cos(dTheta)*refX+np.sin(dTheta)*refY) + mAcc*(np.cos(mTheta)*refX+np.sin(mTheta)*refY) + rAcc*(np.cos(rTheta)*refX+np.sin(rTheta)*refY)
        aimUnitVector = aimVector / np.linalg.norm(aimVector)

        #print(aimUnitVector)
        self.weapon.shootAt(self.coords + self.weapon.height + gravityDeflection, aimUnitVector, self.faction) #also pass in your faction so you don't shoot an ally (or yourself)

        self.recoil += 2
        if(self.recoil > self.maxRecoil):
            self.recoil = self.maxRecoil

    def inHitbox(self,offset2d): #check whether the 2d offset vector is inside your hitbox or not
        return offset2d[0]<=self.size[0] and offset2d[1]<=self.size[1] #that's all it should take because we're checking radius, not displacement

    def damage(self,d): #deal damage to the soldier (ignore if negative)
        if d>0:
            self.hp-=d
            #print("I used to be an adventurer like you until I took an arrow to the knee")
            #print(d)
            self.timesHit+=1

class DeadBody(object): #a dead body lying on the battlefield

    radius=0 #if you're within this radius of the body, you have to slow down to avoid it
    slowFactor=params.bodySlowFactor #for each body you have to jump over, you lose this much speed

    color=(0,0,0,0)

    def __init__(self,coords):
        self.coords=np.array(coords)

    def getSlowFactor(self): #for convenience, because you multiply by this not the raw factor
        return 1-self.slowFactor

    def collide(self,coords): #determine whether coords are within radius of this
        dr=coords-self.coords
        return np.sqrt(np.dot(dr,dr))<=self.radius

class Weapon(object): #base weapon class..make it static

    fireRate=0 #Hz
    height=np.array((0,0,0.)) #how high above the ground the gun is held


    inherentSpread=0 #spread from where you're aiming
    recoilSpread=0 #the maximum recoil attained by a gun as you fire endlessly
    recoilBase=.5 #how quickly the gun reaches its maximum recoil

    maxRange=0 #don't try to shoot beyond this range
    averageSpeed=0 #how fast the bullet travels "on average"... i'm thinkning make it like 80% of the muzzle velocity or something?

    #damage stuff
    falloffBuffer=0 #this determines how long bullet will go before starting falloff
    maxDamage=0 #damage when you're standing right in front of the gun
    minDamage=0 #damage when the gun is beyond its max range... ie at terminal velocity
    dropOff=0 #every x meters, the damage done by the gun is halved
    multiKillDamage=0 #if it hits someone and deals at least this much damage, hit the next person and deal this much less damage
                        #quick side note: if multiKillDamage is 0, the bullet will hit every single person in a line

    @classmethod
    def getDamage(self,distance,multiKill=0): #get the damage dealt to a person when shot from a ceratain distance
        d=self.falloffBuffer*np.exp2(-distance/self.dropOff)#+self.minDamage-multiKill
        if d<self.minDamage:
            d=self.minDamage
        #d-=multiKill #if activated here, this will ALLOW massive collats at close range
        if d>self.maxDamage:
            d= self.maxDamage
        d-=multiKill #if activated here, this will PREVENT massive close range collats
        return d

    @staticmethod
    def getSign(direction): #decide whether to multiply by negative 1 or not
        if direction>0:
            return 1
        else:
            return -1

    @classmethod
    def shootAt(self,source,direction,faction): #shoot from source (your soldier's coords) in direction (with recoil included)

        #first loop through the grid and if it's occupied, check the soldiers inside
        flatTrajectory=direction[:2] #direction is 3d, but this is the trajectory along the flat map (no z component)
        start=source#+np.array([0,0,self.height]) #start at their feet plus the weapon height

        #split up the hashes between x2-x1 and y2-y1
        hashes=[] #each t value for which the bullet passes into a new grid box
        grids=set()
        for i in range(2):
            m=(direction[i])#*params.maxBulletDistance/params.gridSize)
            for coord in range(Battlefield.gridify(start[i]),Battlefield.gridify(start[i]+direction[i]*self.maxRange),
                               self.getSign(m)*params.gridSize):
                fooIndex=Battlefield.getIndex(start+direction*(coord-start[i])/m)
                #if True or not grids.__contains__(fooIndex):
                hashes.append((coord-start[i])/m )
                    #grids.add(fooIndex)

        hashes.sort()
        '''
        i=0
        while i<len(hashes)-1:
            if Battlefield.getIndex(start+direction*hashes[i])==Battlefield.getIndex(start+direction*hashes[i+1]):
                hashes.pop(i+1)
            i+=1
            '''


        if hashes[0]==hashes[1]: #don't double count the first one
            hashes.pop(0)

        #for i in hashes:print(Battlefield.getIndex(start+direction*i))


        multiKill=0 #track the number of people hit
        for tIndex in range(len(hashes)-1): #now visit each grid
            
            t=(hashes[tIndex]+hashes[tIndex+1])/2 #ensure it's inside the block

            grindex=Battlefield.main.getIndex(start+direction*t) #the GRid INDEX but more fun to say 
            if grids.__contains__(grindex):
                next
            grids.add(grindex)

            #z=start[2]+direction[2]*t #the z height upon entering this block
            if start[2]+direction[2]*hashes[tIndex]<params.minBulletHeight:
                break #the bullet hit the ground, stop simulating
            elif start[2]+direction[2]*hashes[tIndex+1]>params.maxBulletHeight:
                continue #the bullet is above people's heads, don't bother checking this square
            #if not (params.minBulletHeight<=z<=params.maxBulletHeight) and t!= hashes[0]: #dont check backwards
                #break #exit the loop, forget the bullet

            #else check for collisions inside the grid box
            gridBox=Battlefield.main.soldiersMap.get(grindex)
            if gridBox: #if it's occupied
                gridBox.sort(key=lambda soldier: np.linalg.norm(soldier.coords-start)) #sort the list from closest to furthest
                for s in gridBox: #for each soldier inside
                    if faction.isEnemySoldier(s): #don't shoot an ally or yourself
                        displacement=s.coords-start
                        displacementDotDirection=np.dot(displacement,direction)
                        offsetVector=direction-displacementDotDirection/np.dot(displacement,displacement)*displacement #this is the shortest distance between the direction and displacement vectors
                        offset3d=offsetVector/np.linalg.norm(offsetVector)*np.linalg.norm(displacement)**2*np.linalg.norm(offsetVector)/displacementDotDirection #the 3d offset relative to soldier's feet
                        offset2d=(np.sqrt(offset3d[0]**2+offset3d[1]**2),offset3d[2])#the 2d offset of radius, height instead of x y z
                        #print(offset2d)
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

    
    main=None #the battlefield reference

    def __init__(self):

        self.terrain=None #maybe later add a terrain for varrying gradients and travel speeds?

        self.soldiersList=list() #list of the soldiers for looping
        self.deadList=list() #list of bodies for looping
        self.soldiersMap=dict() #positional map of soldier positions
        self.deadMap=dict()  #positional map of dead bodies
        self.factionMap=dict() #this lets you access a list of soldiers sorted by faction

        self.size=(np.array((params.battlefieldBounds[0][0],params.battlefieldBounds[1][0])),np.array(
                            (params.battlefieldBounds[0][1]-params.battlefieldBounds[0][0],
                             params.battlefieldBounds[1][1]-params.battlefieldBounds[1][0]))) #corner, and width/height

        self.filepath=""
        self.initNewBattle()

        self.__class__.main=self

    @classmethod
    def getIndex(self,coords): #get the positional map index by coords
        return tuple(self.gridify(coords[i]) for i in range(2))

    @staticmethod
    def gridify(num):
        return int(num-num%params.gridSize)

    #=============I'm actually going to change this to return slowness factor instead=======
    def countDeadBodies(self,coords): #count dead bodies at coords
        block=self.dead.get(self.getIndex(coords))
        if block is None:
            return 0
        n=0
        for body in block: #this is a list of bodies
            if body.collide(coords):
               n+=1

        return n

    def runFrame(self): #run one frame

        britList=[]
        sealList=[]
        
        for i in self.soldiersList:
            if i.faction.id==1:
                britList.append(i)
            else:
                sealList.append(i)

        print("shooting")
        for i in sealList:
            i.shoot(random.choice(britList))

        #clean
        print("cleaning")
        n=0
        for i in tuple(self.soldiersList):
            if i.hp<0:
                n+=1
                self.removeSoldier(i)
        print(n,"killed")

    #interface to add/remove soldiers/bodies from the map

    def addSoldierToMap(self,index,soldier): #add a soldier to the solder map grid
        if self.soldiersMap.get(index) is None:
            self.soldiersMap[index]=[soldier]
        else:
            self.soldiersMap[index].append(soldier)

    def removeSoldierFromMap(self,index,soldier): #remove the soldier from the square, and if empty, deallocate it
        if self.soldiersMap.get(index) is not None:
            sindex=self.soldiersMap[index].index(soldier)
            if sindex!=-1:
                self.soldiersMap[index].pop(sindex)

            if len(self.soldiersMap[index])==0: #remove the list from memory if it's empty
                self.soldiersMap.__delitem__(index)

    def addSoldier(self,soldier): #add a new soldier to the battlefield
        self.soldiersList.append(soldier)
        self.addSoldierToMap(self.getIndex(soldier.coords),soldier)
        factionList=self.factionMap.get(soldier.faction.id)
        if factionList is None:
            self.factionMap[soldier.faction.id]=[soldier]
        else:
            factionList.append(soldier)

    def removeSoldier(self,soldier): #remove the soldier when they distance
        sindex=self.soldiersList.index(soldier)
        if sindex!=-1:
            self.soldiersList.pop(sindex)
        self.removeSoldierFromMap(self.getIndex(soldier.coords),soldier)
        factionList=self.factionMap.get(soldier.faciton.id)
        if factionList is not None:
            sindex=factionList.index(soldier)
            if sindex!=-1:
                factionList.pop(sindex)

    #draw commands

    def getImageCoords(self,coords): #convert 2d/3d real world coords to image pixel coords
        return np.array((coords[:2]-self.size[0])/params.pixelDensity,dtype=np.int32)

    def max(self,color):
        return [i+(i>255)*(255-i)+(i<0)*(-i) for i in color]      

    def createImage(self): #return the surface of the battlefield picture
        size=self.getImageCoords(self.size[1]+self.size[0])
        surface=pygame.Surface(size)
        surface.fill(params.backgroundColor)

        s2=dict() #make it a dictionary of pixel colors
        n=0
        for i in self.soldiersList:
            c=tuple(self.getImageCoords(i.coords))
            pixel=s2.get(c)
            if pixel is None:
                s2[c]=np.array(i.color) #make sure its a new object
            else:
                s2[c]+=i.color
                n+=1
        print(len(self.soldiersList),len(s2),n)
        #now add in the pixel dictionary
        for coords, value in s2.items():
            try:
                surface.set_at(coords,self.max(surface.get_at(coords)[:3]+value))
            except:#Exception as e:
                pass

        '''
        s2=pygame.Surface(size)#the transparent surface
        s2.set_colorkey((0,0,0))
        #now draw the dead bodies

        for i in self.deadList:
            #surface.fill(i.color,(self.getImageCoords(i.coords),(2,2)))
            pass

        #now draw the soldiers
        for i in self.soldiersList:
            #surface.fill(i.color,(self.getImageCoords(i.coords),(2,2)))
            c=self.getImageCoords(i.coords)
            try:
                surface.set_at(c,self.max(surface.get_at(c)[:3]+i.color))
            except:
                pass
                '''
      
        return surface

    def saveFrame(self,frameNo): #generate the image and save it it to the filepath
        pygame.image.save(self.createImage(),self.filepath+"/frames/"+str(frameNo).zfill(params.imageFrameZeros)+".png")

    def initNewBattle(self):  
        append=0
        while os.path.exists("battles/"+params.battleName+bool(append)*(" ("+str(append)+")")):
            append+=1
        self.filepath="battles/"+params.battleName+bool(append)*(" ("+str(append)+")")
        os.makedirs(self.filepath+"/frames")
        
    #initialization functions for setting up soldiers in different shapes

    def initLine(self,soldier,number,start,direction,maxLength=2**31):
        direction=np.array(direction)
        for i in range(number):
            soldier(start+((i*2*soldier.size[0])%maxLength)*direction+int((i*2*soldier.size[0])/maxLength)*np.cross(direction,Z))



'''
def foo(): #draw the frame and save to file
    pygame.image.save(Battlefield.main.createImage(),"foo.png")

params.initClasses(Weapon,Faction,Soldier)

Battlefield()
#for i in range(100):
#    params.Seal([0,25-i/2,0])
    
Battlefield.main.initLine(params.Seal,100,[0,0,0],[0,1,0])
Battlefield.main.initLine(params.Redcoat,300000,[500,0,0],[1,0,0],500)


for x in range(10):
    for y in range(10):
        params.Redcoat([100+x/2,100+y/2,0])

s=params.Seal([0,0,0])
b=params.Redcoat([40,40.2,0])
b2=params.Redcoat([80,80.4,0])
for i in range(1000):
    s.shoot(b)
    s.update()
print("TOTAL HITS:",b.timesHit)
print("collats:",b2.timesHit)
b.timesHit=0
print("Now single tapping")
for i in range(1):
    if(i % 2 == 0):
        s.shoot(b)
    s.update()
print("TOTAL HITS:",b.timesHit)
'''
#foo()

