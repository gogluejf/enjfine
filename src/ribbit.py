import thumby
import sys

sys.path.insert(0, '/Games/enjfine')

import enjfine
import effects

class RibbitGame:
    
    #__heart = bytearray([14,31,63,126,63,31,14]) #7x7
    #__death = bytearray([66,195,44,28,28,44,195,66]) #8x8

    title1 = "Tiny"
    title2 = "Ribbit"
    game_map = bytearray([0,128,96,48,24,204,180,108,148,108,148,232,216,240,224,224,192,192,192,192,224,240,56,28,142,70,6,6,230,134,6,6,4,12,24,48,224,192,128,
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

    __splash_map =  bytearray([0,0,0,8,20,20,20,20,8,0,0,0]) +  bytearray([0,0,8,20,34,34,34,34,20,8,0,0]) + bytearray([8,20,34,65,73,73,73,73,65,34,20,8])
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
            
        def __init__(self, nbGoals):
            self.nbGoals = nbGoals
            self.reset()
            
        def reset(self):
            self.__resetGoals()
            self.lifes = 5 #does are remaining lifes, so 0 is 1 life ( classic )
            self.level = 0 #level start at zero but display as starting at 1
        
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
        
        #current score
        def getScore(self):
            return self.level * self.nbGoals + len(self.hittedGoals)
            
        

    def __init__(self):
        self.__tile = enjfine.Dimension(7, 7) 
        self.__grid= enjfine.Grid(enjfine.Point(self.__griOffsetX,self.__griOffsetY), self.__tile, self.__cols, self.__rows)
        self.__state = self.State(round(self.__cols/2))
        

    def initGame(self):

        ### goals
        
        self.__sw = enjfine.animator.StopWatch(0, self.drawer.animator.currentFrameTs)
       
        self.__state.reset()
       
        for i in range(self.__state.nbGoals):
            rect = enjfine.rectangle.RectangleBox(enjfine.Dimension(self.__tile.w, self.__tile.h-1))
            rect.box.pt = self.__grid.getPointFromGridCoordinate(enjfine.GridCoordinate(i*2,0))
            self.drawer.data.rectBoxes.append(rect)   

        self.__frog = enjfine.sprite.SpriteBox(self.__frog_map, enjfine.Dimension(self.__tile.w+2,self.__tile.h+2), self.__frog_mask_map, enjfine.Box(enjfine.Point(-1,-1),self.__tile), 2)
        self.__frog.id = "frog"
        self.__frog.box.pack(self.__grid, enjfine.animator.BoxedEffect.BLOCK)
        self.drawer.data.spriteBoxes.append(self.__frog)      

        self.__initLanes()

        self.__splash = enjfine.sprite.SpriteBox(self.__splash_map, enjfine.Dimension(12,7), None, None, 3)
        self.__splash.id = "splash"
        self.__splash.Invert()
        self.__splash.setAnimate(7)
  
        self.__startLife()
    
    def __startLife(self):

        if(self.__state.isGameOver()):
            return

        level = enjfine.text.TextBox(enjfine.text.Text("level {0}".format(self.__state.level+1)))
        lifes = enjfine.text.TextBox(enjfine.text.Text("x {0}".format(self.__state.lifes)))
        box = enjfine.Box(enjfine.Point(), enjfine.Dimension(self.__frog.box.dim.w + 6 + lifes.box.dim.w,8*3))
        
        box.pt = self.__grid.getDimensionPosition(box.dim, enjfine.Position.CENTER, enjfine.VPosition.MIDDLE)
        level.box.pt = box.getDimensionPosition(level.box.dim, enjfine.Position.CENTER, enjfine.VPosition.TOP)
        lifes.box.pt = box.getDimensionPosition(lifes.box.dim, enjfine.Position.RIGHT, enjfine.VPosition.BOTTOM)
        
        self.__resetFrogPosition()
        self.__frog.box.pt = box.getDimensionPosition(lifes.box.dim, enjfine.Position.LEFT, enjfine.VPosition.BOTTOM)

        vOffset = enjfine.Vector(0,0)
    
        self.drawer.animator.fadeBlocking(enjfine.animator.Fade.OUT, 500)
        self.drawer.animator.emptyScreen()
        self.drawer.textDrawer.draw(level, vOffset)
        self.drawer.spriteDrawer.draw(self.__frog, vOffset)
        self.drawer.textDrawer.draw(lifes, vOffset)
        self.drawer.animator.fadeBlocking(enjfine.animator.Fade.IN, 25)
        self.drawer.animator.wait(1500)
        self.drawer.animator.fadeBlocking(enjfine.animator.Fade.OUT, 500)
        self.__resetFrogPosition()
        self.drawer.animator.initFrame()
        self.drawer.update()
        self.drawer.animator.fadeBlocking(enjfine.animator.Fade.IN, 25)
        self.drawer.animator.unpause()


        """        
        while(1):
        
        drawer.animator.initFrame()
        
        if drawer.controller.justPressed(controller.Button.A | controller.Button.B):

            drawer.animator.move(img.box, velocity.copy(), 250)
            drawer.animator.move(title.box, velocity * -1, 250)
            sw = drawer.animator.move(title2.box, velocity * -1, 250)
        
        if(sw is not None and sw.isTimeout(drawer.animator.currentFrameTs)):
            break
            
        drawer.update()
        """



    
    def __resetFrogPosition(self):
        self.__frog.box.pt = self.__grid.getPointFromGridCoordinate(enjfine.GridCoordinate(round(self.__cols/2), len(self.__lanes)-1))
        self.__frog.sprite.mirrorX=0
        self.__frog.sprite.mirrorY=0
        self.__frog.changeFrame(0)
        self.__frog.Revert()
    
    def __initLanes(self):
        
        for i in range(1,5):
            self.drawer.data.removeById("lane_{0}".format(i))
    
        self.__lanes = [self.LaneType.GOAL]
       
        level = (self.__state.level % 8) + 1
        speed = 1 + (self.__state.level // 8) * 0.20 # increasing speed at level 9
       
        if(level == 1):
            self.__initLakeItemsLane(10*speed, [    {"lakeItem" : self.LakeItem.TURTLE2, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  8}])
            self.__initLakeItemsLane(-10*speed, [   {"lakeItem" : self.LakeItem.LOG1, "col" :  1},
                                                    {"lakeItem" : self.LakeItem.LOG2, "col" :  8}])
            self.__initVehiculesLane(-20*speed, [   {"vehicule" : self.Vehicule.CAR1, "col" :  0},
                                                    {"vehicule" : self.Vehicule.TRUCK, "col" :  5}])
            self.__initVehiculesLane(20*speed, [    {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR1, "col" :  6}])
 
        if(level == 2):
            self.__initLakeItemsLane(10*speed, [    {"lakeItem" : self.LakeItem.TURTLE2, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  9}])
            self.__initLakeItemsLane(20*speed, [    {"lakeItem" : self.LakeItem.LOG1, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.LOG2, "col" :  7}])
            self.__initLakeItemsLane(-10*speed, [   {"lakeItem" : self.LakeItem.TURTLE1, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  9}])
            self.__initLakeItemsLane(20*speed, [    {"lakeItem" : self.LakeItem.TURTLE3, "col" :  0}])

        if(level== 3):
            self.__initLakeItemsLane(10*speed, [    {"lakeItem" : self.LakeItem.LOG1, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.LOG1, "col" :  9}])
            self.__initLakeItemsLane(30*speed, [    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  3},
                                                    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  6},
                                                    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  9}])
            self.__initVehiculesLane(60*speed, [    {"vehicule" : self.Vehicule.TRUCK, "col" :  0}])
            self.__initLakeItemsLane(-10*speed, [   {"lakeItem" : self.LakeItem.TURTLE1, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  9}])
            
        if(level== 4):
            self.__initVehiculesLane(-25*speed, [   {"vehicule" : self.Vehicule.CAR1, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR1, "col" :  5}])
            self.__initVehiculesLane(-30*speed, [   {"vehicule" : self.Vehicule.CAR1, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR1, "col" :  6}])
            self.__initVehiculesLane(-15*speed, [   {"vehicule" : self.Vehicule.CAR1, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR1, "col" :  5}])
            self.__initVehiculesLane(-10*speed, [   {"vehicule" : self.Vehicule.CAR1, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR1, "col" :  6}])
            
        if(level == 5):
            self.__initLakeItemsLane(-20*speed, [   {"lakeItem" : self.LakeItem.LOG1, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.LOG1, "col" :  4},
                                                    {"lakeItem" : self.LakeItem.LOG2, "col" :  8}])
            self.__initVehiculesLane(30*speed, [    {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR2, "col" :  6}])
            self.__initLakeItemsLane(-30*speed, [   {"lakeItem" : self.LakeItem.LOG2, "col" :  0},
                                                    {"lakeItem" : self.LakeItem.LOG2, "col" :  7}])
            self.__initVehiculesLane(25*speed, [    {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR2, "col" :  4}])                                          
 
        if(level == 6):
            self.__initVehiculesLane(0, [])
            self.__initVehiculesLane(-100*speed, [  {"vehicule" : self.Vehicule.TRUCK, "col" :  0}])
            self.__initVehiculesLane(70*speed, [    {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR1, "col" :  7}])
            self.__initVehiculesLane(0, [])         
 
        
        if(level == 7):
            self.__initLakeItemsLane(45*speed, [    {"lakeItem" : self.LakeItem.TURTLE2, "col" :  0}])
            self.__initLakeItemsLane(10*speed, [    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  2}])
            self.__initLakeItemsLane(-45*speed, [   {"lakeItem" : self.LakeItem.TURTLE2, "col" :  0}])
            self.__initLakeItemsLane(10*speed, [    {"lakeItem" : self.LakeItem.TURTLE1, "col" :  0}])
 
 
        if(level == 8):
            self.__initVehiculesLane(60*speed, [    {"vehicule" : self.Vehicule.TRUCK, "col" :  0}])
            self.__initVehiculesLane(25*speed, [    {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR2, "col" :  3},
                                                    {"vehicule" : self.Vehicule.CAR2, "col" :  6}])    
            self.__initVehiculesLane(-20*speed, [   {"vehicule" : self.Vehicule.CAR1, "col" :  0},
                                                    {"vehicule" : self.Vehicule.TRUCK, "col" :  5}])
            self.__initVehiculesLane(20*speed, [    {"vehicule" : self.Vehicule.CAR2, "col" :  0},
                                                    {"vehicule" : self.Vehicule.CAR1, "col" :  6}]) 
        
        #our hero
        self.__lanes.append(self.LaneType.START)
    
        #put back frog on top
        self.drawer.data.spriteBoxes.remove(self.__frog)  
        self.drawer.data.spriteBoxes.append(self.__frog)  
    
    
    def __initLakeItemsLane(self, speed, lakeItems):
        for lakeItem in lakeItems: self.__initLakeItem(lakeItem.get("lakeItem"), speed, lakeItem.get("col"))

        row = len(self.__lanes)
        
        rect = enjfine.rectangle.RectangleBox(enjfine.Dimension(self.__grid.dim.w, self.__tile.h))
        rect.id = "lane_{0}".format(row)
        rect.box.pt = self.__grid.getPointFromGridCoordinate(enjfine.GridCoordinate(0,row))
        self.drawer.data.rectBoxes.append(rect)  
        
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

        velocity = enjfine.Vector(speed,0)
        lakeItem = enjfine.sprite.SpriteBox(bitmap, enjfine.Dimension(width, self.__tile.h))
        if speed < 0:
            lakeItem.sprite.mirrorX = 1
        
        lakeItem.id = "lane_{0}".format(row)
        lakeItem.box.pt = self.__grid.getPointFromGridCoordinate(enjfine.GridCoordinate(col, row))
        lakeItem.box.pt.velocityGoal = velocity
        lakeItem.box.pt.velocity = velocity
        lakeItem.Invert()
        
        lakeItem.box.pack(self.__grid, enjfine.animator.BoxedEffect.WRAP, {"wrap_item_w" : 44})
        self.drawer.data.spriteBoxes.append(lakeItem) 

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
        
        velocity = enjfine.Vector(speed,0)
        vehicule = enjfine.sprite.SpriteBox(bitmap, enjfine.Dimension(width, self.__tile.h))
        if speed < 0:
            vehicule.sprite.mirrorX = 1

        vehicule.id = "lane_{0}".format(row)
        vehicule.box.pt = self.__grid.getPointFromGridCoordinate(enjfine.GridCoordinate(col, row))
        vehicule.box.pt.velocityGoal = velocity
        vehicule.box.pt.velocity = velocity

        vehicule.box.pack(self.__grid, enjfine.animator.BoxedEffect.WRAP, {"wrap_item_w" : 26})
        self.drawer.data.spriteBoxes.append(vehicule) 

    def update(self):

        if self.drawer.controller.twoAxisGridMove(self.__frog) :
        
            coord = self.__grid.getGridCoordinateFromPosition(self.__frog.box.pt)
            lane = round(coord.row)
            
            if self.__lanes[lane] == self.LaneType.LAKE:
                self.__frog.Invert()
            else:
                self.__frog.Revert()

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

        if not self.__frog.hide:
            coord = self.__grid.getGridCoordinateFromPosition(self.__frog.box.pt)
            lane = round(coord.row)
            
            collides = self.drawer.animator.detectCollision(self.__frog, self.drawer.data.spriteBoxes, "lane_{0}".format(lane))
 
            collide_goal = self.__lanes[lane] == self.LaneType.GOAL and (not coord.col % 2 or self.__state.isGoalHitted(coord.col // 2))
            sink_lake = self.__lanes[lane] == self.LaneType.LAKE and not len(collides)
            collide_vehicule = self.__lanes[lane] == self.LaneType.ROAD and len(collides)
    
            #if in lake,hitting a vehicule or missing goal, then we loose a life
            if (collide_goal or sink_lake  or collide_vehicule):
                
                if(self.__lanes[lane] == self.LaneType.ROAD):
                    effect = effects.SplashEffect(self.drawer, {"particles" : 24, "velocity": collides[0].box.pt.velocity})
                    effect.init(self.__frog, self.__deathAnimationMs)
                if(self.__lanes[lane] == self.LaneType.LAKE):
                    self.__splash.box.pt = self.__frog.box.pt
                    self.drawer.data.spriteBoxes.append(self.__splash)
                    def removeSplash():
                        self.drawer.data.spriteBoxes.remove(self.__splash)
                    self.drawer.animator.delay(self.__deathAnimationMs, removeSplash)
                    
                effect = effects.HideEffect(self.drawer)
                effect.init(self.__frog, self.__deathAnimationMs)    
                    
                self.drawer.animator.pause()
    
                for target in collides:
                    effect = effects.ShakeEffect(self.drawer)
                    effect.init(target, 1000)    
    
    
                def die():
                    self.__state.looseLife()
                    self.drawer.update()
                    self.__startLife()
    
                self.__sw.setTimeout(self.__deathAnimationMs-500, self.drawer.animator.currentFrameTs, die)    
                #self.drawer.animator.delay(self.__deathAnimationMs-500, die)
            
            elif (self.__lanes[lane] == self.LaneType.LAKE):
                #make the frog drift with the log and turles, sync it with first item on the lane
                self.__frog.box.pt.velocityGoal = collides[0].box.pt.velocityGoal
                self.__frog.box.pt.velocity = collides[0].box.pt.velocity
    
            #ok, no sink, no collision, if we are on goal lane, we scored
            elif(self.__lanes[lane] == self.LaneType.GOAL):
                self.__state.hitGoal(coord.col // 2)
                bl = enjfine.blit.BlitBox(self.__goal_map, enjfine.Dimension(7, 7))
                bl.box.pt = self.__grid.getPointFromGridCoordinate(enjfine.GridCoordinate(coord.col, 0)) 
                self.drawer.data.blitBoxes.append(bl)
                
                #passing a level
                if(self.__state.isLevelClear()):
                    
                    effect = effects.HideEffect(self.drawer)
                    effect.init(self.__frog, 500)  
                
                    self.__state.nextLevel()
                    self.drawer.update()
                    self.drawer.data.blitBoxes = []
                    self.__initLanes()
                    self.__startLife()
                
                self.__resetFrogPosition()

            if(self.drawer.controller.pressed(enjfine.controller.Button.A | enjfine.controller.Button.B, enjfine.controller.Operator.AND)):
                self.__state.nextLevel()
                self.drawer.update()
                self.drawer.data.blitBoxes = []
                self.__initLanes()
                self.__startLife()
        
        self.__sw.watch(self.drawer.animator)
        
        return not self.__state.isGameOver()
        
        

#turtle sink    
#improve death frog 
    #goals collision shake everything

#fixall loop
    ##gameover, #startlife

#sin, cos intro
#operation menu
        #help
        #endless
        #regulare
        #score
        
        

#add level 2 animation         
#score
    #add title animation

#endless mode

#effect on boxes ?
    #shake other than just sprite ?
#smooth mouvement
#fix justPressed blocking
#shake only on x axes ? (intro animation)


runner = enjfine.runner.GameRunner(RibbitGame())
runner.run()
        
        
        
