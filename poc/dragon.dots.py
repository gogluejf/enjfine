import time
import thumby
import math
import random

import sys
sys.path.insert(0, '/Games/engine')

import rectangle
import blit
import sprite
import text
import drawers
import controller
import animator
import runner
import physicals


class Position():
    LEFT = -1
    CENTER = 0
    RIGHT = 1

class VPosition():
    TOP = -1
    MIDDLE = 0
    BOTTOM = 1    

class FontSize():
    SMALL = 0
    BIG = 1
    
class Color():
    WHITE = 1
    BLACK = 0

class TextBG():
    TRANSPARENT=-1
    INVERT=0
    INVERT_FULL_LINE=1

#effect of a box on a parent box
class BoxedEffect():
    NO_EFFECT = -1 #  a parent box boundary has no effect on a box
    WRAP = 0 #during a movement, as soon as a box is outside of a parent box boundary, it will teleport the outside
    BOUNCE = 1 #during a movement, the box will revert speed goal and current speed direction when reaching the boundary of a parent box
    BLOCK = 2 #during a movement, box will just block when reaching the boundary of a parent box

#effect to apply on sprite
class SpriteEffect():
    SHAKE = 0# will shake the sprite in quick movement
    FLASH = 1 # will flash a sprite by inverting the sprite colors 
    INVERT = 2 # invert the spirte color
    INVISIBLE = 3 #make the sprite invisible
    EXPLODE = 4 #make the an explosion of particles from the center of the sprite
    SPLASH = 5 #make splash effect of particles in a particular direction

class Button:
    UP = 0
    DOWN = 1
    LEFT = 1 << 1
    RIGHT = 1 << 2
    A = 1 << 3
    B = 1 << 4

class Fade:
    IN = 1
    OUT = 0

class Operator():
    OR = 0
    AND = 1

