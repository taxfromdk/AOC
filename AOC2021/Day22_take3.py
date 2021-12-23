#day22
#
#https://adventofcode.com/2021/day/22

import functools

def getRange(x):
    v = x.split("..")
    return int(v[0]), int(v[1])

def getAxis(x):
    v = x.split("=")
    return getRange(v[1])

def parse(text):
    #print(text)
    inst=[]
    lines=text.split("\n")
    for l in lines:
        state, rng= l.split(" ")
        #print(state, rng)
        axes=rng.split(",")
        #print(axes)
        vals = [getAxis(a) for a in axes]
        
        inst.append((state,vals))
    return inst

############################
#
#  Axis
#
############################

#Model sampling as falling panes of glass
#use fact that axes can be treated seperately
#Axes can be combined by knowing if we hit in all axis hitters remain 
#else they miss

class Axis:
    #ranges are natural numbers
    #end values are inclusive
    def __init__(s, r):
        s.r = r
        assert(isinstance(r, tuple))
        assert(len(list(r)) == 2)
        assert(isinstance(r[0], int))
        assert(isinstance(r[1], int))
        assert(r[0]<=r[1])
    
    def __str__(s):
        return "%dto%d"%(s.r[0], s.r[1])
    
    def draw(s, c, w):
        l = " "*(s.r[0])
        l+= c * (s.r[1]-s.r[0] + 1)
        l+= " " * (w-len(l))
        l+= str(s.r)
        print(l)
        
    def l(s):
        return s.r[1]-s.r[0]+1
        
    def shatter_against(s, other):
        h0,h1 = s.r
        s0,s1 = other.r
        p = []
        
        #low miss part
        if h0<s0:
            p.append((Axis((h0,min(h1,s0-1))),"m"))
        
        #middle hit part
        if h1>=s0 and h0<=s1:
            p.append((Axis((max(h0,s0),min(h1,s1))),"h"))
         
        #high miss part
        if s1<h1:
            p.append((Axis((max(s1+1,h0),h1)),"m"))
            
        return p
    
    def covers(s, other):
        return s.r[0] <= other.r[0] and s.r[1] >= other.r[1]
    
def ran(x0, l):
    return (x0, x0+l-1)

def test_axis(len_hitter, len_stator, margin):
    W=20
    field_length = (len_hitter + margin)*2 + len_stator
    print("hitter:%d stator:%d margin:%d"%(len_hitter, len_stator, margin))
    for i in range(field_length - len_hitter + 1):
        stator = Axis(ran(len_hitter+margin, len_stator))
        hitter = Axis(ran(i,len_hitter))
        pieces = hitter.shatter_against(stator)
        hitter.draw("H",W)
        stator.draw("S",W)
        if len(pieces) == 0:
            print("!"*W)
        for i in range(len(pieces)):
            pieces[i][0].draw(pieces[i][1],W)
        print("-"*W)
            
#test_axis(2,4,1)
#test_axis(3,3,1)
#test_axis(4,2,1)

############################
#
#  Algorithm
#
############################


#with a robust axis the task can be solved
#by making a set of three axis covering the
#scan area and shatter each axis in the 
#operations in reverse order. Volumes that 
#hit on all axis adds to the accumulators and missing volumes
#continue through remaining operations. At the end 
#remaining are counted as off.
#
#A note on performance. The most significant effect on performance 
#was merging shattered areas. It vastly reduced the hitter list size 
#and kept runtime fast.
#
#It was also tried to filter out operations if they were "occluded"
#by later operations. But it hat little effect

def merge(a,b):
    #return None
    ax,ay,az = a
    bx,by,bz = b
    if ay == by and az == bz:
        if ax[1]+1==bx[0]:
            return ((ax[0], bx[1]),ay,az)    
        if bx[1]+1==ax[0]:
            return ((bx[0], ax[1]),ay,az)    
    if ax == bx and az == bz:
        if ay[1]+1==by[0]:
            return (ax,(ay[0], by[1]),az)    
        if by[1]+1==ay[0]:
            return (ax,(by[0], ay[1]),az)    
    if ax == bx and ay == by:
        if az[1]+1==bz[0]:
            return (ax,ay,(az[0], bz[1]))    
        if by[1]+1==ay[0]:
            return (ax,ay,(bz[0], az[1]))    
    return None   
        

def solve1(fn, part, facit):
    print("Part %d on %s"%(part, fn))
    text = open(fn).read()
    r=50
    instructions = parse(text)
    if part == 2:
        for t in instructions:
            inst, ranges = t
            for a,b in ranges:
                r = max(r,max(abs(a),abs(b)))
    
    scanarea=((-r,r),(-r,r),(-r,r))
    hitters=[scanarea]
    scanvolume= Axis(scanarea[0]).l()*Axis(scanarea[1]).l()*Axis(scanarea[2]).l()
    off=0
    on=0
    instructions = list(reversed(instructions))
    instlen = len(instructions)
    
    while len(instructions) > 0:
        t = instructions.pop(0)
        inst, ranges = t
        rx,ry,rz=ranges
        
        print("%d/%d"%(len(instructions),instlen), inst, rx, ry, rz, "hitlist:", len(hitters))
        x=Axis(rx)
        y=Axis(ry)
        z=Axis(rz)
            
        next_hitters=[]
        for hx,hy,hz in hitters:
            ax = Axis(hx).shatter_against(x)
            ay = Axis(hy).shatter_against(y)
            az = Axis(hz).shatter_against(z)
            tmp = []
            for xx,tx in ax:
                for yy,ty in ay:
                    for zz,tz in az:
                        vol = xx.l()*yy.l()*zz.l()
                        #print(tx, ty, tz)
                        if tx==ty==tz=="h":
                            if inst=="on":
                                on+=vol
                            else:
                                off+=vol
                        else:
                            tmp.append((xx.r,yy.r,zz.r))    
            
            #Newly generated volumes are highly 
            #mergeable
            if len(tmp) > 1:
                for i in range(len(tmp)):
                    a = tmp.pop(0)
                    for j in range(len(tmp)):
                        b = tmp.pop(0)
                        m = merge(a,b)
                        if not m is None:
                            a = m
                            break 
                        tmp.append(b)
                    tmp.append(a)
            next_hitters += tmp
            
        hitters=next_hitters
        
    for hx,hy,hz in hitters:
        vol += Axis(hx).l()*Axis(hy).l()*Axis(hz).l()
        off += vol
    print("fn:", fn)
    print("part:", part)
    print("on:", on)
    print("off:", off)
    print("scanvolume:", scanvolume)
    if not facit is None:
        if on != facit:
            print("on were supposed to be", facit)
            assert(0)
        else:
            print("Correct!!!")
            print("="*50)
            
            #assert(0)
    
solve1("i22_test.txt",1,590784)    
solve1("i22.txt",1, 650099)

solve1("i22_test2.txt",2,2758514936282235)    
solve1("i22.txt",2,1254011191104293)
