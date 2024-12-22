
class HockeyGame:

    __player_map = bytearray([0,24,60,230,190,36,24,0,0,0,0,16,28,7,28,17,2,4,4,0])
    __player_map_mask = bytearray([24,60,254,255,255,254,60,24,0,0,16,60,63,31,63,63,23,14,14,4])
    __center_line_map = bytearray([0,0,0,85,0,0,0,0,0,0,85,0,0,0,20,0,65,8,65,0,20,0,0,0,85,0,0,0,0,0,0,85,0,0,0])
    __puck_map = bytearray([0,12,26,26,26,12,0])
    __puck_map_mask = bytearray([12,30,63,63,63,30,12])
    __net_map = bytearray([254,85,171,1,7,13,10,8])
    
    __player_collide_w=5
    __player_collide_h=5
    __player_offset_h=8
    
    def __init__(self):
        self.__iceBox = Box(Point(0, 0), Dimension(thumby.display.width, thumby.display.height))

    class Team():
        YOU=0
        CPU=1
    
    def initGame(self):

        #init score
        self.__score = {self.Team.YOU: 0, self.Team.CPU: 0}
        txt = self.drawer.textDrawer.TextBox(self.drawer.textDrawer.Text("{0} {1}".format(self.__score[self.Team.YOU], self.__score[self.Team.CPU])))
        txt.box.pt = self.__iceBox.getDimensionPosition(txt.box.dim, Position.CENTER, VPosition.TOP)
        self.drawer.textBoxes.append(txt) 
        
        #init ice
        bl = BlitBox(self.__center_line_map, Dimension(7, 40))
        bl.box.pt = self.__iceBox.getDimensionPosition(bl.box.dim)
        self.drawer.blitBoxes.append(bl)   
        
        #init nets
        self.__nets = {}
        self.__nets[self.Team.YOU] = self.__initNet(self.Team.YOU)
        self.__nets[self.Team.YOU] = self.__initNet(self.Team.CPU)
        
        #init players
        self.__players = []
        self.__players.append(self.__initHockeyPlayer(self.Team.CPU, Point(self.__iceBox.dim.w-10-self.__player_collide_w,  self.__iceBox.dim.h-2-self.__player_collide_h)))
        self.__players.append(self.__initHockeyPlayer(self.Team.CPU, Point(self.__iceBox.dim.w-10-self.__player_collide_w, 2+self.__player_offset_h)))
        self.__players.append(self.__initHockeyPlayer(self.Team.YOU, Point(10, self.__iceBox.dim.h-2-self.__player_collide_h)))
        self.__mainPlayer = self.__initHockeyPlayer(self.Team.YOU, Point(10, 2+self.__player_offset_h))
        self.__mainPlayer.setEffect(SpriteEffect.FLASH, {"bps" : 3})
        self.__players.append(self.__mainPlayer)

        #init pu 1k
        self.__puck = SpriteBox(self.__puck_map, Dimension(7,6), self.__puck_map_mask, Box(Point(-1,-1), Dimension(5,4)))
        self.__puck.box.pt = Point(18,26) #self.drawer.screenBox.getCenterPoint()
        self.__puck.box.pt.vAcceleration =  self.__puck.box.pt.vAcceleration / 3

        self.__puck.box.pack( self.__iceBox, BoxedEffect.BOUNCE)
        self.drawer.spriteBoxes.append(self.__puck)

        self.__puck.id = "puck"

    #init a net BlitBox and return it
    def __initNet(self, team):

        bl = BlitBox(self.__net_map, Dimension(4, 12))
        if team == self.Team.YOU:
            bl.box.pt = self.__iceBox.getDimensionPosition(bl.box.dim, Position.LEFT)
        if team == self.Team.CPU:
            bl.box.pt = self.__iceBox.getDimensionPosition(bl.box.dim, Position.RIGHT)
            bl.mirrorX = 1    

        self.drawer.blitBoxes.append(bl)  
        return 

    # initiate an hockey player SpriteBox and return it
    def __initHockeyPlayer(self, team, pt):

        player = SpriteBox(self.__player_map, Dimension(10, 14), self.__player_map_mask, Box(Point(-1,-self.__player_offset_h), Dimension(self.__player_collide_w, self.__player_collide_h)))
        player.box.pack(self.__iceBox, BoxedEffect.BOUNCE)
        player.box.pt = pt
        if(team == self.Team.CPU):
            player.setEffect(SpriteEffect.INVERT)
            player.sprite.mirrorX=1
        self.drawer.spriteBoxes.append(player)
        
        player.id = "player"
        player.team = team
        
        return player
    
    def ai(self):
        
        for player in self.__players:
            if player.team != self.Team.CPU:
                continue

            player.box.pt.velocityGoal = self.__puck.box.getCenterPoint() - player.box.getCenterPoint()
            player.sprite.mirrorX = 1 if(player.box.pt.velocityGoal.x < 0) else 0

    def update(self):

        self.drawer.controller.twoAxisFreeMove(self.__mainPlayer)

        #collision engine
        for spriteBox in self.drawer.spriteBoxes:
            
            box1 = self.__mainPlayer.box
            box2 = spriteBox.box
    
            if(box1 == box2):
                continue
            
            xcollide = False
            ycollide = False
            
            if((box1.pt.x >= box2.pt.x and box1.pt.x <= box2.pt.x + box2.dim.w) or (box2.pt.x >= box1.pt.x and box2.pt.x <= box1.pt.x + box1.dim.w)):
                 xcollide = True
            if((box1.pt.y >= box2.pt.y and box1.pt.y <= box2.pt.y + box2.dim.h) or (box2.pt.y >= box1.pt.y and box2.pt.y <= box1.pt.y + box1.dim.h)):
                 ycollide = True
    
            if(xcollide and ycollide):
                
                box1.pt.x = box2.pt.x+box2.dim.w if box1.pt.velocity.x < 0 else box2.pt.x-box1.dim.w
                box1.pt.y = box2.pt.y+box2.dim.h if box1.pt.velocity.y < 0  else box2.pt.y-box1.dim.h
                
                if(spriteBox.id == "puck"):
                    #box2.pt.velocityGoal = box1.pt.velocityGoal / 2
                    box2.pt.velocity = box1.pt.velocity * 2    
                    box1.pt.velocityGoal = box1.pt.velocityGoal * -1 / 1.5
                    box1.pt.velocity = box1.pt.velocity * -1 / 1.5       
    
                if(spriteBox.id == "player"):
                    box1.pt.velocityGoal = box1.pt.velocityGoal * -1
                    box1.pt.velocity = box1.pt.velocity * -1  
                    spriteBox.setEffect(SpriteEffect.EXPLODE, {}, 3000, self.drawer.animator.currentFrameTs )


        #aiming at moving target
        if(thumby.buttonB.justPressed()):
            speed = 50
            v = self.drawer.animator.aimToTarget(self.__puck.box, self.__mainPlayer.box, speed)

            self.__puck.box.pt.velocityGoal += (v)
            self.__puck.box.pt.velocity += (v)
            self.__puck.box.pt.vAcceleration = Vector(speed, speed)

        if(thumby.buttonA.justPressed()):
            self.__puck.box.pt.velocityGoal = Vector(0,0)
            self.__puck.box.pt.velocity = Vector(0,0)
        
        #self.ai()
        
   
