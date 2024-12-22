import time
import thumby
import random
import math

class Position():
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    LEFT_OUTER = 3
    RIGHT_OUTER = 4

class VPosition():
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2    
    TOP_OUTER = 3
    BOTTOM_OUTER = 4    

class Color():
    WHITE = 1
    BLACK = 0

#base object for advance object who contain a Collision Box
class BoxObj:
    def __init__(self):
        self.id = None # id to facilitate operations
        self.hide = False #to draw or not the box object 
        self.applyOffset = False #an offset that only apply at draw time ( no impact on pox physic)

import runner
import controller
import animator

import rectangle
import blit
import sprite
import text

class Vector:        
    def __init__(self, x, y):
        self.setVector(x,y)
    
    def setVector(self, x, y):
        self.x=x
        self.y=y

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalized(self):
        return self / self.length()

    def dot(self, vector):
        return self.x*vector.x +  self.y*vector.y

    def __str__ (self):
        return "Vector ({0}, {1})".format(self.x, self.y)

    def __mul__ (self, multiplier):
        return Vector(self.x * multiplier, self.y *  multiplier)
    
    def __truediv__ (self, divider):

        return Vector(self.x / divider, self.y / divider)    

    def __add__ (self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def __sub__ (self, vector):
        return Vector(self.x - vector.x, self.y - vector.y)

    #return new vector with absolute values
    def absolute(self):
        return Vector(abs(self.x), abs(self.y))

    def copy(self):
        return Vector(self.x, self.y)
    
    #get radian angle of a vector
    def getDegrees(self):
        if self.x == 0:
            degrees = 90 if self.y > 0 else 270
        else:    
            degrees = math.degrees(math.atan(self.y / self.x))
            if(self.x < 0): degrees -= 180
        return degrees % 360
    
class Point:
    def __init__(self, x=0, y=0):
        self.id = None
        self.velocityGoal=Vector(0,0)  #speed per second at cruise speed
        self.velocity=Vector(0,0) #current speed per seconde (pixel)
        self.vAcceleration=Vector(75,75) #accelation multiplier ( this is how much acceleration per seconLd it will get (eg if goal is 25 and acceleration is 75, it will take 333ms to get to goal velocity))
        self.setPoint(x,y)
    
    def setPoint(self, x, y):
        self.x=x
        self.y=y

    def __str__(self):
        return "Point (\Position ({0}, {1})\nGoal ({2})\nVelocity ({3})\nAcceleration({4})\n)".format(self.x, self.y, self.velocityGoal, self.velocity, self.vAcceleration)

    #get vector representing the distance within 2 points
    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Vector(x, y)

    #add a vector to a point and return the new position 
    def __add__(self, vector):
        x = self.x + vector.x
        y = self.y + vector.y
        return Point(x, y)

    def copy(self):
        return Point(self.x, self.y)

    #get a point to a specific distance from a point base on an angle
    def getPointFromDegrees(self, degrees, distance):
        radian = math.radians(degrees)
        return self + Vector(math.cos(radian), math.sin(radian)) * distance

    #get the box position of a satellite object base on the point (the anchor)
    #box: the object the will float aroung the anchor
    #degrees: angle from the the centerBox
    #distance: from the centerBox
    def getSatellitePosition(self, box, degrees, distance):
        pt = self.getPointFromDegrees(degrees, distance)
        pt.x -= box.dim.w/2
        pt.y -= box.dim.h/2
        return pt

class Dimension:

    def __init__(self, w=thumby.display.width, h=thumby.display.height):
        self.setSize(w,h)
        self.pt = None
    
    def setSize(self, w, h):
        self.w = w
        self.h = h
        
    #set a point on dimension representing the right/bottom coordinate of the dimension
    #this point used to update the dimension
    def initPoint(self, pt = None):
        
        self.pt = pt if pt is not None else Point(self.w, self.h)

    #get a Dimension matching a grod of many ( cols*rows ) dimensions 
    def getGridSize(self, cols, rows):
        return Dimension(self.w*cols, self.h*rows)

    def __str__(self):
        return "Dimension ({0}, {1})".format(self.w, self.h)

    def __sub__(self, other):
        w = self.w - other.w
        h = self.h - other.h
        return Dimension(w, h)

#get a box to use with animate and draw via drawer objects
#point attribute is the top left corner of the box
class Box:
    def __init__(self, pt = Point(), dim = Dimension()):
        self.parent = None
        self.pt = pt
        self.dim = dim

    #return a Poin that is the center point of the box
    def getCenterPoint(self):
        return Point(self.pt.x+self.dim.w/2, self.pt.y+self.dim.h/2)

    #return a point for a specific dimension position inside a box
    def getDimensionPosition(self, dim, position = Position.CENTER, vposition = VPosition.MIDDLE):
        
        if (position == Position.LEFT): x = self.pt.x
        if (position == Position.CENTER): x = self.pt.x + self.dim.w/2 - dim.w/2
        if (position == Position.RIGHT): x = self.pt.x + self.dim.w - dim.w
        if (vposition == VPosition.TOP): y = self.pt.y
        if (vposition == VPosition.MIDDLE): y = self.pt.y + self.dim.h/2 - dim.h/2
        if (vposition == VPosition.BOTTOM): y = self.pt.y + self.dim.h - dim.h

        if (position == Position.LEFT_OUTER): x = self.pt.x - dim.w
        if (position == Position.RIGHT_OUTER): x = self.pt.x + self.dim.w
        if (vposition == VPosition.TOP_OUTER): y = self.pt.y - dim.y
        if (vposition == VPosition.BOTTOM_OUTER): y = self.pt.y + self.dim.h

        return Point(x, y)

    #trap the box in another box to limit some velocity movement and other effects
    # properties default override properties per effect
    # WRAP
    #   wrap_item_w: when wrapping on x axe, the offset item will use that widh for the boxed item rather than the boxed item width ( this is useful when multiple sprite of not same size need to wrap on same axe and keep distance ratio)
    #   wrap_item_h: same as wrap_item_w, but on y axe
    def pack(self, parent, boxedEffect = animator.BoxedEffect.WRAP, properties = {} ):
        self.parent = parent
        self.boxedEffect = boxedEffect
        self.boxedEffectProperties = properties

    def unpack(self):
        self.parent=None


    def __str__(self):
        string = "Box:(\n{0}\n{1}".format(self.pt, self.dim)
        if(self.parent != None):
            string = string + "\nParent ({0})\nBoxedEffect({1})".format(self.parent, self.boxedEffect)

        return string+")"

class GridCoordinate:
    def __init__(self, col=0, row=0):
        self.setCoordinate(col,row)
    
    def setCoordinate(self, col, row):
        self.col=col
        self.row=row

    def __str__(self):
        return "Grid coordinate ({0}, {1})".format(self.row, self.col)

#grid for tiling positioning
class Grid(Box):
    
    def __init__(self, pt = Point(), dim = Dimension(8,8), cols = 9, rows = 5):
        self.cols = cols
        self.rows = rows
        self.cellSize = dim
        super().__init__(pt, Dimension(dim.w * cols, dim.h * rows))

    #get a point from col and row position
    #col: 0 = first colda
    #row: 0 = first row
    def getPointFromGridCoordinate(self, coord):

        if (coord.col >= self.cols):
            raise Exception("col {0} is outside cols range 0x{1}".format(coord.col, self.cols-1))
        if (coord.row >= self.rows):
            raise Exception("row {0} is outside rows range 0x{1}".format(coord.row, self.rows-1))

        return Point(self.pt.x+self.cellSize.w*coord.col, self.pt.y+self.cellSize.h*coord.row)

    #get the grid coordinate
    #if pt is not matching grid coordinate, it will roundi to closest coord
    
    def getGridCoordinateFromPosition(self, pt):
        return GridCoordinate(round((pt.x-self.pt.x) / self.cellSize.w), round((pt.y-self.pt.y) / self.cellSize.h))



#frontend drawing engine
class Drawer:
    
    screenBox = Box()

    #frontend game data
    class Data():
        def reset(self):
            self.rectBoxes = []
            self.blitBoxes = []
            self.spriteBoxes = []
            self.textBoxes = []
            self.points = []
        
        #update positions
        def update(self, animator):
            for obj in self.rectBoxes: animator.updateBox(obj.box)
            for obj in self.blitBoxes: animator.updateBox(obj.box)
            for obj in self.spriteBoxes: animator.updateBox(obj.box)
            for obj in self.textBoxes: animator.updateBox(obj.box) 
            for pt in self.points: animator.updatePpoint(pt) 
        
        #draw on screen
        def draw(self, drawer):
            
            vOffset = Vector(random.randint(-1,1), random.randint(-1,1))

            self.__draw(self.rectBoxes, lambda obj: drawer.__rectDrawer.draw(obj, vOffset))
            self.__draw(self.blitBoxes, lambda obj: drawer.blitDrawer.draw(obj, vOffset))
            self.__draw(self.textBoxes, lambda obj: drawer.textDrawer.draw(obj, vOffset))
            self.__draw(self.spriteBoxes, lambda obj: drawer.spriteDrawer.draw(obj, vOffset))

            for pt in self.points: drawer.pointDrawer.draw(obj)
            
        def __draw(self, boxObjs, drawcallback):
            for obj in boxObjs:
                if(obj.hide):
                    continue
                drawcallback(obj)
        
        def removeById(self, id):
            
            for index in range(len(self.rectBoxes)-1, -1, -1):
                if(self.rectBoxes[index].id == id): self.rectBoxes.pop(index)
            for index in range(len(self.blitBoxes)-1, -1, -1):
                if(self.blitBoxes[index].id == id): self.blitBoxes.pop(index)
            for index in range(len(self.textBoxes)-1, -1, -1):
                if(self.textBoxes[index].id == id): self.textBoxes.pop(index)
            for index in range(len(self.spriteBoxes)-1, -1, -1):
                if(self.spriteBoxes[index].id == id): self.spriteBoxes.pop(index)
            for index in range(len(self.points)-1, -1, -1):
                if(self.points[index].id == id): self.points.pop(index)
    
    #set the fps for the game
    def __init__(self):
        self.animator = animator.Animator()
        self.controller = controller.Controller()
        self.textDrawer = text.TextDrawer()
        self.blitDrawer = blit.BlitDrawer()
        self.__rectDrawer = rectangle.RectangleDrawer()
        self.spriteDrawer = sprite.SpriteDrawer(self.animator)
        self.pointDrawer = PointDrawer(self.animator)

        random.seed(time.ticks_ms())
        thumby.display.setFPS(self.animator.maxFps)
        self.data = self.Data()
        self.reset()

    def reset(self):
        self.animator.reset()
        self.data.reset()

    def update(self):
        self.data.update(self.animator)
        self.animator.runTimers()
        self.data.draw(self)

        thumby.display.update()

    #print str to screen
    def debug(self, str, line=1):
        self.textDrawer.drawLine(text.Text(str),line)

    def __printFps(self):
        self.textDrawer.drawLine(text.Text(str(self.animator.getFps()) + "FPS",Position.RIGHT),5)
        
        
class PointDrawer():
    
    def draw(self, pt):
        

        thumby.display.setPixel(round(pt.x), round(pt.y),  enjfine.Color.WHITE)


