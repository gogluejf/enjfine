




    
 



"""
devil_map = bytearray([0,102,217,204,124,204,217,102])
devilSpBox = SpriteBox(devil_map, Dimension(8, 8))
devilSpBox.box.pt.setPoint(64,8)
devilSpBox.box.pack(drawer.screenBox, BoxedEffect.WRAP)
#devilSpBox.box.pt.velocityGoal.x=50
#devilSpBox.box.pt.velocityGoal.y=10
#drawer.spriteBoxes.append(devilSpBox)


#old fields for gravity
ts_init = time.ticks_ms()
position = -skullSpBox.box.dim.h
velocity = 0
pt=Point(0,0)
"""









#charger
rectBox = RectangleBox(Dimension(0, 2))
rectBox.box.pt = drawer.screenBox.getDimensionPosition(rectBox.box.dim, Position.LEFT, VPosition.BOTTOM)
rectBox.box.pack(drawer.screenBox)
drawer.rectBoxes.append(rectBox)
#rectBox.box.dim.initPoint()

pt = Point(0,0) #rectBox.box.dim.pt
pt.vAcceleration.x = 250
pt.velocityGoal.x = 200


#wave
#self._d = 0
#self.__devil.box.pt.x = self.__anchorPt.x



while(1):
    
    drawer.animator.initFrame()
    
    #onTimeout
    #collision engine fix
    #move to position

    #charger
    if(thumby.buttonA.pressed()):
        #pt.velocityGoal.x = 50
        drawer.animator.updatePoint(pt)
        if(pt.x > rectBox.box.parent.dim.w):
            pt.x = rectBox.box.parent.dim.w
        rectBox.box.dim.w = round(pt.x)
    else:
        #pt.velocityGoal.x = 0
        pt.velocity.x = 0
        pt.x = 0
        rectBox.box.dim.w = 0


	#text shaking center screen
        textbox = enjfine.text.TextBox(enjfine.text.Text("Warning"), 8)
        textbox.box.pt = self.__drawer.screenBox.getDimensionPosition(textbox.box.dim, enjfine.Position.CENTER, enjfine.VPosition.MIDDLE)
        textbox.text.bg = enjfine.text.TextBg.INVERT_FULL_LINE
        textbox.text.color = enjfine.Color.BLACK
        effect = effects.ShakeEffect(self.__drawer)
        effect.init(textbox)
        self.__drawer.data.textBoxes.append(textbox)


	#wave
	self._d += math.radians(360 * self.drawer.animator.previousFrameDeltaSec)
	self.__devil.box.pt.y = self.__anchorPt.y + math.sin(self._d) * 5	


	#target line
	v = (self.__pill.box.getCenterPoint() - self.__ship.box.getCenterPoint()).normalized()
	pt1 = self.__ship.box.getCenterPoint() + (v * 12)
	pt2 = pt1 + (v * 6)
	thumby.display.drawLine(round(pt1.x), round(pt1.y), round(pt2.x), round(pt2.y), enjfine.Color.WHITE)







    #wrap scrolling engine ( support y scrolling ? )
    #scroll Y 
    
    #scroll grid
    #break boxedEffect for x/y
    #mirror and wrap into grid system
    
    #text examples
    #drawer.text_drawer.drawLine("dragon dots",3,0,0)
    #textBox = drawer.text_drawer.drawLine(Text("Game Over",0),1)
    #drawer.text_drawer.drawLine(Text("Play again?", 0),3)
    #text_option = Text("B:YES A:NO",0,0,1)
    #drawer.animator.flashText(text_option)
    #drawer.text_drawer.drawLine(text_option,5)



    """
    


    #if(thumby.buttonB.justPressed()):
        ts= time.ticks_ms()
        vector = skullSpBox.box.getCenterPoint() - devilSpBox.box.getCenterPoint()

        print("skull {0}".format(skullSpBox.box.getCenterPoint()))
        print("skull {0}".format(devilSpBox.box.getCenterPoint()))
        print("press {0}".format(vector) )
        
        devilSpBox.box.pt.velocity = vector 
        devilSpBox.box.pt.vAcceleration = vector.absolute() / 2
    
    if devilSpBox.box.pt.velocity.x != 0 and time.ticks_ms() - ts > 2000:
        print(devilSpBox.box.pt)
        print(time.ticks_ms() - ts)
    """




    #walkign dragon
    #offset = math.sin(t / 50) * 1
    #dragonSprite.y = round(thumby.display.height/2 - (dragonSprite.width/2) + offset)
    #dragonSprite.x = dragonSprite.width * -1 if  dragonSprite.x>=(thumby.display.width+dragonSprite.width) else dragonSprite.x + 1

    # gravity
    #t= time.ticks_ms()
    #ts = (t-ts_init) / 1000
    #forces = 9.8 #// 9.8m/s/s on earth
    #mass = 300
    #acceleration = forces / mass
    #velocity = velocity + (acceleration * ts)
    #position =  position + round(velocity * ts)
    #skullSprite.y = position
    #if(skullSprite.y>=thumby.display.height+skullSprite.height):
    #    ts_init = time.ticks_ms()
    #    position = -skullSprite.height
    #    velocity = 0


    game.update()
    