class PlatformerGame:
    
    # BITMAP: width: 72, height: 30
    __bg_far_map = bytearray([0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,4,0,0,0,0,0,0,0,64,0,0,0,0,0,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,192,224,48,16,16,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,1,3,6,4,4,0,32,0,0,0,0,0,
           0,0,0,0,0,1,0,0,0,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,128,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    # BITMAP: width: 5, height: 7 <- optimized ( just moon)
    #bg_far_map = bytearray([28,62,99,65,65])
    #self.__bgFar1 = SpriteBox(bg_far_map, Dimension(5,7), None, Box(Point(60,5),Dimension(drawer.screenBox.dim.w, 30)))
    #self.__bgFar1.box.pack(drawer.screenBox, BoxedEffect.WRAP)
    #self.__bgFar2 = SpriteBox(bg_far_map, Dimension(5,7), None, Box(Point(60,5),Dimension(drawer.screenBox.dim.w, 30)))
    #self.__bgFar2.box.pt.setPoint(drawer.screenBox.dim.w,0)
    #self.__bgFar2.box.pack(drawer.screenBox, BoxedEffect.WRAP)


    # BITMAP: width: 72, height: 10
    __bg_close_map = bytearray([0,0,0,0,0,0,0,0,128,64,32,16,8,4,2,84,168,80,160,64,128,0,0,0,0,0,0,0,0,0,0,128,64,32,64,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,112,64,248,64,96,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,0,0,0,0,0,0,0,1,2,1,2,1,2,1,2,0,0,0,0,0,0,2,1,0,0,0,1,2,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,2,1,2,0,0])


    __skull_map = bytearray([0,120,252,102,254,102,252,120,0,0,0,1,0,1,0,1,0,0])
    __skull_map_mask = bytearray([120,252,254,255,255,255,254,252,120,0,1,3,3,3,3,3,1,0])
    
    def initGame(self):
        
        screen = self.drawer.screenBox

        self.__bgFar1 = BlitBox(self.__bg_far_map, Dimension(screen.dim.w, 30))
        self.__bgFar1.box.pack(screen, BoxedEffect.WRAP)
        self.drawer.blitBoxes.append(self.__bgFar1)
        
        self.__bgFar2 = BlitBox(self.__bg_far_map, Dimension(screen.dim.w, 30))
        self.__bgFar2.box.pt.setPoint(screen.dim.w,0)
        self.__bgFar2.box.pack(screen, BoxedEffect.WRAP)
        self.drawer.blitBoxes.append(self.__bgFar2)        
        
        self.__bgClose1 = BlitBox(self.__bg_close_map, Dimension(screen.dim.w, 10))
        self.__bgClose1.box.pt.setPoint(0, 30)
        self.__bgClose1.box.pack(screen, BoxedEffect.WRAP)
        self.drawer.blitBoxes.append(self.__bgClose1)
        
        self.__bgClose2 = BlitBox(self.__bg_close_map, Dimension(screen.dim.w, 10))
        self.__bgClose2.box.pt.setPoint(screen.dim.w, 30)
        self.__bgClose2.box.pack(screen, BoxedEffect.WRAP)
        self.drawer.blitBoxes.append(self.__bgClose2)        
        
        self.__skull = SpriteBox(self.__skull_map, Dimension(9, 10), self.__skull_map_mask, Box(Point(-1,-1), Dimension(7,8)))
        self.__skull.box.pack(Box(Point(10,0), screen.dim - Dimension(20,0)), BoxedEffect.BLOCK)
        self.drawer.spriteBoxes.append(self.__skull)    

    def update(self):
        
        self.drawer.controller.platformerJumper(self.__skull)    
            
        #scroll background    
        box = self.__skull.box
        parent = box.parent
        collision = False
    
        if(box.pt.x+box.dim.w>=parent.pt.x+parent.dim.w): collision = True
        if(box.pt.x<=parent.pt.x): collision = True
    
        if(collision):
            speed = -4
     
            self.__bgFar1.box.pt.vAcceleration.x = box.pt.vAcceleration.x / abs(speed)
            self.__bgFar1.box.pt.velocityGoal.x = box.pt.velocityGoal.x / speed
            self.__bgFar1.box.pt.velocity.x = box.pt.velocity.x / speed
            
            self.__bgFar2.box.pt.vAcceleration.x = box.pt.vAcceleration.x / abs(speed)
            self.__bgFar2.box.pt.velocityGoal.x = box.pt.velocityGoal.x / speed 
            self.__bgFar2.box.pt.velocity.x = box.pt.velocity.x / speed    
        
            speed = -1
        
            self.__bgClose1.box.pt.vAcceleration.x = box.pt.vAcceleration.x / abs(speed)
            self.__bgClose1.box.pt.velocityGoal.x = box.pt.velocityGoal.x / speed
            self.__bgClose1.box.pt.velocity.x = box.pt.velocity.x / speed
            
            self.__bgClose2.box.pt.vAcceleration.x = box.pt.vAcceleration.x / abs(speed)
            self.__bgClose2.box.pt.velocityGoal.x = box.pt.velocityGoal.x / speed
            self.__bgClose2.box.pt.velocity.x = box.pt.velocity.x / speed   
        
        else:
            self.__bgFar1.box.pt.velocityGoal.x = 0
            self.__bgFar1.box.pt.velocity.x = 0
            
            self.__bgFar2.box.pt.velocityGoal.x = 0 
            self.__bgFar2.box.pt.velocity.x = 0    
    
            self.__bgClose1.box.pt.velocityGoal.x = 0
            self.__bgClose1.box.pt.velocity.x = 0
            
            self.__bgClose2.box.pt.velocityGoal.x = 0
            self.__bgClose2.box.pt.velocity.x = 0
      
  
class DragonDotsGame:
    
    __dragon_map = bytearray([0,0,0,0,0,0,252,252,96,96,224,224,224,0,0,0,192,192,240,240,63,63,63,63,254,254,255,255,243,243,51,51])

    # BITMAP: width: 16, height: 16
    __soldier_map = bytearray([0,0,0,68,36,20,8,28,162,162,42,28,0,0,0,0,0,0,0,224,96,96,114,55,31,255,244,132,14,2,2,6])

    def initGame(self):
        self.__dragon = SpriteBox(self.__dragon_map, Dimension(16,16))
        grid = Grid(Point(), self.__dragon.box.dim, 4, 2)
        self.__dragon.box.pack(grid, BoxedEffect.BLOCK)
        self.drawer.spriteBoxes.append(self.__dragon)    
    def update(self):
        
        self.__dragon.setEffect(SpriteEffect.EXPLODE, {}, 1000, self.drawer.animator.currentFrameTs )
        self.__dragon.setEffect(SpriteEffect.SHAKE, {}, 1000, self.drawer.animator.currentFrameTs )
        
        self.drawer.controller.twoAxisGridMove(self.__dragon)  
  

class TinyKombatGame:

    # BITMAP: width: 16, height: 25
    __stand_map = bytearray([0,240,248,156,252,156,248,240,0,0,0,0,0,0,0,0,24,60,125,120,97,48,25,88,32,56,24,0,0,0,0,0,0,0,143,255,113,7,254,120,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0]) 
    __block_map = bytearray([120,252,78,254,78,252,120,0,0,128,64,120,56,0,0,0,24,60,188,152,216,204,12,4,6,6,6,0,0,0,0,0,0,0,143,255,113,7,254,120,0,0,0,0,0,0,0,0,0,0,1,1,1,0,1,1,1,0,0,0,0,0,0,0]) 
    __punch_map = bytearray([0,0,240,248,156,252,156,248,240,0,0,0,0,0,0,0,24,60,124,121,64,97,104,13,28,24,24,8,8,28,28,8,128,248,63,7,3,63,248,192,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,0,0,0,0])
    __kick_map = bytearray([240,248,156,252,156,248,240,0,0,0,0,0,0,0,0,0,24,125,220,153,128,1,8,4,135,131,192,224,96,48,28,0,0,0,0,129,241,60,15,7,3,1,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0])
    __hero_map = __stand_map + __block_map + __punch_map + __kick_map
    
    class HeroFrame():
        STAND = 0
        BLOCK = 1
        PUNCH = 2
        KICK = 3


    def initGame(self):
        
        screen = self.drawer.screenBox #Box(Point(0, 0), Dimension(thumby.display.width, thumby.display.height))
        
        self.__sw = StopWatch(0, self.drawer.animator.currentFrameTs)
        
        self.__you = SpriteBox(self.__hero_map, Dimension(16, 25))
        self.__you.box.pack(screen, BoxedEffect.BLOCK)
        self.drawer.spriteBoxes.append(self.__you)    

        
    def update(self):
 
        self.drawer.controller.platformerJumper(self.__you)    
        
        if(self.__sw.isTimeout(self.drawer.animator.currentFrameTs)):
            
            if(thumby.buttonL.pressed()):
                self.__you.changeFrame(self.HeroFrame.BLOCK)        
            
            if(thumby.buttonA.justPressed()):
                self.__you.changeFrame(self.HeroFrame.KICK)
            
            if(self.drawer.controller.pressed(Button.DOWN | Button.A, Operator.AND)):
                self.__you.changeFrame(self.HeroFrame.PUNCH)            
            
            if(self.drawer.controller.pressed(Button.LEFT | Button.A, Operator.OR)):
                self.__sw.setTimeout(100, self.drawer.animator.currentFrameTs, lambda: self.__you.changeFrame(self.HeroFrame.STAND))    

            self.__sw.watch(self.drawer.animator.currentFrameTs)
       
