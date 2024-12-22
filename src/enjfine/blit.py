import thumby
import enjfine

class BlitBox(enjfine.BoxObj):
    
    #bitmap to load in sprite
    #dim : the bitmap dimension
    def __init__(self, bitmap, dim, mirrorX = 0, mirrorY = 0):
        super().__init__()
         
        self.box = enjfine.Box(enjfine.Point(), dim)
        self.bitmap = bitmap
        self.mirrorX = mirrorX
        self.mirrorY = mirrorY
        
        
class BlitDrawer:
    
    def draw(self, blitBox, vOffset):
        
        pt = blitBox.box.pt
        if(blitBox.applyOffset): #shake effects43
            pt += vOffset
        
        thumby.display.blit(blitBox.bitmap, round(pt.x), round(pt.y), blitBox.box.dim.w, blitBox.box.dim.h, 0, blitBox.mirrorX, blitBox.mirrorY)

    
