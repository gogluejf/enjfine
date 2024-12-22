import thumby
import math
import enjfine
import random


class TargetEffect():
    BOX_OBJ = 1
    RECTANGLE = 1 << 1
    BLIT = 1 << 2
    SPRITE = 1 << 3
    TEXT = 1 << 4
    POINT = 1 << 5
    
class EffectType():
    TICK = 1 # for effects base on bps
    DO = 2 # for effects that apply one state change ( or get update  via the animator update methods ( just need to init and end )
    DO_UNTIL = 3 # for effects that need to apply logic on time within frames

class Effect():
    
    #__supported = 0 #bitfield of EffectTarget.* , define into he child class
    #__type = 0 #EffectType.* the type of effect

    #properties: dictionary of properties applicable to the effect
    def __init__(self, drawer, properties = {}):
        self.__properties = properties
        self.__drawer = drawer
        self.__animator = self.__drawer.animator
    
    #init the effect on a single box object
    #target : the object target to apply effect on
    #return stopwatch to control the timer
    def init(self, target, duration = -1):
        self.__init(target)
        if(self.__type == EffectType.TICK):
            sw = self.__animator.tick(self.__properties.get("bps", self.__animator.maxFps), lambda: self.__onTick(target), lambda: self.__onEnd(target), duration, lambda: self.__onEnd(target))
        if(self.__type == EffectType.DO):
            self.__do(target)
            sw = self.__animator.delay(duration, lambda: self.__onEnd(target))
        if(self.__type == EffectType.DO_UNTIL):
            sw = self.__animator.doUntil(lambda previousFrameDeltaSec: self.__doUntil(target, previousFrameDeltaSec) , duration, lambda: self.__onEnd(target))
        return sw

    #init the effect on many objects
    #targets : an array of object target to apply effect on
    #return stopwatch to control the timer
    def initMany(self, targets, duration = -1):
        self.__initMany(targets)
        if(self.__type == EffectType.TICK):
            sw = self.__animator.tick(self.__properties.get("bps", self.__animator.maxFps), lambda: self.__onTickMany(targets), lambda: self.__onEndMany(targets), duration, lambda: self.__onEndMany(targets))
        if(self.__type == EffectType.DO):
            self.__doMany(targets)
            sw = self.__animator.delay(duration, lambda: self.__onEndMany(targets))
        if(self.__type == EffectType.DO_UNTIL):
            sw = self.__animator.doUntil(lambda previousFrameDeltaSec: self.__doUntilMany(targets, previousFrameDeltaSec) , duration, lambda: self.__onEndMany(targets))

        return sw

    def __initMany(self, targets):
        for target in targets: self.__init(target)
    def __onTickMany(self, targets):
        for target in targets: self.__onTick(target)
    def __onEndMany(self, targets):
        for target in targets: self.__onEnd(target)
    def __doMany(self, targets):
        for target in targets: self.__do(target)
    def __doUntilMany(self, targets):
        for target in targets: self.__doUntil(target)

# will flash by inverting the colors
#properties
    #bps: (beat per second) number of flash per second, default to max fps
class FlashEffect(Effect):

    __supported = TargetEffect.SPRITE | TargetEffect.RECTANGLE | TargetEffect.TEXT | TargetEffect.POINT
    __type = EffectType.TICK

    def __init(self, target):
        pass

    def __onTick(self, target):
        target.Invert()

    def __onEnd(self, target):
        target.Revert()

#invert a target for a period of time
class  InvertEffect(Effect):

    __supported = TargetEffect.SPRITE | TargetEffect.RECTANGLE | TargetEffect.TEXT | TargetEffect.POINT
    __type = EffectType.DO

    def __init(self, target):
        pass

    def __do(self, target):
        target.Invert()

    def __onEnd(self, target):
        target.Revert()

# will blink by showing and hiding the sprite
#properties
    #bps: (beat per second) number of flash per second, default to max fps
