import time
import thumby
import math


# todo, suite games with beep and intelligent level
# think of the day



# BITMAP: width: 8, height: 8 skull
bitmap0 = bytearray([0,60,254,51,255,51,254,60])

# BITMAP: width: 8, height: 8 #drop
bitmap1 = bytearray([0,120,254,219,223,219,254,120])
# Set the FPS (without this call, the default fps is 30)

# BITMAP: width: 36, height: 7 tiny #numbers
bitmapNumbers = bytearray([36,62,32,0,50,42,38,0,34,42,54,0,14,8,62,0,46,42,18,0,62,42,58,0,50,10,6,0,62,42,62,0,14,10,62,0])

thumby.display.setFPS(60)
# BITMAP: width: 16, height: 16 #planes
bitmapPlane = bytearray([4,4,12,12,0,78,27,21,27,78,0,12,12,4,4,0,
           16,16,0,16,56,16,0,16,16,0,0,0,2,3,2,0])


planeSprite = thumby.Sprite(16,16,bitmapPlane,(thumby.display.width-16)/2,0)

planeNumbers = thumby.Sprite(36,8,bitmapNumbers,(thumby.display.width-36)/2,2)


yStable = int(thumby.display.height/2);
yL = yStable
yR = yL;

yTop = -20 # - 20
yBottom = thumby.display.height-yTop
col=1

while(1):

    t0 = time.ticks_ms()   # Get time (ms)

    thumby.display.fill(0) # Fill canvas to black
    thumby.display.drawSprite(planeNumbers)


    if thumby.buttonR.pressed() :
        if yL >= yTop:
            yL-=1
            yR+=1
    elif thumby.buttonL.pressed():
          if yR >= yTop:
            yR-=1
            yL+=1
    elif yL < yStable:
        yL+=1
        yR-=1
    elif yR < yStable:
        yR+=1
        yL-=1

    thumby.display.drawLine(0, yL, 72, yR, col)

    # thumby.display.drawSprite(planeSprite)


    # Display the bitmap using bitmap data, position, and bitmap dimensions
   
   
    # Center the sprite using screen and bitmap dimensions and apply bob offset
    # thumbySprite.x = int((thumby.display.width/2) - (32/2))
    # thumbySprite.y = int(round((thumby.display.height/2) - (32/2) + bobOffset))

    # thumby.display.drawSprite(thumbySprite)
    thumby.display.update()