class Vector:        
    def __init__(self, x, y):
        self.setVector(x,y)
    
    def setVector(self, x, y):
        self.x=x
        self.y=y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        return self / self.length()

    def dot(self, vector):
        return self.x*vector.x +  self.y*vector.y

    def __str__ (self):
        return "Vector ({0}, {1})".format(self.x, self.y)

    def __mul__ (self, multiplier):
        return Vector(self.x * multiplier, self.y *  multiplier)
    
    def __truediv__ (self, divider):

        return Vector(self.x / divider, self.y / divider)    

    def __add__ (self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__ (self, vector):
        return Vector(self.x - vector.x, self.y - vector.y)

    #return new vector with absolute values
    def absolute(self):
        return Vector(abs(self.x), abs(self.y))

    def copy(self):
        return Vector(self.x, self.y)
    
class Point:
    def __init__(self, x=0, y=0):
        self.velocityGoal=Vector(0,0)  #speed per second at cruise speed
        self.velocity=Vector(0,0) #current speed per seconde (pixel)
        self.vAcceleration=Vector(75,75) #accelation multiplier ( this is how much acceleration per seconLd it will get (eg if goal is 25 and acceleration is 75, it will take 333ms to get to goal velocity))
        self.setPoint(x,y)
    
    def setPoint(self, x, y):
        self.x=x
        self.y=y

    def __str__(self):
        return "Point (\Position ({0}, {1})\nGoal ({2})\nVelocity ({3})\nAcceleration({4})\n)".format(self.x, self.y, self.velocityGoal, self.velocity, self.vAcceleration)

    #get vector representing the distance within 2 points
    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vector(x, y)

    #add a vector to a point and return the new position 
    def __add__(self, vector):
        x = self.x + vector.x
        y = self.y + vector.y
        return Point(x, y)

class Dimension:
    
    def __init__(self, w=thumby.display.width, h=thumby.display.height):
        self.setSize(w,h)
        
        self.pt = None
    
    def setSize(self, w, h):
        self.w = w
        self.h = h
        
    #set a point on dimension representing the right/bottom coordinate of the dimension
    #this point used to update the dimension
    def initPoint(self, pt = None):
        
        self.pt = pt if pt is not None else Point(self.w, self.h)

    #get a Dimension matching a grod of many ( cols*rows ) dimensions 
    def getGridSize(self, cols, rows):
        return Dimension(self.w*cols, self.h*rows)

    def __str__(self):
        return "Dimension ({0}, {1})".format(self.w, self.h)

    def __sub__(self, other):
        w = self.w - other.w
        h = self.h - other.h
        return Dimension(w, h)

class GridCoordinate:
    def __init__(self, col=0, row=0):
        self.setCoordinate(col,row)
    
    def setCoordinate(self, col, row):
        self.col=col
        self.row=row

    def __str__(self):
        return "Grid coordinate ({0}, {1})".format(self.row, self.col)

#get a box to use with animate and draw via drawer objects
#point attribute is the top left corner of the box
class Box:
    def __init__(self, pt = Point(), dim = Dimension()):
        self.parent = None
        self.pt = pt
        self.dim = dim

    #return a Poin that is the center point of the box
    def getCenterPoint(self):
        return Point(self.pt.x+self.dim.w/2, self.pt.y+self.dim.h/2)

    #return a point for a specific dimension position inside a box
    def getDimensionPosition(self, dim, position = Position.CENTER, vposition = VPosition.MIDDLE):
        
        if (position == Position.LEFT): x = self.pt.x
        if (position == Position.CENTER): x = self.pt.x + self.dim.w/2 - dim.w/2
        if (position == Position.RIGHT): x = self.pt.x + self.dim.w - dim.w
        
        if (vposition == VPosition.TOP): y = self.pt.y
        if (vposition == VPosition.MIDDLE): y = self.pt.y + self.dim.h/2 - dim.h/2
        if (vposition == VPosition.BOTTOM): y = self.pt.y + self.dim.h - dim.h

        return Point(x, y)

    #trap the box in another box to limit some velocity movement and other effects
    # properties default override properties per effect
    # WRAP
    #   wrap_item_w: when wrapping on x axe, the offset item will use that widh for the boxed item rather than the boxed item width ( this is useful when multiple sprite of not same size need to wrap on same axe and keep distance ratio)
    #   wrap_item_h: same as wrap_item_w, but on y axe
    def pack(self, parent, boxedEffect = BoxedEffect.WRAP, properties = {} ):
        self.parent = parent
        self.boxedEffect = boxedEffect
        self.boxedEffectProperties = properties

    def Unpack(self):
        self.parent=None

    def __str__(self):
        string = "Box:(\n{0}\n{1}".format(self.pt, self.dim)
        if(self.parent != None):
            string = string + "\nParent ({0})\nBoxedEffect({1})".format(self.parent, self.boxedEffect)

        return string+")"


#grid for tiling positioning
class Grid(Box):
    
    def __init__(self, pt = Point(), dim = Dimension(8,8), cols = 9, rows = 5):
        self.cols = cols
        self.rows = rows
        self.cellSize = dim
        super().__init__(pt, Dimension(dim.w * cols, dim.h * rows))

    #get a point from col and row position
    #col: 0 = first colda
    #row: 0 = first row
    def getPointFromGridCoordinate(self, coord):

        if (coord.col >= self.cols):
            raise Exception("col {0} is outside cols range 0x{1}".format(coord.col, self.cols-1))
        if (coord.row >= self.rows):
            raise Exception("row {0} is outside rows range 0x{1}".format(coord.row, self.rows-1))

        return Point(self.pt.x+self.cellSize.w*coord.col, self.pt.y+self.cellSize.h*coord.row)

    #get the grid coordinate
    #if pt is not matching grid coordinate, it will roundi to closest coord
    
    def getGridCoordinateFromPosition(self, pt):
        return GridCoordinate(round((pt.x-self.pt.x) / self.cellSize.w), round((pt.y-self.pt.y) / self.cellSize.h))


class StopWatch():

    #duration in ms before time, -1 for no timeout
    #currentFrameTs to init the watch, -1 if no timeout
    def __init__(self, duration = -1, currentFrameTs = -1):
        self.__timeout =  True
        self.__reset(duration, currentFrameTs)

    def __reset(self, duration, currentFrameTs)  :  
        self.__duration = duration
        self.__initFrameMs = currentFrameTs
        

    # test for timeout
    def isTimeout(self, currentFrameTs):
        return self.__duration != -1 and currentFrameTs - self.__initFrameMs >  self.__duration

    #set a timeout that will execcute code once timeoute reached
    #onTimeoutCode : run when the duration is reached
    #untilTimeCode : run when each frame until duration is reached
    #cancel : this will cancel timeout if a time is already set and set a new one
    def setTimeout(self, duration, currentFrameTs, onTimeoutCode, untilTimeoutCode = None, cancel = False):
        
        if( cancel or self.__timeout):
            self.__reset(duration, currentFrameTs)
            self.__onTimeoutCode = onTimeoutCode
            self.__untilTimeoutCode = untilTimeoutCode
            self.__timeout =  False

    #cancel of current stopwatch ( no more on/until timeout will execute)
    def cancel(self):
        self.__timeout = True

    #if currently watching for a timeout, this will end the timer and force the onTimeoutCode
    def forceTimeout(self):
        self.__duration = 0

    #watch for the timeout, will exeucute onTimeout and untilTimeout is reached
    #return true if the watch executed ( reached timeout )
    def watch(self, currentFrameTs):
        
        if not self.__timeout:
            if(self.isTimeout(currentFrameTs)):
                self.__onTimeoutCode()
                self.__timeout = True
            else:
                if(self.__untilTimeoutCode is not None): self.__untilTimeoutCode()
        
        return self.__timeout


#contain a box and sprite
#use the box to do animation ( sprite get update in drawer ready to display)
class SpriteBox:
    
    #bitmap to load in sprite
    #dim: the sprite dimension 
    #bitmapMask : useful to draw black and white sprite while supporting transparence ( use if you plan having background)
    #collisionBoxOverride: if sprite dimension is not the box you want for physique, use collisionBoxOverride to override the collision box.  box.pt will be used for offset to the sprite box )
    #because screen is so mall and big sprite look better, the collisionBoxOverride is very useful to have big sprite with smaller collision box so the graphx and the gamplay still nice
    #nbFrame, how many frame the sprite have ( important for inverted frames )
    def __init__(self, bitmap, dim, bitmapMask = None, collisionBoxOverride = None, nbFrame = 1):
        self.id = None
        self.debug = False #setting it to true will display the collision box
        self.nbFrame = nbFrame
        self.currentFrame = 0 #currentFrame of the animation
        
        self.__effects = {}

        self.box = Box(Point(), collisionBoxOverride.dim if collisionBoxOverride is not None else dim)
        self.spriteOffsetPt = collisionBoxOverride.pt if(collisionBoxOverride) else None

        key = -1 if bitmapMask is not None else 0 #all sprite set to black color has transparent, except when a mask is provided, in that case we set both color and the mask will set transparency 
        self.sprite = thumby.Sprite(dim.w, dim.h, bitmap + self.__invertBitMap(bitmap), 0, 0, key)
        self.spriteMask = thumby.Sprite(dim.w,dim.h,bitmapMask) if( bitmapMask is not None) else None #set mask if one is provided

        self.sprite.hide = False

    #use this method to change fraem, since it adapt both the mask and sprite for animation
    #it also keep track of the animation frame for proper couleur invertion effect
    def changeFrame(self, frame):
        self.sprite.setFrame(frame)
        if(self.spriteMask != None):
            self.spriteMask.setFrame(frame)
        self.currentFrame = frame

    #take a array of byte and invert them ( in thumby, we used it to invert  black and white into bitmaps)
    def __invertBitMap(self, bitmap):

        invertedBitmmap = []

        for c in range(len(bitmap)):
            invertedBitmmap.append(~bitmap[c] & 255)
            
        return bytearray(invertedBitmmap)
     
    #set an effect to apply on a sprite after the draw ran ( effect with x/y layout changes do not affect collision box position 
    #effect: the effect identifier as defined into SpriteEffect.*
    #duration the duration of the effect on the sprite in ms , -1 for unlimted duration
    #currentFrameTs: the current frame ms to start the timer , leave it to -1 for unlimited duration
    #overrideIfExist: if False and an effect of same type is already set, the effect will not be replaced. 
    def setEffect(self, effect, properties = {}, duration = -1, currentFrameTs = -1, overrideIfExist = False):
    
        if(overrideIfExist == False and effect in self.__effects):
            return
        
        self.__effects[effect] = self.SpriteEffectAnimator(effect, properties, duration, currentFrameTs, self)
        

    #exeucte the effect on the sprite
    def applyEffects(self, animator):
        
        for key, effect in self.__effects.items():
            if(effect.isTimeout(animator.currentFrameTs)):
                e = self.__effects.pop(key, None)
                e.end(self)
                continue
            effect.apply(self, animator)

    #effect: the effect identifier as defined into SpriteEffect.*
    def endEffect(self, effect):
        e = self.__effects.pop(effect, None)
        if(e is None):
            return

        e.end(self)



    #class to apply extra effect on a sprite after they has been updated
    class SpriteEffectAnimator():
        
        #effect: the effect identifier as defined into SpriteEffect.*
        #duration the duration of the effect on the sprite in ms , -1 for unlimted duration
        #the current frame ms to start the timer
        #properties: dictionary to pass specific params to specific effect
            #FLASH
                #bps: (beat per second) number of flash per second
            #SHAKE
                #bps: (beat per second) number of position change per second
                #radius: pixel offset in every direction for randhom shake effect
            #EXPLODE
                #particles: number of particles during explosion
                #color :  Color.* the color of the particles
            #SPLASH
                #particles: number of particles during explosion
                #color :  Color.* the color of the particles
                #velocity: the velocity where the particles will splash
                #degrees : + or - angle to splash
        def __init__(self, effect, properties, duration, currentFrameTs, spriteBox):
            self.__effect = effect
            self.__properties = properties
            self.__stopwatch = StopWatch(duration, currentFrameTs)
            self.__counter = 999999 #setting it very high so first iteration is always beyond frame interval, forcing the effect on first frame

            self.init(spriteBox)

        #return true if the effect timeout
        #the current frame ms to to test the timeout
        def isTimeout(self, currentFrameTs):
            return self.__stopwatch.isTimeout(currentFrameTs)
        
        def init(self, spriteBox):
            
            if(self.__effect == SpriteEffect.EXPLODE):
                self.__points = []
                for i in range(self.__properties.get("particles", 24)):
                    
                    v = random.randint(25,75)
                    
                    pt =  spriteBox.box.getCenterPoint()
                    pt.velocityGoal.y = v
                    pt.velocity.y = -v/1.5
                    pt.vAcceleration = Vector(5,75)
                    pt.velocity.x = random.randint(-30,30)
                    self.__points.append(pt)

            if(self.__effect == SpriteEffect.SPLASH):
                self.__points = []
                
                velocity = self.__properties.get("velocity", Vector(45,-45))
                length = velocity.length() * 4 #60
            
                if velocity.x == 0:
                    radian = math.radians(90) if velocity.y > 0 else math.radians(270)
                else:    
                    radian = math.atan(velocity.y / velocity.x)
                    if(velocity.x < 0):
                            radian -= math.radians(180)
                
                for i in range(self.__properties.get("particles", 24)):
                    r = radian + math.radians(random.randint(-self.__properties.get("degrees", 30), self.__properties.get("degrees", 30)))
                    pt =  spriteBox.box.getCenterPoint()
                    pt.velocity = Vector(math.cos(r), math.sin(r)) * length * random.uniform(.75,1)
                    pt.vAcceleration = pt.velocity.absolute() * random.uniform(1,4) 
                    self.__points.append(pt)
            

        #note that all effect are apply after the sprit has been updated, so the effect that affect the sprite coordinate have no permenent effect on next frames
        def apply(self, spriteBox, animator):
             
            sprite = spriteBox.sprite
              
            if(self.__effect == SpriteEffect.FLASH):
                
                f = animator.getFramesIntervalFromBps(self.__properties.get("bps", 1)) + 1
                
                self.__counter += 1
                if(self.__counter >= f):
                    self.__counter=0
                    frame = spriteBox.nbFrame+spriteBox.currentFrame
                else:
                    frame = spriteBox.currentFrame
                
                sprite.setFrame(frame)
                if(sprite.key != -1): sprite.key = frame

            if(self.__effect == SpriteEffect.INVERT):
                sprite.setFrame(spriteBox.nbFrame + spriteBox.currentFrame)
                if(sprite.key != -1): sprite.key = 1
            
            if(self.__effect == SpriteEffect.SHAKE):
                
                f = animator.getFramesIntervalFromBps(self.__properties.get("bps", animator.maxFps))
                self.__counter += 1
                if(self.__counter >= f):
                    self.__counter=0
                    radius = self.__properties.get("radius", 1)
                    sprite.x = sprite.x + random.randint(-radius,radius)
                    sprite.y = sprite.y + random.randint(-radius,radius)
                
            if(self.__effect == SpriteEffect.INVISIBLE):
                sprite.hide = True

            if(self.__effect == SpriteEffect.EXPLODE or self.__effect == SpriteEffect.SPLASH):
                for pt in self.__points:
                    animator.updatePoint(pt)
                    thumby.display.setPixel(round(pt.x), round(pt.y),  self.__properties.get("color", Color.WHITE))

        def end(self, spriteBox):
            
            sprite = spriteBox.sprite
            
            if(self.__effect == SpriteEffect.FLASH or self.__effect == SpriteEffect.INVERT):
                sprite.setFrame(spriteBox.currentFrame)
                if(sprite.key != -1): sprite.key = 0

            if(self.__effect == SpriteEffect.INVISIBLE):
                sprite.hide = False

            if(self.__effect == SpriteEffect.EXPLODE or self.__effect == SpriteEffect.SPLASH):
                self.__points = None

    def __str__(self):
        string = "SpriteBox:(\n{0}".format(self.box)
        string = string + "Sprite:(\nx: {0} y:{1} width:{2} height:{3})\n".format(self.sprite.x, self.sprite.y, self.sprite.width, self.sprite.height)
        string = string + "offset: {0}".format(self.spriteOffsetPt)
        
        return string+")"

class BlitBox:
    
    #bitmap to load in sprite
    #dim : the bitmap dimension
    def __init__(self, bitmap, dim, mirrorX = 0, mirrorY = 0):
        
        self.box = Box(Point(), dim)
        self.bitmap = bitmap
        self.mirrorX = mirrorX
        self.mirrorY = mirrorY


class RectangleMode:
    OUTLINE = 0 #draw boundary of the box
    FILLED = 1 #draw a filled box 

class RectangleBox:

    def __init__(self, dim, mode = RectangleMode.FILLED, color = Color.WHITE):

        self.box = Box(Point(), dim)
        self.mode = mode
        self.color = color
        
#general drawer help
class Drawer:
    
    screenBox = Box()

    
    #set the fps for the game
    def __init__(self):
        self.animator = self.Animator()
        self.controller = self.Controller()
        self.textDrawer = self.TextDrawer()
        self.blitDrawer = self.BlitDrawer()
        self.__rectDrawer = self.RectangleDrawer()
        self.spriteDrawer = self.SpriteDrawer(self.animator)

        random.seed(time.ticks_ms())
        thumby.display.setFPS(self.animator.maxFps)
        self.reset()

    def reset(self):
        self.animator.reset()
        self.rectBoxes = []
        self.spriteBoxes = []
        self.blitBoxes = []
        self.textBoxes = []

    def update(self):

        self.animator.runWatches()

        #update all positions
        for rectBox in self.rectBoxes: self.animator.updateBox(rectBox.box)
        for blitBox in self.blitBoxes: self.animator.updateBox(blitBox.box)
        for spriteBox in self.spriteBoxes: self.animator.updateBox(spriteBox.box)
        for textBox in self.textBoxes: self.animator.updateBox(textBox.box)        
        
        #draw on screen
        for rectBox in self.rectBoxes: self.__rectDrawer.draw(rectBox)
        for blitBox in self.blitBoxes: self.blitDrawer.draw(blitBox)
        for textBox in self.textBoxes: self.textDrawer.draw(textBox)
        for spriteBox in self.spriteBoxes: self.spriteDrawer.draw(spriteBox)
        
        thumby.display.update()


    #print str to screen
    def debug(self, str, line=1):
        self.textDrawer.drawLine(self.text_drawer.Text(str),line)

    def __printFps(self):
        self.textDrawer.drawLine(self.text_drawer.Text(str(self.animator.getFps()) + "FPS",Position.RIGHT),5)


    class RectangleDrawer:
        
        def draw(self, rectBox):
            if(rectBox.mode == RectangleMode.FILLED):
                thumby.display.drawFilledRectangle(round(rectBox.box.pt.x), round(rectBox.box.pt.y), rectBox.box.dim.w, rectBox.box.dim.h, rectBox.color)
            if(rectBox.mode == RectangleMode.OUTLINE):
                thumby.display.drawRectangle(round(rectBox.box.pt.x), round(rectBox.box.pt.y), rectBox.box.dim.w, rectBox.box.dim.h, rectBox.color)
            
    class BlitDrawer:
        
        def draw(self, blitBox):
            thumby.display.blit(blitBox.bitmap, round(blitBox.box.pt.x), round(blitBox.box.pt.y), blitBox.box.dim.w, blitBox.box.dim.h, 0, blitBox.mirrorX, blitBox.mirrorY)

    class SpriteDrawer:

        def __init__(self, animator):
            self.__animator = animator

        #take a box with a sprite and draw it to screen
        def draw(self, spriteBox):
            
            spriteBox.sprite.x = spriteBox.box.pt.x
            spriteBox.sprite.y = spriteBox.box.pt.y

            #if collision box is not same size as the sprite, then we offest the sprite as defined when we created the SpritBox object
            if(spriteBox.spriteOffsetPt is not None):
 
                offsetx = spriteBox.box.dim.w - spriteBox.sprite.width - spriteBox.spriteOffsetPt.x if( spriteBox.sprite.mirrorX ) else spriteBox.spriteOffsetPt.x
                spriteBox.sprite.x = spriteBox.sprite.x + offsetx
                
                offsety = spriteBox.box.dim.h - spriteBox.sprite.height - spriteBox.spriteOffsetPt.y if( spriteBox.sprite.mirrorY ) else spriteBox.spriteOffsetPt.y
                spriteBox.sprite.y = spriteBox.sprite.y + offsety

            spriteBox.applyEffects(self.__animator)

            if(spriteBox.sprite.hide == True):
                return

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


    class Controller:

        #control
            #move grid
            #fast to stop
            #jump / #gravity
            #double jump
            #fly with gravity
            #velocity charger ( hockey style)
            #create control motion template( ice, gravity, etc )

        #wait for button to be pressed
        #buttons: bitfield of Button.*
        def wait(self, buttons):
        
            while(1):
                if(self.pressed(buttons)): 
                    break
                thumby.display.update()
        
        #multtiple buttons detection
        #buttons: bitfield of Button.*
        def pressed(self, buttons, operator = Operator.OR):
            
            if(operator == Operator.OR and (buttons & Button.UP and thumby.buttonD.pressed() or buttons & Button.DOWN and thumby.buttonU.pressed() or buttons & Button.LEFT and thumby.buttonL.pressed() or buttons & Button.RIGHT and thumby.buttonR.pressed() or buttons & Button.A and thumby.buttonA.pressed() or buttons & Button.B and thumby.buttonB.pressed())):
                return True
            
            if(operator == Operator.AND):
                
                pressed= 0
                if(thumby.buttonD.pressed()): pressed |= Button.DOWN
                if(thumby.buttonU.pressed()): pressed |= Button.UP
                if(thumby.buttonL.pressed()): pressed |= Button.LEFT
                if(thumby.buttonR.pressed()): pressed |= Button.RIGHT
                if(thumby.buttonA.pressed()): pressed |= Button.A
                if(thumby.buttonB.pressed()): pressed |= Button.B
                
                if(pressed & buttons == buttons):
                    return True
      
            return False
            
        #multtiple buttons detection
        #buttons: bitfield of Button.*
        def justPressed(self, buttons, operator = Operator.OR):
            
            if(operator == Operator.OR and (buttons & Button.UP and thumby.buttonD.justPressed() or buttons & Button.DOWN and thumby.buttonU.justPressed() or buttons & Button.LEFT and thumby.buttonL.justPressed() or buttons & Button.RIGHT and thumby.buttonR.justPressed() or buttons & Button.A and thumby.buttonA.justPressed() or buttons & Button.B and thumby.buttonB.justPressed())):
                return True
            
            if(operator == Operator.AND):
                
                justPressed= 0
                if(thumby.buttonD.justPressed()): justPressed |= Button.DOWN
                if(thumby.buttonU.justPressed()): justPressed |= Button.UP
                if(thumby.buttonL.justPressed()): justPressed |= Button.LEFT
                if(thumby.buttonR.justPressed()): justPressed |= Button.RIGHT
                if(thumby.buttonA.justPressed()): justPressed |= Button.A
                if(thumby.buttonB.justPressed()): justPressed |= Button.B
                
                if(justPressed & buttons == buttons):
                    return True;
      
            return False

        
        def twoAxisFreeMove(self, spriteBox):
            
            box = spriteBox.box
            sprite = spriteBox.sprite
            pt = box.pt
            
            acceleration=40
            speed=50
            
            pt.velocityGoal.x=0
            pt.velocityGoal.y=0
            pt.vAcceleration.x=acceleration
            pt.vAcceleration.y=acceleration
            
            if(thumby.buttonL.pressed()): 
                pt.velocityGoal.x=-speed
                sprite.mirrorX = 1            
            if(thumby.buttonR.pressed()): 
                pt.velocityGoal.x=speed
                sprite.mirrorX = 0
            if(thumby.buttonD.pressed()): pt.velocityGoal.y=speed
            if(thumby.buttonU.pressed()): pt.velocityGoal.y=-speed    

        #return true if a button has been pushed
        def twoAxisGridMove(self, spriteBox):
        
            #push with delay
            #smooth transition

            x=0
            y=0

            if(thumby.buttonL.justPressed()):   x = -1
            if(thumby.buttonR.justPressed()):   x = 1
            if(thumby.buttonD.justPressed()):   y = 1
            if(thumby.buttonU.justPressed()):   y = -1
            
            if(x == 0 and y == 0):
                return False

            box = spriteBox.box
            grid = box.parent
            coord = grid.getGridCoordinateFromPosition(box.pt)
            
            if(x != 0): coord.col = coord.col + x
            if(y != 0): coord.row = coord.row + y
        
            if( coord.col < 0 or coord.col >= grid.cols ): return True
            if( coord.row < 0 or coord.row >= grid.rows ): return True
        
            box.pt =  grid.getPointFromGridCoordinate(coord)
            return True
            
        def platformerJumper(self, spriteBox):
            
            box = spriteBox.box
            sprite = spriteBox.sprite
            pt = box.pt
            
            accelerationx=500
            speedx=50
            accelerationy=300
            speedy=100
            
            pt.velocityGoal.x=0
            pt.velocityGoal.y=speedy
            pt.vAcceleration.x=accelerationx
            pt.vAcceleration.y=accelerationy

            if(thumby.buttonL.pressed()): 
                pt.velocityGoal.x=-speedx
                #sprite.mirrorX = 1            
            if(thumby.buttonR.pressed()): 
                pt.velocityGoal.x=speedx
                #sprite.mirrorX = 0
            if(thumby.buttonB.justPressed()): pt.velocity.y = -speedy            
    
    

    #all to animate or boxes ( sprite and text)
    class Animator:
    
        #bouncing like balls
        #grativy
        #move (acc/dec)
        
        #effect
            #magnet
            #wave
            #circle
            #pause
    
        #engine
            #ai pattern
        #engine with map
            #gravity collision with map
            #scrolling map ( and background)

        __minBrightness = 0
        __maxBrightness = 127

        def __init__(self):
            self.maxFps=60
            self.currentFrameTs=0 #timestamp at the beginning of the frame so all animation sync on same clock
            self.__previousFrameDeltaSec=0 # the difference in second from previous frame to current one
            self.__fpsCpt=0 #incremente fps in current second
            self.__fpsLs=0 # how many frame in last sec
            self.__paused = False #pause all movement
            self.reset()

        def reset(self):
            thumby.display.brightness(self.__maxBrightness)
            self.unpause()
            self.resetWatches()

        def initFrame(self, emptyScreen = True):
            currentFrameTs = time.ticks_ms()
            self.__previousFrameDeltaSec =  (currentFrameTs - self.currentFrameTs) / 1000
            self.currentFrameTs=currentFrameTs

            s=self.currentFrameTs%2000
    
            if s < 1000:
                self.__fpsCpt += 1
            else:
                if self.__fpsCpt > 0:
                    self.__fpsLs= self.__fpsCpt
                    print(self.__fpsLs)
                    self.__fpsCpt=0
            
            if(emptyScreen):
                self.emptyScreen()
            
        #color : Color.*
        def emptyScreen(self, color = Color.BLACK):    
            thumby.display.fill(color) # Fill canvas to black

        #get the current fps
        def getFps(self):
            return self.__fpsLs

        #get frame interval with time precision even when framerate change 
        #return the number of frames representing the interval between 2 beat
        #bps:beat per second
        def getFramesIntervalFromBps(self, bps):
            f = round(self.getFps() / bps)
            return f if (f>1) else 1



        #fade in or out for a specific duration
        #this function is blocking for the duration of the fade
        #fade: Fade.*
        #duration: the duration of the effect on the sprite in ms , -1 for unlimted duration
        def fadeBlocking(self, fade, duration):

            s=self.__minBrightness
            e=self.__maxBrightness
            ratio = e/duration

            #if(wait):

            if(fade == Fade.IN):
                brightness = s
                direction = 1
            if(fade == Fade.OUT):
                brightness = e
                direction = -1
            
            thumby.display.brightness(brightness)
            done = False
            self.initFrame(False)
            while(not done):
                self.initFrame(False)

                brightness = brightness + direction * ratio * self.__previousFrameDeltaSec*1000
                
                if(brightness < s): 
                    brightness = s
                    done = True
                if(brightness > e): 
                    brightness = e
                    done = True
                
                thumby.display.brightness(round(brightness))
                thumby.display.update()
        
        
        #fade in or out for a specific duration
        #fade: Fade.*
        #duration: the duration of the effect on the sprite in ms , -1 for unlimted duration
        #code to execute when the fade is completed
        #return a stopwatch so we can control animation
        def fade(self, fade, duration = 0, code = None):

            s=0
            e=127
            ratio = e/duration if duration else e

            if(fade == Fade.IN):
                self.brightness = s
                direction = 1
            if(fade == Fade.OUT):
                self.brightness = e
                direction = -1
  
            thumby.display.brightness(self.brightness)
            
            def onTimeout():
                thumby.display.brightness(e if direction == 1 else s)
                if code != None: code()

            def untilTimeout():
                self.brightness = self.brightness + direction * ratio * self.__previousFrameDeltaSec*1000
                thumby.display.brightness(round(self.brightness))
            
            sw = StopWatch()
            sw.setTimeout(duration, self.currentFrameTs,  onTimeout, untilTimeout)
            self.watches.append(sw)
            return sw

        #move a box to a velocity distance
        #duration is the time in ms the movement should take
        #code to execute when the motion is complete
        #return a stopwatch so we can control animation
        def move(self, box, velocity, duration, code = None):
            ptDestination = box.pt + velocity
            def stop():
                box.pt = ptDestination
                if code != None: code() 
                
            velocity /= (duration / 1000)


            box.pt.velocityGoal = velocity
            box.pt.velocity = velocity
            
            sw = StopWatch()
            sw.setTimeout(duration, self.currentFrameTs,  stop)
            self.watches.append(sw)            
            return sw
    
        #reset all existing watches
        def resetWatches(self):
            self.watches = []

        def runWatches(self):
            for index in range(len(self.watches)-1, -1, -1):
                if self.watches[index].watch(self.currentFrameTs):
                    self.watches.pop(index)

        #wait some time before executing some code
        #return a stopwatch so we can control animation
        def delay(self, duration, code):

            def delayed():
                code()

            sw = StopWatch()
            sw.setTimeout(duration, self.currentFrameTs,  delayed)
            self.watches.append(sw)
            return sw

        #not recommended to use during a gaming loop
        #this is design to be called between loops
        #duration :  time to wait in ms
        def wait(self, duration):

            initTs = time.ticks_ms()
            while(1):
                if(time.ticks_ms() - initTs >= duration):
                    break
                thumby.display.update()
        
        #calculate the time it take for a object to hot a moving target
        # delta: relative position within aiming object and target object
        # velocity: relative velocity within aiming object to target object
        # speed: the aiming object speed velocity
        #return the shortest time it take to reach a target, nevative value if can reach target
        def __shortestTimeToTarget(self, delta, velocity, speed):
            
            #Quadratic equation coefficients a*t^2 + b*t + c = 0
            a = velocity.dot(velocity) - speed * speed
            b = 2 * velocity.dot(delta)
            c = delta.dot(delta)
            
            d = b * b - 4 * a * c
            
            if(d > 0):
                return 2 * c/(math.sqrt(d) - b)
            else:
                return -1;

        #boxOrigin: the box that will aim to the point
        #boxTarget: the box target the origin box will move too
        #return the vector for an origin in movement to aim at a target in movement
        def aimToTarget(self, boxOrigin, boxTarget, speed):
            delta = boxTarget.getCenterPoint() - boxOrigin.getCenterPoint()
            velocity = boxTarget.pt.velocity - boxOrigin.pt.velocity
        
            t = self.__shortestTimeToTarget(delta, velocity, speed)
        
            if(t <= 0):
                return None
            targetPoint = boxTarget.pt + (boxTarget.pt.velocity * t)
            print(t)
            v = targetPoint - boxOrigin.getCenterPoint()
        
            return v / t
    
        #return a collection of spriteBox that collide with main sprintBox
        #main : the target we test collision againts
        #filterId : only test sprite with a particular id
        def detectCollision(self, main, spriteBoxes, filterId = None):
    
            collides = []
    
            if not main.sprite.hide:
                for target in spriteBoxes:
        
                    if(filterId != None and target.id != filterId):
                        continue
                    
                    boxm = main.box
                    boxt = target.box
            
                    if(boxm == boxt):
                        continue
                    
                    xcollide = False
                    ycollide = False
        
                    if((boxm.pt.x >= boxt.pt.x and boxm.pt.x <= boxt.pt.x + boxt.dim.w) or (boxt.pt.x >= boxm.pt.x and boxt.pt.x <= boxm.pt.x + boxm.dim.w)):
                         xcollide = True
                    if((boxm.pt.y >= boxt.pt.y and boxm.pt.y <= boxt.pt.y + boxt.dim.h) or (boxt.pt.y >= boxm.pt.y and boxt.pt.y <= boxm.pt.y + boxm.dim.h)):
                         ycollide = True
            
                    if(xcollide and ycollide):
                         collides.append(target)
                    
            return collides

        #pause all box movement
        def pause(self): 
            self.__paused = True
        
        #unpause all sprite mouvement
        def unpause(self): 
            self.__paused = False
        
        def updateBox(self, box):

            if(self.__paused):
                return

            parent = box.parent

            self.updatePoint(box.pt)
            if(box.dim.pt): 
                self.updateDimension(box.dim,parent)
            
            if(parent is not None):
                
                if(box.boxedEffect == BoxedEffect.WRAP):
                    if box.pt.x > parent.pt.x + parent.dim.w:
                        box.pt.x -= parent.dim.w + box.boxedEffectProperties.get("wrap_item_w", box.dim.w) 
                    elif box.pt.x < parent.pt.x - box.boxedEffectProperties.get("wrap_item_w", box.dim.w) :
                        box.pt.x +=  parent.dim.w + box.boxedEffectProperties.get("wrap_item_w", box.dim.w) 
                
                    if box.pt.y >= parent.pt.y + parent.dim.h:
                        box.pt.y -= parent.dim.h + box.boxedEffectProperties.get("wrap_item_h", box.dim.h) 
                    elif box.pt.y <= parent.pt.y -box.boxedEffectProperties.get("wrap_item_h", box.dim.h) :
                        box.pt.y +=  parent.dim.h + box.boxedEffectProperties.get("wrap_item_h", box.dim.h) 
                else:
    
                    x=None
                    y=None

                    if(box.pt.x+box.dim.w > parent.pt.x+parent.dim.w): 
                        x = parent.pt.x+parent.dim.w-box.dim.w
                    if(box.pt.x < parent.pt.x): 
                        x = parent.pt.x
                    if(box.pt.y+box.dim.h>parent.pt.y+parent.dim.h): 
                        y = parent.pt.y+parent.dim.h-box.dim.h
                    if(box.pt.y<parent.pt.y): 
                        y = parent.pt.y

                    if(x is not None): 
                        box.pt.x = x
                        #if(box.boxedEffect == BoxedEffect.BLOCK):
                        #    box.pt.velocityGoal.x = 0
                        #    box.pt.velocity.x = 0
                        if(box.boxedEffect == BoxedEffect.BOUNCE):
                            box.pt.velocityGoal.x = -box.pt.velocityGoal.x
                            box.pt.velocity.x = -box.pt.velocity.x

                    if(y is not None): 
                        box.pt.y = y
                        #if(box.boxedEffect == BoxedEffect.BLOCK):
                        #    box.pt.velocityGoal.y = 0
                        #    box.pt.velocity.y = 0
                        if(box.boxedEffect == BoxedEffect.BOUNCE):
                            box.pt.velocityGoal.y = -box.pt.velocityGoal.y
                            box.pt.velocity.y = -box.pt.velocity.y

        def updateDimension(self, dim,parent):
            self.updatePoint(dim.pt)
            
            if(parent is not None and dim.pt.x > parent.dim.w): dim.pt.x = parent.dim.w
            if(parent is not None and dim.pt.y > parent.dim.h): dim.pt.y = parent.dim.h
            
            dim.w = round(dim.pt.x)
            dim.h = round(dim.pt.y)

        #point:Point the x, y point you want to affect
        #the point movement will be influence by the velocity
        def updatePoint(self, pt):
            
            delta_s = self.__previousFrameDeltaSec
            
            pt.velocity.x = self.__approach(pt.velocityGoal.x, pt.velocity.x, delta_s * pt.vAcceleration.x)
            pt.x = pt.x + ((pt.velocity.x * delta_s))

            pt.velocity.y = self.__approach(pt.velocityGoal.y, pt.velocity.y, delta_s * pt.vAcceleration.y)
            pt.y = pt.y + ((pt.velocity.y * delta_s))


        #increase/decrease the velocity to reach goal
        #goal: Vector representing the max speed for the vector
        #current: Vector represengint the current speed
        #step = incremental step to next velocity ( based on time )
        def __approach(self,goal, current, step):
 
            diff = goal - current
            
            if(diff>step): return current+step
            if(diff<-step): return current-step
            return goal


        def flashText(self, text):
            text.color = 1 if math.sin(self.currentFrameTs / 100) > 0 else 0

    
    #helper to draw text and numbers
    class TextDrawer:

        #todo scroll smooth ( lines )
        #scroll ( box )
        #draw multilines
        #wordwrap
        #multiline controls
            
        #effect
            #character typing

        # BITMAP: width: 40, height: 6 tiny #numbers
        numbers_map = bytearray([62,34,62,0,36,62,32,0,50,42,38,0,34,42,54,0,14,8,62,0,46,42,18,0,62,42,58,0,50,10,6,0,62,42,62,0,14,10,62,0])
        __currentFont=0 #identification of font size and space
  
        # a box containing some text, useful to apply effects on text
        class TextBox:
        
            # Text Object to contain in the box
            #max_chars: the box size will match this is the maximun character can be display in the box, if max_chars=0, the maximum chars will be equal to the text size
            def __init__(self, text, max_chars = 0):

                self.text= text
                self.max_chars = self.text.getTextLength() if max_chars == 0 else max_chars
                self.box = Box(Point(), Dimension(self.text.getFontWidth(True)*self.max_chars, self.text.getFontHeight()))
                
            #return the text string visibile ( either full text or the first part of text up to max_chars)
            def getVisibileText(self):
                return self.text.text[0:self.max_chars] if self.text.getTextLength()>self.max_chars else self.text.text

            #get the size of the visible text
            def getVisibleTextSizeWidth(self):
                return self.text.getFontWidth(True)*len(self.getVisibileText())
                
            #get absolute x screen position of the text 
            def getTextXFromPos(self):    

                if self.text.pos == Position.LEFT: x=self.box.pt.x
                if self.text.pos == Position.CENTER: x=self.box.pt.x + round(self.box.dim.w/2-self.getVisibleTextSizeWidth()/2)
                if self.text.pos == Position.RIGHT: x=self.box.pt.x + self.box.dim.w-self.getVisibleTextSizeWidth()
                return x                
                
        #transport layer for drawing rectangle
        class Text:
            
            space=1
            __font_h=8
            
            def __init__(self,text, pos=Position.CENTER, color=Color.WHITE, bg=TextBG.TRANSPARENT, fontSize=FontSize.SMALL):
                self.text = text
                self.pos = pos
                self.color = color
                self.bg = bg
                self.fontSize = fontSize

            #get font width ( not including space)
            #withSpace True=include space width, False= only character width
            def getFontWidth(self, withSpace=False):
                w = 8 if self.fontSize == FontSize.BIG else 5
                if withSpace:
                    w=w+self.space
                return w

            #get font heigh
            def getFontHeight(self):
                return self.__font_h

            #return the number of character to display
            def getTextLength(self):
                return len(self.text)

            #return the text width size to display in pixel. This include the spacing after the last character
            def getTextSizeWidth(self):
                return self.getFontWidth(True)*self.getTextLength()


        #write text at a specic line on the screen ( each line is 8px to fit big or small font)
        #text object to draw
        #line: 1 to 5
        def drawLine(self, text, line=0):

            textBox = self.TextBox(text)
            textBox.box.pt.setPoint(0, (line-1)*text.getFontHeight())
            textBox.box.dim.w = thumby.display.width
            
            self.draw(textBox)

        #textBox: TextBox containing the text to draw 
        #big: 1=big, 0=small
        #rectangle obj to display bg
        def draw(self, textBox):

            self.__drawTextBackgroundRectangle(textBox)           
            self.__loadFont(textBox.text)

            thumby.display.drawText(textBox.getVisibileText(), int(textBox.getTextXFromPos()), int(textBox.box.pt.y), textBox.text.color)

        #load the font
        #since loading font is a slow function, only load when text size change
        def __loadFont(self, text):

            font= str(text.fontSize) + "-" + str(text.space)
            if(font != self.__currentFont):
                thumby.display.setFont("/lib/font8x8.bin" if text.fontSize == FontSize.BIG else "/lib/font5x7.bin",  text.getFontWidth(), text.getFontHeight(), text.space)
                self.__currentFont=font
        
        #get the background for the text
        #text_obj: text object
        #return rectangle object
        def __drawTextBackgroundRectangle(self, textBox):
            
            padding=0
  
            if textBox.text.bg != TextBG.TRANSPARENT:
                if textBox.text.bg == TextBG.INVERT:
                    rect_x = textBox.getTextXFromPos()
                    rect_w = textBox.getVisibleTextSizeWidth()
                    if rect_w>thumby.display.width-textBox.getTextXFromPos():
                        rect_w = thumby.display.width-textBox.getTextXFromPos()
                else: #TextBG.INVERT_FULL_LINE
                    rect_x = textBox.box.pt.x
                    rect_w = textBox.box.dim.w
    
                thumby.display.drawFilledRectangle(textBox.box.pt.y-padding, rect_w+(padding*2), textBox.text.getFontHeight()+(padding*2), (textBox.text.color+1)%2)
    
            else:
                rectangle=None
                
            return rectangle



"""
devil_map = bytearray([0,102,217,204,124,204,217,102])
devilSpBox = SpriteBox(devil_map, Dimension(8, 8))
devilSpBox.box.pt.setPoint(64,8)
devilSpBox.box.pack(drawer.screenBox, BoxedEffect.WRAP)
#devilSpBox.box.pt.velocityGoal.x=50
#devilSpBox.box.pt.velocityGoal.y=10
#drawer.spriteBoxes.append(devilSpBox)


#old fields for gravity
ts_init = time.ticks_ms()
position = -skullSpBox.box.dim.h
velocity = 0
pt=Point(0,0)
"""


class RibbitGame:
    
    #__heart = bytearray([14,31,63,126,63,31,14]) #7x7
    #__death = bytearray([66,195,44,28,28,44,195,66]) #8x8

    title = "Tiny Ribbit"

    frog_title_map = bytearray([0,128,96,48,24,204,180,108,148,108,148,232,216,240,224,224,192,192,192,192,224,240,56,28,142,70,6,6,230,134,6,6,4,12,24,48,224,192,128,
           63,127,192,128,248,55,201,182,79,151,15,135,111,155,13,3,7,1,3,1,62,65,128,0,33,64,0,28,63,255,30,0,0,64,0,128,241,191,111,
           192,124,231,163,230,243,114,241,114,209,114,241,242,245,227,228,200,196,152,164,152,36,25,54,12,52,12,52,44,24,44,24,36,152,7,217,182,249,246,
           3,6,15,29,55,109,223,237,255,111,251,126,219,126,95,246,95,183,125,151,111,159,47,251,47,251,127,217,255,221,247,253,179,253,187,237,187,231,223,
           0,0,0,0,0,0,0,0,1,1,3,3,6,15,14,25,54,109,114,77,19,108,19,100,27,100,89,38,89,54,75,54,79,54,95,55,125,63,109])


    __frog_map = bytearray([0,238,40,60,62,60,40,238,0,0,0,0,0,0,0,0,0,0]) + bytearray([0,130,130,254,56,254,186,146,0,0,0,0,0,0,0,0,0,0])
    __frog_mask_map = bytearray([238,255,254,126,127,126,254,255,238,0,1,0,0,0,0,0,1,0]) + bytearray([130,199,255,255,254,255,255,255,146,0,1,1,1,0,1,1,1,0])

    __car1 = bytearray([34,127,127,34,62,62,62,34,34,127,127,62,28]) 
    __car2 = bytearray([62,127,107,119,42,54,42,54,127,99,99,62,62,28])
    __truck = bytearray([127,127,62,62,62,62,62,62,62,62,62,62,62,62,62,62,62,62,127,127,0,127,127,62,62,28])

    __turtle1 = bytearray([28,34,65,73,85,73,85,73,85,65,34,28,28,8])
    __turtle2 = bytearray([28,34,65,73,85,73,85,73,85,65,34,28,28,8]) + bytearray([0]) + bytearray([28,34,65,73,85,73,85,73,85,65,34,28,28,8])
    __turtle3 = bytearray([28,34,65,73,85,73,85,73,85,65,34,28,28,8]) + bytearray([0]) + bytearray([28,34,65,73,85,73,85,73,85,65,34,28,28,8]) + bytearray([0]) + bytearray([28,34,65,73,85,73,85,73,85,65,34,28,28,8])
    __log1 = bytearray([28,34,89,99,89,99,89,99,89,99,89,99,93,99,65,65,34,28])
    __log2 = bytearray([28,34,89,99,89,99,89,99,89,99,89,99,89,99,89,99,89,99,89,99,93,99,65,65,34,28])   

    __goal_map = bytearray([0,40,28,28,28,40,0])
    __cols = 10    
    __rows = 6

    __griOffsetX = 1
    __griOffsetY = -2 #this is because row height is 7pixel and screen is  40, because he have 6 row, we offset 2px 

    __deathAnimationMs = 1500

    class Vehicule():
        CAR1=0
        CAR2=1
        TRUCK=2    
    
    class LakeItem():
        TURTLE1=0
        TURTLE2=1
        TURTLE3=2
        LOG1=3
        LOG2=4

    class LaneType():
        GOAL=0
        LAKE=1
        ROAD=2
        START=3

    # keep tracks of goals, level, life
    class State():
            
        def __init__(self, nbGoals = 5):
            self.nbGoals = nbGoals
            self.reset()
            
        def reset(self):
            self.__resetGoals()
            self.lifes = 2 #does are remaining lifes, so 0 is 1 life ( classic )
            self.level = 1
        
        def __resetGoals(self):
            self.__goals = [0] * self.nbGoals
            self.hittedGoals = []
        
        #true if all goals are filled
        def isLevelClear(self):
            return len(self.hittedGoals) ==  self.nbGoals
    
        def nextLevel(self):
            self.level += 1
            self.__resetGoals()
    
        def looseLife(self):
            self.lifes -= 1
    
        def isGameOver(self):
            return self.lifes < 0
    
        def hitGoal(self, index):
             self.__goals[index] = 1
             self.hittedGoals.append(index)

        def isGoalHitted(self, index):
            return self.__goals[index] == 1
        

    def __init__(self):
        self.__tile = Dimension(7, 7) 
        self.__grid= Grid(Point(self.__griOffsetX,self.__griOffsetY), self.__tile, self.__cols, self.__rows)
        
        self.__state = self.State(round(self.__cols/2))
        

    def initGame(self):

        ### goals
        
        self.__sw = StopWatch(0, self.drawer.animator.currentFrameTs)
       
        self.__state.reset()
       
        for i in range(self.__state.nbGoals):
            rect = RectangleBox(Dimension(self.__tile.w, self.__tile.h-1))
            rect.box.pt = self.__grid.getPointFromGridCoordinate(GridCoordinate(i*2,0))
            self.drawer.rectBoxes.append(rect)   

       
        self.__lanes = [self.LaneType.GOAL]
       
        ### draw lake
       
        #"""
        self.__initLakeItemsLane(10, [  {"lakeItem" : self.LakeItem.TURTLE2, "col" :  0},
                                        {"lakeItem" : self.LakeItem.TURTLE1, "col" :  9}])

        self.__initLakeItemsLane(-10, [ {"lakeItem" : self.LakeItem.LOG1, "col" :  0},
                                        {"lakeItem" : self.LakeItem.LOG2, "col" :  7}])

        #draw water
        rect = RectangleBox(Dimension(self.__grid.dim.w, self.__tile.h * (len(self.__lanes)-1)))
        rect.box.pt = self.__grid.getPointFromGridCoordinate(GridCoordinate(0,1))
        self.drawer.rectBoxes.append(rect)  

        #"""

        """
        self.__initVehiculesLane(60, [ {"vehicule" : self.Vehicule.TRUCK, "col" :  0}])

        self.__initVehiculesLane(25, [  {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                        {"vehicule" : self.Vehicule.CAR2, "col" :  3},
                                        {"vehicule" : self.Vehicule.CAR2, "col" :  6}])    

        """
        self.__initVehiculesLane(-20, [ {"vehicule" : self.Vehicule.CAR1, "col" :  0},
                                        {"vehicule" : self.Vehicule.TRUCK, "col" :  5}])

        self.__initVehiculesLane(20, [  {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                        {"vehicule" : self.Vehicule.CAR1, "col" :  6}])
    
        #our hero
        self.__lanes.append(self.LaneType.START)
        
        self.__frog = SpriteBox(self.__frog_map, Dimension(9,9), self.__frog_mask_map, Box(Point(-1,-1),self.__tile), 2)
        self.__frog.id = "frog"
        self.__frog.box.pack(self.__grid, BoxedEffect.BLOCK)
        self.drawer.spriteBoxes.append(self.__frog)         

        

        self.__startLife()
    
    def __startLife(self):

        if(self.__state.isGameOver()):
            return

        level = self.drawer.textDrawer.TextBox(self.drawer.textDrawer.Text("level {0}".format(self.__state.level)))
        lifes = self.drawer.textDrawer.TextBox(self.drawer.textDrawer.Text("x {0}".format(self.__state.lifes)))
        box = Box(Point(), Dimension(self.__frog.box.dim.w + 6 + lifes.box.dim.w,8*3))
        
        box.pt = self.__grid.getDimensionPosition(box.dim, Position.CENTER, VPosition.MIDDLE)
        level.box.pt = box.getDimensionPosition(level.box.dim, Position.CENTER, VPosition.BOTTOM)
        lifes.box.pt = box.getDimensionPosition(lifes.box.dim, Position.RIGHT, VPosition.TOP)
        
        self.__resetFrogPosition()
        self.__frog.box.pt = box.getDimensionPosition(lifes.box.dim, Position.LEFT, VPosition.TOP)

        self.drawer.animator.fadeBlocking(Fade.OUT, 500)
        self.drawer.animator.emptyScreen()
        self.drawer.textDrawer.draw(level)
        self.drawer.spriteDrawer.draw(self.__frog)
        self.drawer.textDrawer.draw(lifes)
        self.drawer.animator.fadeBlocking(Fade.IN, 25)
        self.drawer.animator.wait(1500)
        self.drawer.animator.fadeBlocking(Fade.OUT, 500)
        self.__resetFrogPosition()
        self.drawer.animator.initFrame()
        self.drawer.update()
        self.drawer.animator.fadeBlocking(Fade.IN, 25)
        self.drawer.animator.unpause()
    
    def __resetFrogPosition(self):
        self.__frog.box.pt = self.__grid.getPointFromGridCoordinate(GridCoordinate(round(self.__cols/2), len(self.__lanes)-1))
        self.__frog.sprite.mirrorX=0
        self.__frog.sprite.mirrorY=0
        self.__frog.changeFrame(0)
        self.__frog.endEffect(SpriteEffect.INVERT)
    
    def __initLakeItemsLane(self, speed, lakeItems):
        for lakeItem in lakeItems: self.__initLakeItem(lakeItem.get("lakeItem"), speed, lakeItem.get("col"))
        self.__lanes.append(self.LaneType.LAKE)
     
    #lakeItemChoice: LakeItem.*
    #speed: the speed of lake item
    #row: row coordinate where the lake item will start
    def __initLakeItem(self, lakeItemChoice, speed, col):
        
        row = len(self.__lanes)

        if lakeItemChoice == self.LakeItem.TURTLE1:
            bitmap = self.__turtle1
            width = 14
           
        if lakeItemChoice == self.LakeItem.TURTLE2:
            bitmap = self.__turtle2
            width = 29           
           
        if lakeItemChoice == self.LakeItem.TURTLE3:
            bitmap = self.__turtle3
            width = 44   

        if lakeItemChoice == self.LakeItem.LOG1:
            bitmap = self.__log1
            width = 18          
        
        if lakeItemChoice == self.LakeItem.LOG2:
            bitmap = self.__log2
            width = 26          

        velocity = Vector(speed,0)
        lakeItem = SpriteBox(bitmap, Dimension(width, self.__tile.h))
        if speed < 0:
            lakeItem.sprite.mirrorX = 1
        
        lakeItem.id = "lane_{0}".format(row)
        lakeItem.box.pt = self.__grid.getPointFromGridCoordinate(GridCoordinate(col, row))
        lakeItem.box.pt.velocityGoal = velocity
        lakeItem.box.pt.velocity = velocity
        lakeItem.setEffect(SpriteEffect.INVERT)
        
        lakeItem.box.pack(self.__grid, BoxedEffect.WRAP, {"wrap_item_w" : 26})
        self.drawer.spriteBoxes.append(lakeItem) 

    def __initVehiculesLane(self, speed, vehicules):
 
        for vehicule in vehicules: self.__initVehicule(vehicule.get("vehicule"), speed, vehicule.get("col"))
        self.__lanes.append(self.LaneType.ROAD)

    #vehiculeChoice: Vehicule.*
    #speed: the speed of the car
    #row: row coordinate where the car will start
    def __initVehicule(self, vehiculeChoice, speed, col):
        
        row = len(self.__lanes)
        
        if vehiculeChoice == self.Vehicule.CAR1:
            bitmap = self.__car1
            width = 13
           
        if vehiculeChoice == self.Vehicule.CAR2:
            bitmap = self.__car2
            width = 14           
        
        if vehiculeChoice == self.Vehicule.TRUCK:
            bitmap = self.__truck
            width = 26    
        
        velocity = Vector(speed,0)
        vehicule = SpriteBox(bitmap, Dimension(width, self.__tile.h))
        if speed < 0:
            vehicule.sprite.mirrorX = 1

        vehicule.id = "lane_{0}".format(row)
        vehicule.box.pt = self.__grid.getPointFromGridCoordinate(GridCoordinate(col, row))
        vehicule.box.pt.velocityGoal = velocity
        vehicule.box.pt.velocity = velocity
        
        vehicule.box.pack(self.__grid, BoxedEffect.WRAP, {"wrap_item_w" : 26})
        self.drawer.spriteBoxes.append(vehicule) 

    def update(self):

        if self.drawer.controller.twoAxisGridMove(self.__frog) :
        
            coord = self.__grid.getGridCoordinateFromPosition(self.__frog.box.pt)
            lane = round(coord.row)
            
            if self.__lanes[lane] == self.LaneType.LAKE:
                self.__frog.setEffect(SpriteEffect.INVERT)
            else:
                self.__frog.endEffect(SpriteEffect.INVERT)
        
            if(thumby.buttonL.pressed()):   
                self.__frog.changeFrame(1)
                self.__frog.sprite.mirrorX = 1 
            if(thumby.buttonR.pressed()):   
                self.__frog.changeFrame(1)
                self.__frog.sprite.mirrorX = 0
            if(thumby.buttonD.pressed()):   
                self.__frog.changeFrame(0)
                self.__frog.sprite.mirrorY = 1 
            if(thumby.buttonU.pressed()):   
                self.__frog.changeFrame(0)
                self.__frog.sprite.mirrorY = 0 
        
        if not self.__frog.sprite.hide:
            coord = self.__grid.getGridCoordinateFromPosition(self.__frog.box.pt)
            lane = round(coord.row)
            
            collides = self.drawer.animator.detectCollision(self.__frog, self.drawer.spriteBoxes, "lane_{0}".format(lane))
      
            collide_goal = self.__lanes[lane] == self.LaneType.GOAL and (not coord.col % 2 or self.__state.isGoalHitted(coord.col // 2))
            sink_lake = self.__lanes[lane] == self.LaneType.LAKE and not len(collides)
            collide_vehicule = self.__lanes[lane] == self.LaneType.ROAD and len(collides)
    
            #if in lake,hitting a vehicule or missing goal, then we loose a life
            if (collide_goal or sink_lake  or collide_vehicule):
                
                color = Color.BLACK if self.__lanes[lane] == self.LaneType.LAKE else Color.WHITE
                
                if(self.__lanes[lane] == self.LaneType.ROAD):
                    self.__frog.setEffect(SpriteEffect.SPLASH, {"particles" : 24, "velocity": collides[0].box.pt.velocity, "color": color}, self.__deathAnimationMs, self.drawer.animator.currentFrameTs )
               
                self.__frog.setEffect(SpriteEffect.INVISIBLE, {}, self.__deathAnimationMs, self.drawer.animator.currentFrameTs )
               
                
                self.drawer.animator.pause()
    
                for target in collides:
                    target.setEffect(SpriteEffect.SHAKE, {}, 1000, self.drawer.animator.currentFrameTs )
    
                def die():
                    self.__state.looseLife()
                    self.drawer.update()
                    self.__startLife()
    
                self.__sw.setTimeout(self.__deathAnimationMs-500, self.drawer.animator.currentFrameTs, die)    
            
            elif (self.__lanes[lane] == self.LaneType.LAKE):
                #make the frog drift with the log and turles, sync it with first item on the lane
                self.__frog.box.pt.velocityGoal = collides[0].box.pt.velocityGoal
                self.__frog.box.pt.velocity = collides[0].box.pt.velocity
    
            #ok, no sink, no collision, if we are on goal lane, we scored
            elif(self.__lanes[lane] == self.LaneType.GOAL):
                self.__state.hitGoal(coord.col // 2)
                bl = BlitBox(self.__goal_map, Dimension(7, 7))
                bl.box.pt = self.__grid.getPointFromGridCoordinate(GridCoordinate(coord.col, 0)) 
                self.drawer.blitBoxes.append(bl)
                
                #passing a level
                if(self.__state.isLevelClear()):
                    self.__frog.setEffect(SpriteEffect.INVISIBLE, {}, 500, self.drawer.animator.currentFrameTs )
                    self.__state.nextLevel()
                    self.drawer.update()
                    self.drawer.blitBoxes = []
                    self.__startLife()
                
                self.__resetFrogPosition()
        
        self.__sw.watch(self.drawer.animator.currentFrameTs)
        
        return not self.__state.isGameOver()
 
#take a game and run it
#each game need to implement "initGame" and "update" function
#each game have access to "drawer"
class GameRunner:
        
    def __init__(self, game):
        self.__game = game
        self.__game.drawer = Drawer()

    def run(self):
        while(1):
            self.__game.drawer.animator.initFrame()
            self.__title()
            self.__init()
            self.__play()
    
    def __title(self):
        
        drawer = self.__game.drawer

        box = drawer.screenBox
        boxTitle = Box(Point(), Dimension(drawer.screenBox.dim.w, 8*2 + 4))
        boxTitle.pt = box.getDimensionPosition(boxTitle.dim, Position.LEFT, VPosition.BOTTOM)
  
        present = drawer.textDrawer.TextBox(drawer.textDrawer.Text("JF Present"))
        present.box.pt = box.getDimensionPosition(present.box.dim, Position.CENTER, VPosition.MIDDLE)
        
        
        velocity = Vector(50, 0)

        frog = BlitBox(self.__game.frog_title_map, Dimension(39, 40))
        frog.box.pt = box.getDimensionPosition(frog.box.dim, Position.RIGHT, VPosition.MIDDLE) + velocity
        title = drawer.textDrawer.TextBox(drawer.textDrawer.Text("Tiny"))
        title2 = drawer.textDrawer.TextBox(drawer.textDrawer.Text("Ribbit"))
        title.box.pt = boxTitle.getDimensionPosition(title.box.dim, Position.LEFT, VPosition.TOP) + velocity*-1
        title2.box.pt = boxTitle.getDimensionPosition(title2.box.dim, Position.LEFT, VPosition.BOTTOM) + velocity*-1
        
      
        def showPresent():
            drawer.textBoxes.append(present) 
            drawer.animator.fade(Fade.IN, 1500, lambda: 
                drawer.animator.delay(750, lambda: 
                    drawer.animator.fade(Fade.OUT, 1500,  lambda: drawer.animator.delay(500, lambda: (
                        drawer.textBoxes.remove(present),
                        drawer.animator.fade(Fade.IN),
                        showGameTitle())))))
        
        def showGameTitle():
            drawer.blitBoxes.append(frog)
            drawer.textBoxes.append(title) 
            drawer.textBoxes.append(title2)   

            drawer.animator.move(frog.box, velocity*-1, 250)
            drawer.animator.move(title.box, velocity.copy(), 250)
            drawer.animator.move(title2.box, velocity.copy(), 250)
      
        showPresent()    

        sw = None
        while(1):
            
            drawer.animator.initFrame()
            
            if drawer.controller.justPressed(Button.A | Button.B):
    
                drawer.animator.move(frog.box, velocity.copy(), 250)
                drawer.animator.move(title.box, velocity * -1, 250)
                sw = drawer.animator.move(title2.box, velocity * -1, 250)
            
            if(sw is not None and sw.isTimeout(drawer.animator.currentFrameTs)):
                break
         
            drawer.update()

       
        
    def __init(self):
        self.__game.drawer.reset()
        self.__game.initGame()
    
    #return true to play again
    #return false to go back to intro
    def __gameOver(self):
        
        drawer = self.__game.drawer
        
        drawer.animator.fadeBlocking(Fade.OUT, 1)
        drawer.animator.emptyScreen()

        gameover = drawer.textDrawer.TextBox(drawer.textDrawer.Text("Game Over"))
        again = drawer.textDrawer.TextBox(drawer.textDrawer.Text("Play again?"))
        options = drawer.textDrawer.TextBox(drawer.textDrawer.Text("B:YES A:NO"))
        
        box = Box(Point(), Dimension(drawer.screenBox.dim.w, 8*3 +4 +4))
        box.pt = drawer.screenBox.getDimensionPosition(box.dim, Position.CENTER, VPosition.MIDDLE)
        gameover.box.pt = box.getDimensionPosition(gameover.box.dim, Position.CENTER, VPosition.TOP)
        again.box.pt = box.getDimensionPosition(again.box.dim, Position.CENTER, VPosition.MIDDLE)
        options.box.pt = box.getDimensionPosition(options.box.dim, Position.CENTER, VPosition.BOTTOM)
        
        drawer.textDrawer.draw(gameover)
        drawer.textDrawer.draw(again)
        drawer.textDrawer.draw(options)
        
        drawer.animator.fadeBlocking(Fade.IN, 1)

        while(1):
            if(thumby.buttonB.pressed()):
                return True
                
            if(thumby.buttonA.pressed()):
                return False
            
            thumby.display.update()
       
    
    def __play(self):
        
        drawer = self.__game.drawer
        
        while(1):
            drawer.animator.initFrame()
            if drawer.controller.pressed(Button.LEFT | Button.DOWN | Button.A | Button.B, Operator.AND):
                self.__init()
                
            if(not self.__game.update()):
                if(self.__gameOver()):
                    self.__init()
                else:
                    drawer.animator.fadeBlocking(Fade.OUT, 1500)
                    drawer.reset()
                    break
            
            drawer.update()   


#fix all loop
    #intro, #gameover, #startlife

#sin, cos
#interval function
#sin/cos move

#effect on boxes ?
#shake everything
#shake other than just sprite ?
#shake only on x axes ?

#operation menu

#fix wait and fadin fade out ?
#fix justPressed blocking
#add move with lambda
#add wait with lambad ( abstract watch)
        
#add level 2 animation         
#score
    #add title animation
    
#improve death frog 
    #lake 
    #goals collision shake everything

#turtle sink
#levels

#smooth mouvement
#endless mode
#flip goals boxes parity for more challengesddw



gameRunner = GameRunner(RibbitGame())
gameRunner.run()





rectBox = RectangleBox(Dimension(0, 2))
rectBox.box.pt = drawer.screenBox.getDimensionPosition(rectBox.box.dim, Position.LEFT, VPosition.BOTTOM)
rectBox.box.pack(drawer.screenBox)
drawer.rectBoxes.append(rectBox)
#rectBox.box.dim.initPoint()

pt = Point(0,0) #rectBox.box.dim.pt
pt.vAcceleration.x = 250
pt.velocityGoal.x = 200

while(1):
    
    drawer.animator.initFrame()
    
    #onTimeout
    #collision engine fix
    #move to position


    if(thumby.buttonA.pressed()):
        #pt.velocityGoal.x = 50
        drawer.animator.updatePoint(pt)
        if(pt.x > rectBox.box.parent.dim.w):
            pt.x = rectBox.box.parent.dim.w
        rectBox.box.dim.w = round(pt.x)
    else:
        #pt.velocityGoal.x = 0
        pt.velocity.x = 0
        pt.x = 0
        rectBox.box.dim.w = 0



    #wrap scrolling engine ( support y scrolling ? )
    #scroll Y 
    
    #scroll grid
    #break boxedEffect for x/y
    #mirror and wrap into grid system
    
    #text examples
    #drawer.text_drawer.drawLine("dragon dots",3,0,0)
    #textBox = drawer.text_drawer.drawLine(drawer.text_drawer.Text("Game Over",0),1)
    #drawer.text_drawer.drawLine(drawer.text_drawer.Text("Play again?", 0),3)
    #text_option = drawer.text_drawer.Text("B:YES A:NO",0,0,1)
    #drawer.animator.flashText(text_option)
    #drawer.text_drawer.drawLine(text_option,5)



    """
    


    #if(thumby.buttonB.justPressed()):
        ts= time.ticks_ms()
        vector = skullSpBox.box.getCenterPoint() - devilSpBox.box.getCenterPoint()

        print("skull {0}".format(skullSpBox.box.getCenterPoint()))
        print("skull {0}".format(devilSpBox.box.getCenterPoint()))
        print("press {0}".format(vector) )
        
        devilSpBox.box.pt.velocity = vector 
        devilSpBox.box.pt.vAcceleration = vector.absolute() / 2
    
    if devilSpBox.box.pt.velocity.x != 0 and time.ticks_ms() - ts > 2000:
        print(devilSpBox.box.pt)
        print(time.ticks_ms() - ts)
    """




    #walkign dragon
    #offset = math.sin(t / 50) * 1
    #dragonSprite.y = round(thumby.display.height/2 - (dragonSprite.width/2) + offset)
    #dragonSprite.x = dragonSprite.width * -1 if  dragonSprite.x>=(thumby.display.width+dragonSprite.width) else dragonSprite.x + 1

    # gravity
    #t= time.ticks_ms()
    #ts = (t-ts_init) / 1000
    #forces = 9.8 #// 9.8m/s/s on earth
    #mass = 300
    #acceleration = forces / mass
    #velocity = velocity + (acceleration * ts)
    #position =  position + round(velocity * ts)
    #skullSprite.y = position
    #if(skullSprite.y>=thumby.display.height+skullSprite.height):
    #    ts_init = time.ticks_ms()
    #    position = -skullSprite.height
    #    velocity = 0

    #turning around dragon
    #bobRate = 250 # Set arbitrary bob rate (higher is slower)
    #bobRange = 8 # round((thumby.display.height/2 - (dragon_w/2))) # How many pixels to move the sprite up/down (-5px ~ 5px)
    #offset_x = math.sin(t / bobRate) * bobRange
    #offset_y = math.sin((t+375) / bobRate) * bobRange    
    #devilSprite.x = round(dragonSprite.x+dragonSprite.width/2 + offset_x)
    #devilSprite.y = round(dragonSprite.y+dragonSprite.width/2 + offset_y)

    game.update()
    