class BlinkEffect(Effect):

    __supported = TargetEffect.SPRITE | TargetEffect.RECTANGLE | TargetEffect.TEXT | TargetEffect.POINT
    __type = EffectType.TICK

    def __init(self, target):
        pass

    def __onTick(self, target):
        target.hide = True

    def __onEnd(self, target):
        target.hide = False


#hide the a target for a period of time
class  HideEffect(Effect):

    __supported = TargetEffect.BOX_OBJ| TargetEffect.POINT
    __type = EffectType.DO

    def __init(self, target):
        pass

    def __do(self, target):
        target.hide = True

    def __onEnd(self, target):
        target.hide = False

#hide the a target for a period of time
    #bps: (beat per second) number of shakea per second, default to max fps
class  ShakeEffect(Effect):

    __supported = TargetEffect.BOX_OBJ | TargetEffect.POINT
    __type = EffectType.TICK

    def __init(self, target):
        pass
    
    def __onTick(self, target):
        target.applyOffset = True

    def __onEnd(self, target):
        target.applyOffset = False

#do a circle effect that expand ( the circle start from an anchor point )
#angle_steps: what is the angle between each point the circle with draw
#radius_increment: how much the radius increment per second
#radus_max: maximum circle radius before ending the sequence
#loop: loop the sequence ( True, False)
#color: the color of the circle
class  CircleWaveEffect(Effect):

    __supported = TargetEffect.BOX_OBJ | TargetEffect.POINT
    __type = EffectType.DO_UNTIL

    def __init(self, target):
        target.ptAnchor = target.box.getCenterPoint()
        target.radius = 1

    def __doUntil(self, target, previousFrameDeltaSec):
        
        self.__angle = 0
        self.__lastPt = target.ptAnchor + enjfine.Vector(math.cos(0), math.sin(0))*target.radius
        
        while (self.__angle <= 360):
            self.__angle += self.__properties.get("angle_steps", 22.5)
            radiant = math.radians(self.__angle)

            pt = target.ptAnchor + enjfine.Vector(math.cos(radiant), math.sin(radiant)) * target.radius
            thumby.display.drawLine(round(self.__lastPt.x), round(self.__lastPt.y), round(pt.x), round(pt.y), self.__properties.get("color", enjfine.Color.WHITE))
            self.__lastPt = pt

        target.radius += self.__properties.get("radius_increment", 60) * previousFrameDeltaSec
        if(self.__properties.get("loop", True) and target.radius >= self.__properties.get("max_radius", thumby.display.width)):
            target.radius = 1
        
    def __onEnd(self, target):
        pass

# make the an explosion of particles from the center of the sprite <--- init and delay | point
#particles: number of particles during explosion
#color :  enjfine.Color.* the color of the particles
class ExploseEffect(Effect):

    __supported = TargetEffect.BOX_OBJ | TargetEffect.POINT
    __type = EffectType.DO_UNTIL
    
    def __init(self, target):
        target.points = []
        for i in range(self.__properties.get("particles", 24)):
            
            v = random.randint(25,75)
            
            pt =  target.box.getCenterPoint()
            pt.velocityGoal.y = v
            pt.velocity.y = -v/1.5
            pt.vAcceleration = enjfine.Vector(5,75)
            pt.velocity.x = random.randint(-30,30)
            target.points.append(pt)

    def __doUntil(self, target, previousFrameDeltaSec):
        for pt in target.points:
            self.__animator.updatePoint(pt)
            thumby.display.setPixel(round(pt.x), round(pt.y),  self.__properties.get("color", enjfine.Color.WHITE))
    
    def __onEnd(self, target):
        target.points = None

