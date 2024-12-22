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
        txt = TextBox(Text("{0} {1}".format(self.__score[self.Team.YOU], self.__score[self.Team.CPU])))
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
            player.Invert()
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
