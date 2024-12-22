
                
        #blood effect
                
           velocity = self.__properties.get("velocity", Vector(45,-45))
                length = velocity.length() * 4
            
                if velocity.x == 0:
                    radian = math.radians(90) if velocity.y > 0 else math.radians(270)
                else:    
                    radian = math.atan(velocity.y / velocity.x)

                print(math.degrees(radian))

                for i in range(self.__properties.get("particles", 24)):
                    r = radian + math.radians(random.randint(-self.__properties.get("degrees", 30), self.__properties.get("degrees", 30)))
                    pt =  spriteBox.box.getCenterPoint()
                    pt.velocityGoal = Vector(0,50)
                    pt.velocity = Vector(math.cos(r), math.sin(r)) * length * random.uniform(.75,1)
                    pt.vAcceleration.x = pt.velocity.absolute().x * random.uniform(.5,1) 
                    self.__points.append(pt)                
