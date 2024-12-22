import thumby
import enjfine

class Operator():
    AND = 0
    OR = 1

class Button:
    UP = 1
    DOWN = 1 << 1
    LEFT = 1 << 2
    RIGHT = 1 << 3
    A = 1 << 4
    B = 1 << 5

class Axis:
    X = 1
    Y = 1 << 1
    

class Controller():

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
            if(thumby.buttonL.pressed()): pressed |= Button.LEFT
            if(thumby.buttonR.pressed()): pressed |= Button.RIGHT            
            if(thumby.buttonU.pressed()): pressed |= Button.UP            
            if(thumby.buttonD.pressed()): pressed |= Button.DOWN
            if(thumby.buttonA.pressed()): pressed |= Button.A
            if(thumby.buttonB.pressed()): pressed |= Button.B
            
            if(pressed & buttons == buttons):
                return True
    
        return False
        
    #multtiple buttons detection
    #buttons: bitfield of Button.*
    def justPressed(self, buttons, operator = Operator.OR):
        
        if(operator == Operator.OR and (buttons & Button.LEFT and thumby.buttonL.justPressed() or buttons & Button.RIGHT and thumby.buttonR.justPressed() or buttons & Button.UP and thumby.buttonU.justPressed() or buttons & Button.DOWN and thumby.buttonD.justPressed() or buttons & Button.A and thumby.buttonA.justPressed() or buttons & Button.B and thumby.buttonB.justPressed())):
            return True
        
        if(operator == Operator.AND):
            
            justPressed= 0
            if(thumby.buttonL.justPressed()): justPressed |= Button.LEFT
            if(thumby.buttonR.justPressed()): justPressed |= Button.RIGHT
            if(thumby.buttonU.justPressed()): justPressed |= Button.UP            
            if(thumby.buttonD.justPressed()): justPressed |= Button.DOWN
            if(thumby.buttonA.justPressed()): justPressed |= Button.A
            if(thumby.buttonB.justPressed()): justPressed |= Button.B
            
            if(justPressed & buttons == buttons):
                return True;
    
        return False
    
    
    def twoAxisFreeMove(self, spriteBox, speed=50, acceleration=40):
        
        box = spriteBox.box
        sprite = spriteBox.sprite
        pt = box.pt
        
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
        if(thumby.buttonU.pressed()): pt.velocityGoal.y=-speed
        if(thumby.buttonD.pressed()): pt.velocityGoal.y=speed
    
    
    #move on a single axe, 
    #pushing button move to a direction, #releasing stop the sprite, #pushing again will move to the other direction
    def OneAxisOneButtonMove(self, spriteBox, speed = 60, acceleration = 300, axis = Axis.Y, buttons = Button.LEFT | Button.RIGHT | Button.UP | Button.DOWN):

        pt = spriteBox.box.pt
        if(self.pressed(buttons)):
            if(hasattr(spriteBox, "resetAxisDirection") and spriteBox.resetAxisDirection):
                spriteBox.resetAxisDirection = False
                spriteBox.axisDirection = 1 if(not hasattr(spriteBox, "axisDirection") or spriteBox.axisDirection == -1) else -1 # we don't allow more than one rotation on a box at a time
                
                if(axis == Axis.X):
                    pt.velocityGoal.x = speed * spriteBox.axisDirection
                    pt.vAcceleration.x = acceleration
                if(axis == Axis.Y):
                    pt.velocityGoal.y = speed * spriteBox.axisDirection
                    pt.vAcceleration.y = acceleration

        else:
            spriteBox.resetAxisDirection = True
            if(axis == Axis.X): pt.velocityGoal.x = 0
            if(axis == Axis.Y): pt.velocityGoal.y = 0
    
    #return true if a button has been pushed
    def twoAxisGridMove(self, spriteBox):
    
        #push with delay
        #smooth transition
    
        x=0
        y=0
    
        if(thumby.buttonL.justPressed()):   x = -1
        if(thumby.buttonR.justPressed()):   x = 1
        if(thumby.buttonU.justPressed()):   y = -1
        if(thumby.buttonD.justPressed()):   y = 1

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
        
        
