import thumby
import math
import random
import sys


sys.path.insert(0, '/Games/enjfine')
import enjfine
import effects


class PlatformerGame:
    
    title1 = "Tiny"
    title2 = "Skull"

    game_map = bytearray([0,0,0,0,0,0,192,48,24,12,6,2,130,131,129,65,65,65,65,65,193,129,129,1,2,2,2,4,4,76,200,136,16,16,48,32,96,192,0,
           0,0,0,0,248,14,3,96,0,32,0,0,15,56,96,128,152,120,248,120,48,16,1,129,130,108,56,120,204,134,226,227,227,30,240,0,0,129,254,
           0,0,0,0,31,48,64,64,130,0,0,24,0,0,128,0,0,1,1,1,0,1,65,112,76,120,0,124,88,112,65,1,1,1,1,128,192,127,112,
           0,0,0,0,0,0,0,0,0,1,193,58,14,0,0,0,0,192,0,0,0,0,0,0,0,0,128,192,0,0,8,252,52,6,3,1,0,0,0,
           0,0,0,0,0,0,0,128,240,156,131,128,146,136,128,0,128,143,252,48,64,126,6,60,32,48,31,7,12,24,60,55,0,0,0,0,0,0,0])  
    
    # BITMAP: width: 72, height: 30
    __bg_space_map = bytearray([0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,64,0,0,0,0,4,0,0,0,0,0,0,0,64,0,0,0,0,0,0,0,0,0,0,0,16,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,192,224,48,16,16,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,1,3,6,4,4,0,32,0,0,0,0,0,
           0,0,0,0,0,1,0,0,0,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,128,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0])

    # BITMAP: width: 5, height: 7 <- optimized ( just moon)
    #bg_far_map = bytearray([28,62,99,65,65])
    #self.__bgFar1 = enjfine.sprite.SpriteBox(bg_far_map, enjfine.Dimension(5,7), None,enjfine.Box(enjfine.Point(60,5),enjfine.Dimension(drawer.screenBox.dim.w, 30)))
    #self.__bgFar1.box.pack(drawer.screenBox, enjfine.animator.BoxedEffect.WRAP)
    #self.__bgFar2 = enjfine.sprite.SpriteBox(bg_far_map, enjfine.Dimension(5,7), None,enjfine.Box(enjfine.Point(60,5),enjfine.Dimension(drawer.screenBox.dim.w, 30)))
    #self.__bgFar2.box.pt.setPoint(drawer.screenBox.dim.w,0)
    #self.__bgFar2.box.pack(drawer.screenBox, enjfine.animator.BoxedEffect.WRAP)


    # BITMAP: width: 72, height: 10
    __bg_land_map = bytearray([0,0,0,0,0,0,0,0,128,64,32,16,8,4,2,84,168,80,160,64,128,0,0,0,0,0,0,0,0,0,0,128,64,32,64,128,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,112,64,248,64,96,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,1,0,0,0,0,0,0,0,1,2,1,2,1,2,1,2,0,0,0,0,0,0,2,1,0,0,0,1,2,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,2,1,2,0,0])


    __skull_map = bytearray([0,120,252,102,254,102,252,120,0,0,0,1,0,1,0,1,0,0])
    __skull_map_mask = bytearray([120,252,254,255,255,255,254,252,120,0,1,3,3,3,3,3,1,0])
    
    def initGame(self):
        
        screen = self.drawer.screenBox

        
        self.__skull = enjfine.sprite.SpriteBox(self.__skull_map, enjfine.Dimension(9, 10), self.__skull_map_mask,enjfine.Box(enjfine.Point(-1,-1), enjfine.Dimension(7,8)))
        self.__skull.box.pack( enjfine.Box(enjfine.Point(10,0), screen.dim - enjfine.Dimension(20,0)), enjfine.animator.BoxedEffect.BLOCK)
        self.drawer.data.spriteBoxes.append(self.__skull)   

        effect = effects.BackgroundEffect(self.drawer, {
            "map" : self.__bg_space_map,
            "map_dimension" : enjfine.Dimension(self.drawer.screenBox.dim.w, 30),
            "bg_box" : self.drawer.screenBox,
        })
        effect.init(self.__skull)


        effect = effects.BackgroundEffect(self.drawer, {
            "map" : self.__bg_land_map,
            "map_dimension" : enjfine.Dimension(self.drawer.screenBox.dim.w, 10),
            "offset_y" : 30,
            "bg_box" : self.drawer.screenBox,
            "layer" : 0,
        })
        effect.init(self.__skull)

    def update(self):
        
        self.drawer.controller.platformerJumper(self.__skull)    
            
        return True
            
            
runner = enjfine.runner.GameRunner(PlatformerGame())
runner.run()            
            
