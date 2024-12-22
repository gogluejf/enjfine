
import thumby
import math
import random
import sys


sys.path.insert(0, '/Games/enjfine')
import enjfine
import effects

class SpaceGame:

    title1 = "Space"
    title2 = "Shooter"

    game_map = bytearray([0,24,48,192,252,0,1,2,7,6,8,192,120,8,24,16,48,192,192,0,0,4,24,32,70,172,192,192,0,0,0,0,0,0,0,0,0,0,0,
           0,0,0,1,7,196,192,128,128,128,0,1,30,224,0,4,15,17,96,195,130,4,8,176,192,128,0,0,1,194,112,96,192,128,0,0,0,0,0,
           0,0,0,0,0,31,224,128,6,125,75,84,108,95,56,192,0,0,0,0,1,7,3,1,0,1,2,6,60,207,176,44,38,79,118,76,48,192,0,
           0,0,0,0,0,0,0,1,7,12,112,192,0,0,0,1,3,6,0,0,0,0,0,0,0,0,0,0,0,0,31,0,0,0,0,0,24,8,159,
           0,0,0,0,0,0,0,0,0,0,0,3,51,52,24,16,16,16,32,32,32,32,48,32,144,216,136,136,100,196,196,246,226,114,38,250,243,129,1])  


    __bg_space_map = bytearray([0,0,0,0,0,0,0,0,0,0,0,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,128,192,96,32,32,0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,3,7,12,8,8,0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,0,
           0,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])
           
    __squid = bytearray([0,224,24,4,2,2,129,1,1,153,26,34,4,24,224,0,0,1,2,130,196,196,233,232,232,233,196,196,130,2,1,0,0,8,16,35,38,24,1,79,60,0,15,16,129,79,56,0])
           
    def initGame(self):
    
        self.__ship = Ship(self.drawer)
        self.__pillsHandler = PillsHandler(self.drawer)
        self.__levelHandler = LevelHandler(self.drawer, self.__ship)
        
        effect = effects.BackgroundEffect(self.drawer, {
            "map" : self.__bg_space_map,
            "map_dimension" : enjfine.Dimension(self.drawer.screenBox.dim.w, 40),
            "offset_y" : 0,
            "bg_box" : self.drawer.screenBox,
            "layer" : 3,
        })
        effect.init(self.__ship.boxobj)
        
    def update(self):

        #control the ship
        #self.drawer.controller.twoAxisFreeMove(self.__ship.boxobj, 60, 300)
        self.drawer.controller.OneAxisOneButtonMove(self.__ship.boxobj, self.__ship.system.speed, self.__ship.system.speed*5, enjfine.controller.Axis.Y)
   
        #game physic
        self.__pillsHandler.detectPillConsumed(self.__ship)
        self.__ship.missileHandler.detectCollision(self.__levelHandler.badguys, self.__pillsHandler)
            

        #using bombs
        if(thumby.buttonA.justPressed()):
            if(self.__ship.detonatepBomb()):
                pass
        
        #changing weapon
        if(thumby.buttonB.justPressed()):
            self.__ship.changeMissileMode()

    
        #temp to debug
        if(self.drawer.controller.pressed(enjfine.controller.Button.A | enjfine.controller.Button.B, enjfine.controller.Operator.AND)):
            self.__ship.reset()

        return True


