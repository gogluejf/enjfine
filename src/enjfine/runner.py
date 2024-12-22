import thumby
import enjfine

import controller
import animator
import text
import blit

#take a game and run it
#each game need to implement "initGame" and "update" function
#each game have access to "drawer"
class GameRunner:
        
    def __init__(self, game):
        self.__game = game
        self.__game.drawer = enjfine.Drawer()

    def run(self):
        while(1):
            self.__game.drawer.animator.initFrame()
            self.__title()
            self.__init()
            self.__play()
    
    def __title(self):
        
        drawer = self.__game.drawer

        box = drawer.screenBox
        boxTitle = enjfine.Box(enjfine.Point(), enjfine.Dimension(drawer.screenBox.dim.w, 8*2 + 4))
        boxTitle.pt = box.getDimensionPosition(boxTitle.dim, enjfine.Position.LEFT, enjfine.VPosition.BOTTOM)
  
        present = text.TextBox(text.Text("JF Present"))
        present.box.pt = box.getDimensionPosition(present.box.dim, enjfine.Position.CENTER, enjfine.VPosition.MIDDLE)
        
        velocity = enjfine.Vector(50, 0)

        img = blit.BlitBox(self.__game.game_map, enjfine.Dimension(39, 40))
        img.box.pt = box.getDimensionPosition(img.box.dim, enjfine.Position.RIGHT_OUTER, enjfine.VPosition.MIDDLE)
        
        title = text.TextBox(text.Text(self.__game.title1))
        title2 = text.TextBox(text.Text(self.__game.title2))
        title.box.pt = boxTitle.getDimensionPosition(title.box.dim, enjfine.Position.LEFT_OUTER, enjfine.VPosition.TOP)
        title2.box.pt = boxTitle.getDimensionPosition(title2.box.dim, enjfine.Position.LEFT_OUTER, enjfine.VPosition.BOTTOM)
        
        def showPresent():
            drawer.data.textBoxes.append(present) 
            drawer.animator.fade(animator.Fade.IN, 1500, lambda: 
                drawer.animator.delay(750, lambda: 
                    drawer.animator.fade(animator.Fade.OUT, 1500,  lambda: drawer.animator.delay(500, lambda: (
                        drawer.data.textBoxes.remove(present),
                        drawer.animator.fade(animator.Fade.IN),
                        showGameTitle())))))
        
        def showGameTitle():
            drawer.data.blitBoxes.append(img)
            drawer.data.textBoxes.append(title) 
            drawer.data.textBoxes.append(title2)   

            drawer.animator.move(img.box, enjfine.Vector(-1 * img.box.dim.w, 0), 250)
            drawer.animator.move(title.box, enjfine.Vector(title.box.dim.w, 0), 250)
            drawer.animator.move(title2.box, enjfine.Vector(title2.box.dim.w, 0), 250)
      
        showPresent()    

        sw = None
        while(1):
            
            drawer.animator.initFrame()
            
            if drawer.controller.justPressed(controller.Button.A | controller.Button.B):
    
                drawer.animator.move(img.box, enjfine.Vector(img.box.dim.w, 0), 250)
                drawer.animator.move(title.box, enjfine.Vector(-1 * title.box.dim.w, 0), 250)
                sw = drawer.animator.move(title2.box, enjfine.Vector(-1 * title2.box.dim.w, 0), 250)
            
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
        
        drawer.animator.fadeBlocking(animator.Fade.OUT, 1)
        drawer.animator.emptyScreen()

        gameover = text.TextBox(text.Text("Game Over"))
        again = text.TextBox(text.Text("Play Again?"))
        options = text.TextBox(text.Text("B:YES A:NO"))
        
        box = enjfine.Box(enjfine.Point(), enjfine.Dimension(drawer.screenBox.dim.w, 8*3 +4 +4))
        box.pt = drawer.screenBox.getDimensionPosition(box.dim, enjfine.Position.CENTER, enjfine.VPosition.MIDDLE)
        gameover.box.pt = box.getDimensionPosition(gameover.box.dim, enjfine.Position.CENTER, enjfine.VPosition.TOP)
        again.box.pt = box.getDimensionPosition(again.box.dim, enjfine.Position.CENTER, enjfine.VPosition.MIDDLE)
        options.box.pt = box.getDimensionPosition(options.box.dim, enjfine.Position.CENTER, enjfine.VPosition.BOTTOM)
        
        vOffset = enjfine.Vector(0,0)
        
        drawer.textDrawer.draw(gameover, vOffset)
        drawer.textDrawer.draw(again,  vOffset)
        drawer.textDrawer.draw(options, vOffset)
        
        drawer.animator.fadeBlocking(animator.Fade.IN, 1)

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
            
            if drawer.controller.pressed(controller.Button.LEFT | controller.Button.DOWN | controller.Button.A | controller.Button.B, controller.Operator.AND):
                self.__init()
                
            if(not self.__game.update()):
                if(self.__gameOver()):
                    self.__init()
                else:
                    drawer.animator.fadeBlocking(animator.Fade.OUT, 1500)
                    drawer.reset()
                    break

            drawer.update()   
