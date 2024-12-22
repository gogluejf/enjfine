
        w = parent_box.w + self.w*2
        h = parent_box.h + self.h*2
        map = ["" for c in range( math.ceil(h/8) * w )]
        for y in range(h):
             for x in range(w):
                if(x<self.w or x > self.w+parent_box.w or y<self.h or y > self.h+parent_box.h):
                    bit  = "1"
                else:
                    bit = "0"

                map[math.floor(y/8)*w + x] = bit + map[math.floor(y/8)*w + x]
                
        byte_map=[]
        for c in range( math.ceil(h/8) * w):
            byte_map.append(int(map[c],2))


        self.mask_sprite = thumby.Sprite(w,h,bytearray(byte_map),parent_box.point.x-self.w,parent_box.point.y-self.h,0)   
        
        
        
        

#skull_map = bytearray([0,60,254,51,255,51,254,60])
#skullSpBox = SpriteBox(skull_map, Dimension(8, 8))        




        #convert milliseconds to frames equivalent based on current frame rate
        #this useful for fonction requiring constant interval ( interval will be precised, base on frame, and guaranteed similar duration no matter the current framerate )
        def getFrameFromDuration(self, ms):
            return self.getFps()/1000*ms