class LevelHandler:

    __devil_map = bytearray([0,102,217,204,124,204,217,102])       

    def __init__(self, drawer, ship):

        self.__drawer = drawer
        self.__distance = 0
        self.__timer = 0 #timer in secondes
        self.__lastBadGuySpawn = 0
        self.badguys = []
        
        def trackDistance(previousFrameDeltaSec):
            
            self.__distance += previousFrameDeltaSec * ship.boxobj.box.pt.velocity.x
            self.__timer += previousFrameDeltaSec
     
            #spawn new badguy
            if(self.__timer - self.__lastBadGuySpawn) > 3:
                self.__spanwBadguy()
                self.__lastBadGuySpawn = self.__timer
            
            #remove bad guys
            for badguy in self.badguys:
                if(badguy.box.pt.x < self.__drawer.screenBox.pt.x or badguy.hide == True):
                    self.__removeBadguy(badguy)

        self.__drawer.animator.doUntil(trackDistance)

    def __removeBadguy(self, badguy):
        self.badguys.remove(badguy)
        self.__drawer.data.spriteBoxes.remove(badguy)

    def __spanwBadguy(self):
        
        vposition = random.choice([enjfine.VPosition.TOP, enjfine.VPosition.MIDDLE, enjfine.VPosition.BOTTOM])
        
        badguy = enjfine.sprite.SpriteBox(self.__devil_map, enjfine.Dimension(8, 8))
        badguy.box.pt = self.__drawer.screenBox.getDimensionPosition(badguy.box.dim, enjfine.Position.RIGHT, vposition)
        
        #arrive fast and slow down effect
        badguy.box.pt.velocity.x = -100
        badguy.box.pt.velocityGoal.x = -10
        badguy.box.pt.vAcceleration.x = 200
    
        self.__drawer.data.spriteBoxes.append(badguy)
        self.badguys.append(badguy)
    
        #goaway fast
        def goaway():
            badguy.box.pt.velocityGoal.x = -100
        
        self.__drawer.animator.delay(1000, goaway)

        
    
class Ship:
    
    __ship_map = bytearray([0,224,224,192,0,192,2,226,6,246,4,240,16,80,144,32,192,0,0,3,3,1,0,1,32,35,48,55,16,7,10,10,10,2,1,0])
    __ship_map_mask = bytearray([224,240,240,224,224,226,231,247,255,255,254,252,248,248,248,240,224,192,3,7,7,3,3,35,115,119,127,127,63,31,31,31,31,15,3,1])
    
    __fire_map = bytearray([0,4,10,17,21]) + bytearray([4,10,17,21,0])
    def __init__(self, drawer):

        self.__drawer = drawer
        
        self.system = ShipSystem()
        self.__shieldHandler = ShieldHandler(self.__drawer)
        self.missileHandler = MissileHandler(self.__drawer)
        self.__bombHandler = BombHandler(self.__drawer)

        self.__drawer.animator.tick(10, lambda: self.missileHandler.burst(self.boxobj))

        self.reset()
    
        screen = self.__drawer.screenBox
        
        #the ship movement box
        box = enjfine.Box(enjfine.Point(5,0), enjfine.Dimension(16, screen.dim.h))

        #create the ship
        self.boxobj = enjfine.sprite.SpriteBox(self.__ship_map, enjfine.Dimension(18, 15), self.__ship_map_mask, enjfine.Box(enjfine.Point(-1,-1),enjfine.Dimension(16,13)))
        self.boxobj.box.pt = box.getDimensionPosition(self.boxobj.box.dim, enjfine.Position.LEFT, enjfine.VPosition.MIDDLE)
        self.boxobj.box.pack(box, enjfine.animator.BoxedEffect.BLOCK)
        self.__drawer.data.spriteBoxes.append(self.boxobj)

        #make the ship always moving forward
        self.boxobj.box.pt.velocityGoal.x = 50
        self.boxobj.box.pt.velocity.x = 50

        #animate fire behind the ship
        self.__fire = enjfine.sprite.SpriteBox(self.__fire_map, enjfine.Dimension(5,5), None, None, 2)
        self.__fire.setAnimate(self.__drawer.animator.maxFps)
        self.__fire.box.pt.velocityGoal.x = self.boxobj.box.pt.velocityGoal.x
        self.__fire.box.pt.velocity.x = self.boxobj.box.pt.velocity.x
        self.__drawer.data.spriteBoxes.append(self.__fire)            

        effect = effects.BlinkEffect(self.__drawer)
        effect.init(self.__fire)

        #track fire mouvement to follow the ship mouvement
        def trackFire(previousFrameDeltaSec):
            self.__fire.box.pt = self.boxobj.box.getDimensionPosition(self.__fire.box.dim, enjfine.Position.LEFT_OUTER, enjfine.VPosition.MIDDLE)
        
        self.__drawer.animator.doUntil(trackFire)

    def setShield(self):
        if(self.system.shield == True):
            return 
        self.system.setShield(True)
        self.__shieldHandler.activate(self.boxobj)
    
    def removeShield(self):
        if(self.system.shield == False):
            return 
        self.system.setShield(False)
        self.__shieldHandler.desactivate()

    def setInvisible(self):
        if(self.system.invisible == True):
            self.endInvisible()
        
        self.system.setInvisible(True)
        
        effect = effects.FlashEffect(self.__drawer)
        self.__swInvisibleEffect = effect.init(self.boxobj, 10000)
        self.__swInvisible = self.__drawer.animator.delay(10000, lambda: self.system.setInvisible(False))

    def endInvisible(self):
        if(self.system.invisible == False):
            return 
        self.__swInvisible.forceTimeout()
        self.__swInvisible = None
        self.__swInvisibleEffect.forceTimeout()
        self.__swInvisibleEffect = None
        self.system.setInvisible(False)
    
    #try to detonate a bomb
    #will return true if we still have some bomb and we detonated one
    def detonatepBomb(self):
        if(self.system.bombs <= 0):
            return False
        self.__bombHandler.detonate(self.boxobj)
        self.system.removeBomb()
        return True
        
    #toggle from power to spread and vice versa
    def changeMissileMode(self):
        if(self.system.mode == self.system.MissileMode.POWER): 
            self.system.setMissileMode(self.system.MissileMode.SPREAD)
        else:
            self.system.setMissileMode(self.system.MissileMode.POWER)
        self.activateMissile()
    
    #active missle physic base on system state
    def activateMissile(self):
        if(self.system.mode == self.system.MissileMode.POWER):  self.missileHandler.setPower(self.system.power, self.system.bullets)
        if(self.system.mode == self.system.MissileMode.SPREAD):  self.missileHandler.setSpread(self.system.spread)

    #reset all upgrade on the ship
    def reset(self):
        self.removeShield()
        self.endInvisible()
        self.system.reset()
        self.activateMissile()

