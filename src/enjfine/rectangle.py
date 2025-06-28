import thumby
import enjfine

class RectangleMode():
    OUTLINE = 0 #draw boundary of the box
    FILLED = 1 #draw a filled box 

class RectangleBox(enjfine.BoxObj):

    def __init__(self, dim, mode = RectangleMode.FILLED, color = enjfine.Color.WHITE):
        super().__init__()
        self.box = enjfine.Box(enjfine.Point(), dim)
        self.mode = mode
        self.color = color
        
        
class RectangleDrawer:

    def draw(self, rectBox, vOffset):
        
        pt = rectBox.box.pt
        if(rectBox.applyOffset): #shake effects
            pt += vOffset
        
        if(rectBox.mode == RectangleMode.FILLED):
            thumby.display.drawFilledRectangle(round(pt.x), round(pt.y), rectBox.box.dim.w, rectBox.box.dim.h, rectBox.color)
        if(rectBox.mode == RectangleMode.OUTLINE):
            thumby.display.drawRectangle(round(pt.x), round(pt.y), rectBox.box.dim.w, rectBox.box.dim.h, rectBox.color)        
