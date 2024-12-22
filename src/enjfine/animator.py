import time
import thumby
import enjfine
import math

#effect of a box on a parent box
class BoxedEffect():
    NO_EFFECT = -1 #  a parent box boundary has no effect on a box
    WRAP = 0 #during a movement, as soon as a box is outside of a parent box boundary, it will teleport the outside
    BOUNCE = 1 #during a movement, the box will revert speed goal and current speed direction when reaching the boundary of a parent box
    BLOCK = 2 #during a movement box will just block when reaching the boundary of a parent box

class Fade:
    IN = 1
    OUT = 0

class StopWatch():

    #duration in ms before time, -1 for no timeout
    #currentFrameTs to init the watch, -1 if no timeout
    def __init__(self, duration = -1, currentFrameTs = -1):
        self.__timeout =  True
        self.Reset(duration, currentFrameTs)

    #reset the watch with new countdown
    def Reset(self, duration, currentFrameTs)  :  
        self.__duration = duration
        self.__initFrameMs = currentFrameTs
        

    # test for timeout
    def isTimeout(self, currentFrameTs):
        return self.__duration != -1 and currentFrameTs - self.__initFrameMs >  self.__duration

    #set a timeout that will execcute code once timeoute reached
    #onTimeoutCode : run when the timeout is reached
    #untilTimeCode : run when each frame until duration is reached
    #cancel : this will cancel timeout if a time is already set and set a new one
    def setTimeout(self, duration, currentFrameTs, onTimeoutCode = None, untilTimeoutCode = None, cancel = False):

        if(cancel or self.__timeout):
            self.Reset(duration, currentFrameTs)
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
    def watch(self, animator):
        
        if not self.__timeout:
            if(self.isTimeout(animator.currentFrameTs)):
                if(self.__onTimeoutCode is not None): self.__onTimeoutCode()
                self.__timeout = True
            else:
                if(self.__untilTimeoutCode is not None): self.__untilTimeoutCode(animator.previousFrameDeltaSec)
        
        return self.__timeout

class Ticker:
    
    def __init__(self, animator):
        self.__animator = animator
    
    #bps beat per minute
    #onTick: code to execute on tick
    def setTick(self, bps, onTick, afterTick = None):
        self.__counter = 999999 
        self.__bps = bps
        self.__onTick = onTick
        self.__afterTick = afterTick
    
    def tick(self):
        f = self.__animator.getFramesIntervalFromBps(self.__bps) + 1
        
        self.__counter += 1
        if(self.__counter >= f):
            self.__counter=0
            self.__onTick()
        elif (self.__counter == 1 and self.__afterTick is not None):
            self.__afterTick()


