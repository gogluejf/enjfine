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
