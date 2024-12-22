import time
import thumby
import math


# BITMAP: width: 16, height: 16
bitmap0 = bytearray([28,34,65,145,43,70,4,24,24,4,6,3,129,65,34,28,
           0,0,0,1,2,12,16,32,32,16,12,2,1,0,0,0])

# BITMAP: width: 8, height: 8 skull
bitmap1 = bytearray([0,60,254,51,255,51,254,60])

# BITMAP: width: 8, height: 8 devil
bitmap2 = bytearray([0,102,249,204,252,204,249,102])
# BITMAP: width: 8, height: 8 devils 2
bitmap3 = bytearray([0,102,217,204,124,204,217,102])

# Make a sprite object using bytearray (a path to binary file from 'IMPORT SPRITE' is also valid)
thumbySprite = thumby.Sprite(8, 8, bitmap3)



import thumby


# Set the FPS (without this call, the default fps is 30)
thumby.display.setFPS(60)

cpt=0
fontWidth=5
fontHeight=7
colorWhite=1

while(1):

    colorFront=colorWhite
    fontTimer = 10

    thumby.display.fill(0) # Fill canvas to black
    thumby.display.setFont("/lib/font5x7.bin", fontWidth, fontHeight, 1)
    
    bobRate = 250 # Set arbitrary bob rate (higher is slower)
    bobRange = 1  # How many pixels to move the sprite up/down (-5px ~ 5px)
    t0 = time.ticks_ms()   # Get time (ms)

    if cpt<fontTimer:
        thumby.display.drawText("Luv Poulet", 0, 0, colorFront)
        cpt=cpt+1
    else:
        cpt=cpt+1
        thumby.display.drawText("By JF", thumby.display.width-7*fontWidth, thumby.display.height-fontHeight, colorFront)
        if cpt > fontTimer*2:
            cpt=0

    # Calculate number of pixels to offset sprite for bob animation
    bobOffset = math.sin(t0 / bobRate) * bobRange

    # Center the sprite using screen and bitmap dimensions and apply bob offset
    thumbySprite.x = int((thumby.display.width/2) - (8/2))
    thumbySprite.y = int(round((thumby.display.height/2) - (8/2) + bobOffset))

    # Display the bitmap using bitmap data, position, and bitmap dimensions
    thumby.display.drawSprite(thumbySprite)
    thumby.display.update()