#all to animate or boxes ( sprite and text)
class Animator():


    #todo
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

    
    __minBrightness = 0
    __maxBrightness = 127
    
    def __init__(self):
        self.maxFps=60
        self.currentFrameTs=0 #timestamp at the beginning of the frame so all animation sync on same clock
        self.previousFrameDeltaSec=0 # the difference in second from previous frame to current one
        self.__fpsCpt=0 #incremente fps in current second
        self.__fpsLs=0 # how many frame in last sec
        self.__paused = False #pause all movement
        self.reset()
    
    def reset(self):
        thumby.display.brightness(self.__maxBrightness)
        self.unpause()
        self.resetTimers()

    def initFrame(self, emptyScreen = True):
        currentFrameTs = time.ticks_ms()

        self.previousFrameDeltaSec =  (currentFrameTs - self.currentFrameTs) / 1000
        self.currentFrameTs=currentFrameTs
    
        s=self.currentFrameTs%2000
    
        if s < 1000:
            self.__fpsCpt += 1
        else:
            if self.__fpsCpt > 0:
                self.__fpsLs = self.__fpsCpt
                print(self.__fpsLs)
                self.__fpsCpt = 0
        
        if(emptyScreen):
            self.emptyScreen()
        
    #color : Color.*
    def emptyScreen(self, color = enjfine.Color.BLACK):    
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

    # get the beat per second from an interval in ms
    def getBpsFromInterval(self, interval):
        return 1000 / interval
    
    #fade in or out for a specific duration
    #this function is blocking for the duration of the fade
    #fade: Fade.*
    #duration: the duration of the effect in ms
    #deprecated, use self.fade
    def fadeBlocking(self, fade, duration):
    
        s=self.__minBrightness
        e=self.__maxBrightness
        ratio = e/(duration/1000)
    
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
    
            brightness = brightness + direction * ratio * self.previousFrameDeltaSec
            
            if(brightness < s): 
                brightness = s
                done = True
            if(brightness > e): 
                brightness = e
                done = True
            
            thumby.display.brightness(round(brightness))
            thumby.display.update()
    
    
    #not recommended to use during a gaming loop
    #this is design to be called between loops
    #duration :  time to wait in ms
    #deprecated, replaced by delay
    def wait(self, duration):
    
        initTs = time.ticks_ms()
        while(1):
            if(time.ticks_ms() - initTs >= duration):
                break
            thumby.display.update()    
    
    
    
    #fade in or out for a specific duration
    #fade: Fade.*
    #duration: the duration of the effect in  ms
    #onComplete: code to execute when the fade is completed
    #return a stopwatch so we can control animation
    def fade(self, fade, duration = 0, onComplete = None):
    
        s=0
        e=127
        ratio = e/(duration / 1000) if duration else e*1000
    
        if(fade == Fade.IN):
            self.brightness = s
            direction = 1
        if(fade == Fade.OUT):
            self.brightness = e
            direction = -1
    
        thumby.display.brightness(self.brightness)
        
        def endFade():
            thumby.display.brightness(e if direction == 1 else s)
            if onComplete != None: onComplete()
    
        def fade(previousFrameDeltaSec):
            self.brightness = self.brightness + direction * ratio * previousFrameDeltaSec
            thumby.display.brightness(round(self.brightness))

        return self.doUntil(fade, duration, endFade)
    
    #move a box to a vector distance during a specific duration
    #duration is the time in ms the movement should take to move
    #onComplete: code to execute when the motion is complete
    #return a stopwatch so we can control animation
    def move(self, box, vector, duration, onComplete = None):
        
        ptDestination = box.pt + vector
        vector /= (duration / 1000) # velocity per second
    
        box.pt.velocityGoal = vector
        box.pt.velocity = vector
        
        def stop():
            box.pt = ptDestination
            if onComplete != None: onComplete() 
        
        sw = StopWatch()
        sw.setTimeout(duration, self.currentFrameTs,  stop)
        self.__watches.append(sw)            
        return sw

    #rotate a box around a anchorPt of a specific angle during specif duration
    #duration is the time in ms the movement should take to move,
    #onComplete: code to execute when the motion is complete
    #return a stopwatch to monitor and control the timer   
    def rotate(self, anchorPt, box, degrees, duration, onComplete = None):
        
        if(hasattr(box, "degreesFromAnchor") and box.degreesFromAnchor != None): # we don't allow more than one rotation on a box at a time
            return

        vector = box.getCenterPoint() - anchorPt
        radius = vector.length() 
        box.degreesFromAnchor = vector.getDegrees() #since lamba can't overwrite
        destinationDegrees = (box.degreesFromAnchor + degrees)
        degrees /= (duration / 1000) # degrees to move per second
    
        def stop():
            box.pt = anchorPt.getSatellitePosition(box, destinationDegrees, radius)
            if onComplete != None: onComplete()
            box.degreesFromAnchor = None
        
        def rotate(previousFrameDeltaSec):
      
            box.degreesFromAnchor += (degrees * previousFrameDeltaSec)

            if(degrees > 0 and box.degreesFromAnchor > destinationDegrees): box.degreesFromAnchor = destinationDegrees
            if(degrees < 0 and box.degreesFromAnchor < destinationDegrees): box.degreesFromAnchor = destinationDegrees

            box.pt = anchorPt.getSatellitePosition(box, box.degreesFromAnchor, radius)
             
        return self.doUntil(rotate, duration, stop)   

        

    #wait some time before executing some completion code
    #onComplete : code to execute
    #return a stopwatch to monitor and control the timer
    def delay(self, duration, onComplete):

        sw = StopWatch()
        sw.setTimeout(duration, self.currentFrameTs,  onComplete)
        self.__watches.append(sw)
        return sw

    #exectute a code on each frame
    #onFrameCallback the call to execute, this function receive the interval in sec with previous frame
    #duration, if duration is -1 , the execution will happen forever
    #onComplete, code to execute after duration
    #return a stopwatch to monitor and control the timer
    def doUntil(self, onFrameCallback, duration = -1, onComplete = None):

        sw = StopWatch()
        sw.setTimeout(duration, self.currentFrameTs,  onComplete, onFrameCallback)
        self.__watches.append(sw)
        return sw

    #similar to self.doUntil, but for none movement animation, this offer beat per second precision at any framerate
    #bps: beat per second
    #onTick: the code to execute
    #afterTick : code to execute the frame after the tick frame
    #expiredMs: if not -1, the delay before the tick die
    #onExpire: code to run when ticker die
    #return a stopwatch to monitor and control the timer
    def tick(self, bps, onTick, afterTick = None,  expiredMs = -1, onExpire = None):

        tk = Ticker(self)
        tk.setTick(bps, onTick, afterTick)
        self.__tickers.append(tk)
        
        def code():
            if(onExpire != None): onExpire()
            self.__tickers.remove(tk)
            
        return self.delay(expiredMs, code)

    #watch for time events
    def runTimers(self):
        for index in range(len(self.__watches)-1, -1, -1):
            if self.__watches[index].watch(self):
                self.__watches.pop(index)
        for tick in self.__tickers:
            tick.tick()

    #reset all existing watches and ticks
    def resetTimers(self):
        self.__watches = []
        self.__tickers = []

    
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
        
        v = targetPoint - boxOrigin.getCenterPoint()
    
        return v / t
    
    #return a collection of spriteBox that collide with main sprintBox
    #main : the target BoxObj we test collision againts
    #filterId : only test sprite with a particular id
    def detectCollision(self, main, boxObjects, filterId = None):

        collides = []

        if not main.hide:
            for target in boxObjects:

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
        
        delta_s = self.previousFrameDeltaSec
        
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