#the system satus reprenseting the current ship upgrades
#the ship system allow to get current state, mode and inventory, but also to increaset upgrade while respecting limits
class ShipSystem:
    
    class MissileMode():
        POWER = 1
        SPREAD = 2

    __max_speed = 120
    __max_bullets = 4
    __max_power = 3
    __max_spread = 3
    __max_bombs = 3

    def __init__(self):
        self.reset()

    def reset(self):
        self.speed = 30
        self.shield = False
        self.invisible = False
        self.bombs = 1
        self.resetMissile()
    
    def resetMissile(self):
        self.mode = self.MissileMode.POWER
        self.bullets = 1
        self.spread = 0
        self.power = 0

    #toggle the missle mode
    #mode :  self.MissileMode.*
    def setMissileMode(self, mode):        
        self.mode = mode
    
    def increaseSpeed(self):
        if(self.speed >= self.__max_speed):
            return
        self.speed += 30        

    #protect shield for 1 hit
    def setShield(self, state = True):    
        self.shield = state    

    def setInvisible(self, state = True):
        self.invisible = state    
    
    #increase number of simultanous bullets
    def inscreaseBullets(self):
        if(self.bullets == self.__max_bullets):
            return
        self.bullets += 1            

    #increase the power weapon level
    def upgradePower(self):    
        if(self.power == self.__max_power):
            return
        self.power += 1

    #inscrease the spread weapon level
    def upgradeSpread(self):
        if(self.spread == self.__max_spread):
            return
        self.spread += 1

    def addBomb(self):    
        if(self.bombs == self.__max_bombs):
            return
        self.bombs += 1
    
    def removeBomb(self):
        if(self.bombs == 0):
            return
        self.bombs -= 1

