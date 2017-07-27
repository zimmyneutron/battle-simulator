#this sets all the parameters for the battle
import numpy as np

battleName="testBattle" #the folder for saving battle results (no slashes)

#cool stuff you can edit
bodySlowFactor=.2 #each body you have to climb/jump over slows you by this percent
battlefieldBounds=((-100,2000),(-800,800)) #xmin, xmax, ymin, ymax for the battlefield size
pixelDensity=5 #this tells you how many meters each pixel represents for drawing the map
backgroundColor=(30,180,50) #the background color of the pictures (green grass by default)

#technical stuff for controlling gameflow
gridSize=50 #how large each grid square is for the positional maps (small=less soldiers/square, more squares; large=more soldiers in fewer squares)
maxBulletDistance=1800 #how long to track a bullet before giving up
maxBulletHeight=1.6 #meters height before giving up
minBulletHeight=0 #meters height before hitting the ground
imageFrameZeros=8 #how many digits should be saved for image numbers
simulationFramerate=16 #how many simulation frames occur each second