# make splash effect of particles in a particular direction <-- point mouvement | doUntil | point
#particles: number of particles during explosion
#color :  enjfine.Color.* the color of the particles
#velocity: the velocity where the particles will splash
#degrees : + or - angle to splash
class SplashEffect(Effect):

    __supported = TargetEffect.BOX_OBJ | TargetEffect.POINT
    __type = EffectType.DO_UNTIL
    
    def __init(self, target):
        target.points = []
        
        velocity = self.__properties.get("velocity", enjfine.Vector(25,-25))
        length = velocity.length() * 4
        
        for i in range(self.__properties.get("particles", 24)):
            r = math.radians(velocity.getDegrees() + random.randint(-self.__properties.get("degrees", 30), self.__properties.get("degrees", 30)))
            pt =  target.box.getCenterPoint()
            pt.velocity = enjfine.Vector(math.cos(r), math.sin(r)) * length * random.uniform(.75,1)
            pt.vAcceleration = pt.velocity.absolute() * random.uniform(1,4) 
            target.points.append(pt)

    def __doUntil(self, target, previousFrameDeltaSec):
        for pt in target.points:
            self.__animator.updatePoint(pt)
            thumby.display.setPixel(round(pt.x), round(pt.y),  self.__properties.get("color", enjfine.Color.WHITE))
    
    def __onEnd(self, target):
        target.points = None


#repeat
#x scroll, y scroll
#speed -4 -2, -1 ( fastk, medium, slow)
#movement box
#bgmap
#multiple bg + speeds 


#make scrolling background in relation to a target when the target hit his movement ( Box.parentBox ) box boundariees ( BoxedEffect.BLOCK )
#the background will loop over and over when the target sprite is moving
#the background will move in relative speed to the target sprite velocity
#map : the bitmap to use as the background
#map_dimension :  dimension of the map to tile in background
#offset_y : offset from the bg_box where the bg should start
#bg_box: the box that will wrap the background
#layer: the background layer ( 3 = very far 2 = far, 1 = mid, 0 =  close) 3 will move 8 time slower than target, while 0 move at the same speed as the target velocity
class BackgroundEffect(Effect):
    
    __supported = TargetEffect.BOX_OBJ
    __type = EffectType.DO_UNTIL    
    
    def __getLayerSpeed(self, layer):
        if(layer == 0): speed = -1
        if(layer == 1): speed = -2
        if(layer == 2): speed = -4
        if(layer == 3): speed = -8
        return speed
    
    def __getLayer(self):
        return self.__properties.get("layer", 2);
    
    def __init(self, target):

        layer = self.__getLayer()
        if(not hasattr(target, "bg_layers")):
            target.bg_layers = {}
        target.bg_layers[layer] = []
        
        for offset_x in [0, self.__properties.get("bg_box").dim.w,]:

            bg = enjfine.blit.BlitBox(self.__properties.get("map"), self.__properties.get("map_dimension"))
            bg.box.pt.setPoint(offset_x, self.__properties.get("offset_y",0))
            bg.box.pack(self.__properties.get("bg_box"), enjfine.animator.BoxedEffect.WRAP)
            self.__drawer.data.blitBoxes.append(bg)
        
            target.bg_layers[layer].append(bg)
        
        
    def __doUntil(self, target, previousFrameDeltaSec):
        
        box = target.box
        parent = box.parent
        collision = False
    
        if(box.pt.x+box.dim.w>=parent.pt.x+parent.dim.w) and box.pt.velocityGoal.x > 0: collision = True
        if(box.pt.x<=parent.pt.x) and box.pt.velocityGoal.x < 0: collision = True
    
        layer = self.__getLayer()
    
        if(collision):
            speed = self.__getLayerSpeed(layer)
            for bg in target.bg_layers[layer]:
                bg.box.pt.vAcceleration.x = box.pt.vAcceleration.x / abs(speed)
                bg.box.pt.velocityGoal.x = box.pt.velocityGoal.x / speed
                bg.box.pt.velocity.x = box.pt.velocity.x / speed

        else:
            for bg in target.bg_layers[layer]:
                bg.box.pt.velocityGoal.x = 0
                bg.box.pt.velocity.x = 0

    def __onEnd(self, target):
        layer = self.__getLayer()
        for bg in target.bg_layers[layer]:
            self.__drawer.data.blitBoxes.remove(bg)
        
        target.bg_layers[layer] = None