#upgrade pills
class PillsHandler:

    class Type():
        SPEED = 1 #increase ship speed
        SHIELD = 2 #activate a shield
        MISSILE = 3 #increase missles cadence
        SPREAD = 4 #increase missle spreading
        POWER = 5 #inline missle, increase  missle power
        INVISIBLE = 6 #activate invisibility for few seconds
        BOMB = 7 #stock an additional bomb

    __pill_diretion_velocity = [-15,-10, -5, 5, 10, 15]

    __pill_maps = {
        Type.SPEED: bytearray([0,248,4,34,34,170,114,34,4,248,0,0,0,1,2,2,2,2,2,1,0,0]), 
        Type.SHIELD: bytearray([0,248,4,2,186,170,234,2,4,248,0,0,0,1,2,2,2,2,2,1,0,0]),
        Type.MISSILE: bytearray([0,248,4,34,34,114,114,34,4,248,0,0,0,1,2,2,2,2,2,1,0,0]),
        Type.SPREAD: bytearray([0,248,36,34,82,82,170,170,4,248,0,0,0,1,2,2,2,2,2,1,0,0]),
        Type.POWER: bytearray([0,248,4,2,250,42,58,2,4,248,0,0,0,1,2,2,2,2,2,1,0,0]),
        Type.INVISIBLE: bytearray([0,248,4,2,138,250,138,2,4,248,0,0,0,1,2,2,2,2,2,1,0,0]),
        Type.BOMB: bytearray([0,248,4,114,250,250,250,114,4,248,0,0,0,1,2,2,2,2,2,1,0,0])
    }

    __pill_map_mask = bytearray([248,252,254,255,255,255,255,255,254,252,248,0,1,3,7,7,7,7,7,3,1,0])        

    def __init__(self, drawer):
        self.__drawer = drawer
        self.__pills = []
    
    #spawn an upgrade pills 
    def spawnPill(self, pt):
       
        type = random.randint(1,7)
       
        pill = enjfine.sprite.SpriteBox(self.__pill_maps[type], enjfine.Dimension(11, 11), self.__pill_map_mask, enjfine.Box(enjfine.Point(-1,-1), enjfine.Dimension(9,9)))
        pill.box.pack(self.__drawer.screenBox, enjfine.animator.BoxedEffect.BOUNCE)
        pill.id = "pill"
        pill.__pillType = type
        self.__drawer.data.spriteBoxes.append(pill)
        self.__pills.append(pill)

        pill.box.pt = pt.copy()
        pill.box.pt.velocityGoal = enjfine.Vector(random.choice(self.__pill_diretion_velocity),random.choice(self.__pill_diretion_velocity))

    def detectPillConsumed(self, ship):
     
        pills = self.__drawer.animator.detectCollision(ship.boxobj, self.__pills)
        for pill in pills:
            self.__drawer.data.spriteBoxes.remove(pill)
            self.__pills.remove(pill)

            if(pill.__pillType == self.Type.SPEED): 
                ship.system.increaseSpeed()
            if(pill.__pillType == self.Type.SHIELD): 
                ship.setShield()               
            if(pill.__pillType == self.Type.MISSILE): 
                ship.system.inscreaseBullets()
                ship.activateMissile()
            if(pill.__pillType == self.Type.SPREAD):
                ship.system.upgradeSpread()
                ship.activateMissile()
            if(pill.__pillType == self.Type.POWER): 
                ship.system.upgradePower()
                ship.activateMissile()
            if(pill.__pillType == self.Type.INVISIBLE): 
                ship.setInvisible()
            if(pill.__pillType == self.Type.BOMB): 
                ship.system.addBomb()   

            #todo, dispatch upgrade
            #shield around
            
            #if(thumby.buttonR.justPressed()):   self.__shield.activate(self.__ship.boxobj)
            #if(thumby.buttonL.justPressed()):   self.__shield.desactivate()

