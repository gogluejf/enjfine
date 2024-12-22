import thumby
import math
import enjfine
import random

#effect to apply on sprite
class SpriteEffect():
    SHAKE = 0# will shake the sprite in quick movement
    FLASH = 1 # will flash a sprite by inverting the sprite colors 
    INVERT = 2 # invert the spirte color
    INVISIBLE = 3 #make the sprite invisible
    EXPLODE = 4 #make the an explosion of particles from the center of the sprite
    SPLASH = 5 #make splash effect of particles in a particular direction
    CIRCLE_WAVE = 6 #draw a circle around the central point that spread as a wave

#contain a box and sprite
#use the box to do animation ( sprite get update in drawer ready to display)
class SpriteBox(enjfine.BoxObj):
    
    #bitmap to load in sprite
    #dim: the sprite dimension 
    #bitmapMask : useful to draw black and white sprite while supporting transparence ( use if you plan having background)
    #collisionBoxOverride: if sprite dimension is not the box you want for physique, use collisionBoxOverride to override the collision box.  box.pt will be used for offset to the sprite box )
    #because screen is so mall and big sprite look better, the collisionBoxOverride is very useful to have big sprite with smaller collision box so the graphx and the gamplay still nice
    #nbFrame, how many frame the sprite have ( important for inverted frames )
    def __init__(self, bitmap, dim, bitmapMask = None, collisionBoxOverride = None, nbFrame = 1):

        super().__init__()

        self.debug = False #setting it to true will display the collision box
        self.__nbFrame = nbFrame
        self.__currentFrame = 0 #currentFrame of the animation
        self.__animateBps  = 0 # if set to a bps, will rotate the nbFrame according to this beat per second
        self.__invert = False
        
        
        self.box = enjfine.Box(enjfine.Point(), collisionBoxOverride.dim if collisionBoxOverride is not None else dim)
        self.spriteOffsetPt = collisionBoxOverride.pt if(collisionBoxOverride) else None

        key = -1 if bitmapMask is not None else 0 #all sprite set to black color has transparent, except when a mask is provided, in that case we set both color and the mask will set transparency 
        self.sprite = thumby.Sprite(dim.w, dim.h, bitmap + self.__invertBitMap(bitmap), 0, 0, key)
        self.spriteMask = thumby.Sprite(dim.w,dim.h,bitmapMask) if( bitmapMask is not None) else None #set mask if one is provided

       

    #use this method to change fraem, since it adapt both the mask and sprite for animation
    #it also keep track of the animation frame for proper couleur invertion effect
    def changeFrame(self, frame):
        self.sprite.setFrame(frame)
        if(self.spriteMask != None):
            self.spriteMask.setFrame(frame)
        self.__currentFrame = frame

    def Invert(self):
        self.sprite.setFrame(self.__nbFrame + self.__currentFrame)
        if(self.sprite.key != -1): self.sprite.key = 1
        self.__invert = True

    def Revert(self):
        self.sprite.setFrame(self.__currentFrame)
        if(self.sprite.key != -1): self.sprite.key = 0
        self.__invert = False

    #take a array of byte and invert them ( in thumby, we used it to invert  black and white into bitmaps)
    def __invertBitMap(self, bitmap):

        invertedBitmmap = []

        for c in range(len(bitmap)):
            invertedBitmmap.append(~bitmap[c] & 255)
            
        return bytearray(invertedBitmmap)

    def setAnimate(self, bps):
        self.__animateBps = bps
        self.__counter = 0
    
    def animate(self, animator):
        
        if(not self.__animateBps):
            return

        f = animator.getFramesIntervalFromBps(self.__animateBps)

        self.__counter += 1
        if(self.__counter >= f):
            self.__counter=0
            self.changeFrame((self.__currentFrame+1) % self.__nbFrame)
            if(self.__invert):
                self.sprite.setFrame(self.__nbFrame + self.__currentFrame)
 
class SpriteDrawer:

    def __init__(self, animator):
        self.__animator = animator

    #take a box with a sprite and draw it to screen
    def draw(self, spriteBox, vOffset):
        
        spriteBox.animate(self.__animator)  
        
        pt = spriteBox.box.pt
        if(spriteBox.applyOffset): #shake effects43
            pt += vOffset

        spriteBox.sprite.x = pt.x
        spriteBox.sprite.y = pt.y

        #if collision box is not same size as the sprite, then we offest the sprite as defined when we created the SpritBox object
        if(spriteBox.spriteOffsetPt is not None):

            offsetx = spriteBox.box.dim.w - spriteBox.sprite.width - spriteBox.spriteOffsetPt.x if( spriteBox.sprite.mirrorX ) else spriteBox.spriteOffsetPt.x
            spriteBox.sprite.x += offsetx
            
            offsety = spriteBox.box.dim.h - spriteBox.sprite.height - spriteBox.spriteOffsetPt.y if( spriteBox.sprite.mirrorY ) else spriteBox.spriteOffsetPt.y
            spriteBox.sprite.y += offsety


        #draw the sprite and mask if we provided a mask
        if(spriteBox.spriteMask is not None):
            thumby.display.drawSpriteWithMask(spriteBox.sprite, spriteBox.spriteMask)
        else:
            thumby.display.drawSprite(spriteBox.sprite)


        if(spriteBox.debug): #draw collision box
            thumby.display.drawRectangle(int(spriteBox.box.pt.x), int(spriteBox.box.pt.y), spriteBox.box.dim.w, spriteBox.box.dim.h, 1) 
        
        #if(spriteBox.box.parent is not None):
        #    parent = spriteBox.box.parent 
        #    thumby.display.drawRectangle(int(parent.pt.x), int(parent.pt.y), parent.dim.w, parent.dim.h, 1) 
    
        
