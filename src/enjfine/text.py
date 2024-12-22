import thumby
import enjfine


class FontSize():
    SMALL = 0
    BIG = 1

class TextBG():
    TRANSPARENT=-1
    INVERT=0
    INVERT_FULL_LINE=1

# a box containing some text, useful to apply effects on text
class TextBox(enjfine.BoxObj):

    # Text Object to contain in the box
    #max_chars: the box size will match this is the maximun character can be display in the box, if max_chars=0, the maximum chars will be equal to the text size
    def __init__(self, text, max_chars = 0):
        super().__init__()
        self.text= text
        self.max_chars = self.text.getTextLength() if max_chars == 0 else max_chars
        self.box = enjfine.Box(enjfine.Point(), enjfine.Dimension(self.text.getFontWidth(True)*self.max_chars, self.text.getFontHeight()))
        
    #return the text string visibile ( either full text or the first part of text up to max_chars)
    def getVisibileText(self):
        return self.text.text[0:self.max_chars] if self.text.getTextLength()>self.max_chars else self.text.text

    #get the size of the visible text
    def getVisibleTextSizeWidth(self):
        return self.text.getFontWidth(True)*len(self.getVisibileText())
        
    #get absolute x screen position of the text 
    def getTextXFromPos(self):    

        if self.text.pos == enjfine.Position.LEFT: x=self.box.pt.x
        if self.text.pos == enjfine.Position.CENTER: x=self.box.pt.x + round(self.box.dim.w/2-self.getVisibleTextSizeWidth()/2)
        if self.text.pos == enjfine.Position.RIGHT: x=self.box.pt.x + self.box.dim.w-self.getVisibleTextSizeWidth()
        return x                
        
#transport layer for drawing rectangle
class Text:
    
    space=1
    __font_h=8
    
    def __init__(self,text, pos=enjfine.Position.CENTER, color= enjfine.Color.WHITE, bg=TextBG.TRANSPARENT, fontSize=FontSize.SMALL):
        self.text = text
        self.pos = pos
        self.color = color
        self.bg = bg
        self.fontSize = fontSize

    #get font width ( not including space)
    #withSpace True=include space width, False= only character width
    def getFontWidth(self, withSpace=False):
        w = 8 if self.fontSize == FontSize.BIG else 5
        if withSpace:
            w=w+self.space
        return w

    #get font heigh
    def getFontHeight(self):
        return self.__font_h

    #return the number of character to display
    def getTextLength(self):
        return len(self.text)

    #return the text width size to display in pixel. This include the spacing after the last character
    def getTextSizeWidth(self):
        return self.getFontWidth(True)*self.getTextLength()

#helper to draw text and numbers
class TextDrawer:

    #todo scroll smooth ( lines )
    #scroll ( box )
    #draw multilines
    #wordwrap
    #multiline controls
        
    #effect
        #character typing

    # BITMAP: width: 40, height: 6 tiny #numbers
    numbers_map = bytearray([62,34,62,0,36,62,32,0,50,42,38,0,34,42,54,0,14,8,62,0,46,42,18,0,62,42,58,0,50,10,6,0,62,42,62,0,14,10,62,0])
    __currentFont=0 #identification of font size and space

    #write text at a specic line on the screen ( each line is 8px to fit big or small font)
    #text object to draw
    #line: 1 to 5
    def drawLine(self, text, line=0):

        textBox = TextBox(text)
        textBox.box.pt.setPoint(0, (line-1)*text.getFontHeight())
        textBox.box.dim.w = thumby.display.width
        
        self.draw(textBox)

    #textBox: TextBox containing the text to draw 
    #big: 1=big, 0=small
    #rectangle obj to display bg
    def draw(self, textBox, vOffset):

        

        self.__drawTextBackgroundRectangle(textBox, vOffset)           
        self.__loadFont(textBox.text)

        pt = enjfine.Point(textBox.getTextXFromPos(), textBox.box.pt.y)
        if(textBox.applyOffset): #shake effects43
            pt += vOffset

        thumby.display.drawText(textBox.getVisibileText(), int(pt.x), int(pt.y), textBox.text.color)

    #load the font
    #since loading font is a slow function, only load when text size change
    def __loadFont(self, text):

        font= str(text.fontSize) + "-" + str(text.space)
        if(font != self.__currentFont):
            thumby.display.setFont("/lib/font8x8.bin" if text.fontSize == FontSize.BIG else "/lib/font5x7.bin",  text.getFontWidth(), text.getFontHeight(), text.space)
            self.__currentFont=font
    
    #get the background for the text
    #text_obj: text object
    #return rectangle object
    def __drawTextBackgroundRectangle(self, textBox, vOffset):
        
        padding=0

        if textBox.text.bg != TextBG.TRANSPARENT:
            if textBox.text.bg == TextBG.INVERT:
                rect_x = textBox.getTextXFromPos()
                rect_w = textBox.getVisibleTextSizeWidth()
                if rect_w>thumby.display.width-textBox.getTextXFromPos():
                    rect_w = thumby.display.width-textBox.getTextXFromPos()
            else: #TextBG.INVERT_FULL_LINE
                rect_x = textBox.box.pt.x
                rect_w = textBox.box.dim.w

            pt = enjfine.Point(rect_x, textBox.box.pt.y-padding)
            if(textBox.applyOffset): #shake effects43
                pt += vOffset

            thumby.display.drawFilledRectangle(pt.x, pt.y, rect_w+(padding*2), textBox.text.getFontHeight()+(padding*2), (textBox.text.color+1)%2)

        