class MissileHandler:

    __missile_dim_lv = [
        enjfine.Dimension(6, 3), 
        enjfine.Dimension(6, 7), 
        enjfine.Dimension(8, 11), 
        enjfine.Dimension(8, 15)]
        
    __missile_map_lv = [
        bytearray([2,2,2,7,7,2]), 
        bytearray([34,34,34,119,119,34]), 
        bytearray([2,2,34,39,39,114,112,32,2,2,2,7,7,2,0,0]), 
        bytearray([2,2,34,39,39,114,112,32,32,32,34,114,114,39,7,2])]

    #missiles settings
    __speed = 100 #speed goal of missle
    __acceleration = 500 #missle acceleration
    __spread_lv = [ [0],
                    [-10, 10],
                    [-20,0, 20],
                    [-40, -15, 15, 40]]

    def __init__(self, drawer):
        self.__drawer = drawer
        self.__missiles = []
        self.reset()

    #mechanism to shoot missiles
    def burst(self, ship):    
        for index in range(len(self.__missiles)-1, -1, -1):
            if self.__missiles[index].box.pt.x > self.__drawer.screenBox.dim.w:
                missile = self.__missiles.pop(index)
                self.__drawer.data.spriteBoxes.remove(missile)
        
        if(len(self.__missiles) < self.__bullets * (self.__spread+1)):
            self.__shoot(ship)

    #shoot a single missle
    #ship: the object that shoot the missile
    def __shoot(self, ship):

        for angle in self.__spread_lv[self.__spread]:
            missile = enjfine.sprite.SpriteBox(self.__missile_map_lv[self.__power], self.__missile_dim_lv[self.__power])
            missile.id = "missile"
            missile.box.pt = ship.box.getDimensionPosition(missile.box.dim, enjfine.Position.RIGHT_OUTER, enjfine.VPosition.MIDDLE)
            missile.box.pt.velocityGoal = enjfine.Vector(self.__speed, angle)
            missile.box.pt.velocity = enjfine.Vector(self.__speed, angle)
            missile.box.pt.vAcceleration = enjfine.Vector(self.__acceleration, self.__acceleration)
            self.__missiles.append(missile)
            self.__drawer.data.spriteBoxes.append(missile)

    #reset all upgrade on missile
    def reset(self):
        self.__bullets = 1 #how many bullets simultanous on the screen
        self.__power = 0 # level 0 to 2
        self.__spread = 0        

    def remove(self, missile):
        self.__missiles.remove(missile)
        self.__drawer.data.spriteBoxes.remove(missile)

    #increase missile power
    #cancel spread
    def setPower(self, power, bullets):    
        self.__power  = power
        self.__bullets = bullets
        self.__spread = 0    

    #increase missile power
    #cancel power and reset to 1 bullet
    def setSpread(self, spread):
        self.__spread = spread
        self.__bullets = 1
        self.__power = 0

    def detectCollision(self, badguys, pillsHandler):
     
        for badguy in badguys:
            missiles = self.__drawer.animator.detectCollision(badguy, self.__drawer.data.spriteBoxes, "missile")
            for missile in missiles:
                
                self.remove(missile)
                if(random.randint(1,3) == 1):
                    pillsHandler.spawnPill(badguy.box.getCenterPoint())
                
                badguy.hide = True
                effect = effects.ExploseEffect(self.__drawer, {"particles": 24})
                effect.init(badguy, 2000)


class BombHandler:

    def __init__(self, drawer):
        self.__drawer = drawer

    #will detonate a bomb 
    #detonator :  the object that detonate the bomb
    def detonate(self, detonator):
        def bomb():
            effect = effects.CircleWaveEffect(self.__drawer, {"loop" : False})
            effect.init(detonator, 1200)
            
        self.__drawer.animator.delay(100, bomb)
        
        effect = effects.FlashEffect(self.__drawer)
        effect.init(detonator, 200)

