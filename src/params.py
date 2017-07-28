#this sets all the parameters for the battle
import numpy as np

battleName="semiRealistic" #the folder for saving battle results (no slashes)

#cool stuff you can edit
bodySlowFactor=.2 #each body you have to climb/jump over slows you by this percent
battlefieldBounds=((-100,2000),(-800,800)) #xmin, xmax, ymin, ymax for the battlefield size
pixelDensity=5 #this tells you how many meters each pixel represents for drawing the map
backgroundColor=(30,180,50) #the background color of the pictures (green grass by default)
bulletColor=(255,255,255) #set to a color code, or None to not draw bullets

#technical stuff for controlling gameflow
gridSize=50 #how large each grid square is for the positional maps (small=less soldiers/square, more squares; large=more soldiers in fewer squares)
maxBulletDistance=1800 #how long to track a bullet before giving up
maxBulletHeight=1.6 #if the bullet is above this height don't check for collisions
minBulletHeight=0 #meters height before hitting the ground
imageFrameZeros=8 #how many digits should be saved for image numbers
simulationFramerate=16 #how many simulation frames occur each second
gravitationalAcceleration=9.8 #gravity
targetSelectionIterations=15 #randomly check this many enemies to find a close target
