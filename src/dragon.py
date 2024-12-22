import thumby
import math
import random
import sys


sys.path.insert(0, '/Games/enjfine')
import enjfine
import effects

class DragonDotsGame:
    
    
    title1 = "Dragon"
    title2 = "Game"

    game_map = bytearray([0,24,48,192,252,0,1,2,7,6,8,192,120,8,24,16,48,192,192,0,0,4,24,32,70,172,192,192,0,0,0,0,0,0,0,0,0,0,0,
           0,0,0,1,7,196,192,128,128,128,0,1,30,224,0,4,15,17,96,195,130,4,8,176,192,128,0,0,1,194,112,96,192,128,0,0,0,0,0,
           0,0,0,0,0,31,224,128,6,125,75,84,108,95,56,192,0,0,0,0,1,7,3,1,0,1,2,6,60,207,176,44,38,79,118,76,48,192,0,
           0,0,0,0,0,0,0,1,7,12,112,192,0,0,0,1,3,6,0,0,0,0,0,0,0,0,0,0,0,0,31,0,0,0,0,0,24,8,159,
           0,0,0,0,0,0,0,0,0,0,0,3,51,52,24,16,16,16,32,32,32,32,48,32,144,216,136,136,100,196,196,246,226,114,38,250,243,129,1])  


    __dragon_map = bytearray([0,0,0,0,0,0,252,252,96,96,224,224,224,0,0,0,192,192,240,240,63,63,63,63,254,254,255,255,243,243,51,51])

    # BITMAP: width: 16, height: 16
    __soldier_map = bytearray([0,0,0,68,36,20,8,28,162,162,42,28,0,0,0,0,0,0,0,224,96,96,114,55,31,255,244,132,14,2,2,6])

    def initGame(self):
        self.__dragon = enjfine.sprite.SpriteBox(self.__dragon_map, enjfine.Dimension(16,16))
        
        #box = enjfine.Grid(enjfine.Point(), self.__dragon.box.dim, 4, 2)
        box =  enjfine.Box()
        self.__dragon.box.pack(box, enjfine.animator.BoxedEffect.BLOCK)
        self.drawer.data.spriteBoxes.append(self.__dragon)    
            
    def update(self):
        
        #effect = effects.ExploseEffect(self.drawer, {"particles": 24})
        #effect.init(self.__dragon, 1000)

        #effect = effects.ShakeEffect(self.drawer, {})
        #effect.init(self.__dragon, 1000)

        self.drawer.controller.twoAxisFreeMove(self.__dragon, 80, 200)  
  
        return True
  

runner = enjfine.runner.GameRunner(DragonDotsGame())
runner.run()
          