class ShieldHandler:
    
    __ball_map_1 = bytearray([1])
    __ball_map_2 = bytearray([2,7,2])
    __ball_map_3 = bytearray([6,15,15,6])        
    
    __endShieldDuration = 1500 # animation duration for ending shield
    
    def __init__(self, drawer):
        self.__drawer = drawer
        self.__shieldSw = None

        self.__ball1 = enjfine.sprite.SpriteBox(self.__ball_map_1, enjfine.Dimension(1,1))
        self.__ball2 = enjfine.sprite.SpriteBox(self.__ball_map_2, enjfine.Dimension(3,3))
        self.__ball3 = enjfine.sprite.SpriteBox(self.__ball_map_3, enjfine.Dimension(4,4))

    #targetL the object the shield will turn around
    def activate(self, target):
        self.__target = target
        
        if(self.__shieldSw != None):
            return
         
        self.__shieldDegrees = 0
        self.__radius = 10+15
        self.__rotationSpeed = 540+270
        def rotateShield(previousFrameDeltaSec):
            self.__shieldDegrees += (self.__rotationSpeed * previousFrameDeltaSec)
            self.__shieldDegrees %= 360

            self.__ball1.box.pt = self.__target.box.getCenterPoint().getSatellitePosition(self.__ball1.box, self.__shieldDegrees, self.__radius)
            self.__ball2.box.pt = self.__target.box.getCenterPoint().getSatellitePosition(self.__ball2.box, self.__shieldDegrees+30, self.__radius)
            self.__ball3.box.pt = self.__target.box.getCenterPoint().getSatellitePosition(self.__ball3.box, self.__shieldDegrees+60, self.__radius)

        self.__drawer.data.spriteBoxes.append(self.__ball1)
        self.__drawer.data.spriteBoxes.append(self.__ball2)
        self.__drawer.data.spriteBoxes.append(self.__ball3)

        def encloseBalls(previousFrameDeltaSec):
            self.__radius -= (30*previousFrameDeltaSec)
            self.__rotationSpeed -= (540*previousFrameDeltaSec)
        def endEncloseBalls():
            self.__radius = 10
            self.__rotationSpeed = 540

        self.__drawer.animator.doUntil(encloseBalls, 500, endEncloseBalls)

        self.__shieldSw = self.__drawer.animator.doUntil(rotateShield) #, -1, endShield)
        
    def desactivate(self):

        if(self.__shieldSw == None):
            return

        def endShield():
            if(self.__shieldSw != None):
                self.__drawer.data.spriteBoxes.remove(self.__ball1)
                self.__drawer.data.spriteBoxes.remove(self.__ball2)
                self.__drawer.data.spriteBoxes.remove(self.__ball3)
            self.__shieldSw = None
        
        self.__shieldSw.forceTimeout()
        
        self.__ball1.box.pt.velocityGoal.y = 120
        self.__ball1.box.pt.vAcceleration.y = 60
        self.__ball2.box.pt.velocityGoal.y = 120
        self.__ball2.box.pt.vAcceleration.y = 80
        self.__ball3.box.pt.velocityGoal.y = 120
        self.__ball3.box.pt.vAcceleration.y = 40
        
        self.__drawer.animator.delay(self.__endShieldDuration, endShield)
        
        effect = effects.ShakeEffect(self.__drawer)
        effect.init(self.__target, 300)
        effect.initMany([self.__ball1, self.__ball2, self.__ball3], self.__endShieldDuration)
        

runner = enjfine.runner.GameRunner(SpaceGame())
runner.run()



"""
ShipStatus
    Speed (1-5)             [xxx]
    Missile
        Cadence ( 1, 4)     [xxx]
        Power (0-3)         [xxx]
        spread (0-3)        [xxx]
        Mode (spread|bulk)
    Shield (true|false)     [x]
    Bomb (1-3)              [xx]
    Invisible



#self.drawer.animator.rotate(self.__anchorPt, self.__devil.box, 270, 500)


background
    arrive
    go away

pills system
ennemis sequence

boss system
boss presentation
charging weapon

score, level, life, etc
bubble effects..,...




+ invisible
"""

