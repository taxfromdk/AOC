import re

def getints(text):
    return [int(n) for n in re.findall(r'-?\d+', text)]

    
class M:
    inst="adv,bxl,bst,jnz,bxc,out,bdv,cdv".split(",")
    
    
    def __init__(s,p):
        s.p=p
        
    def u(s):
        while 1:
            if s.pc>=len(s.p):
                return None
             
            op=M.inst[s.p[s.pc]]
            s.pc+=1
            literal=s.p[s.pc]
            
            result=(0,0)
            if not literal in range(8):
                result=(1,None)
            s.pc+=1
        
            combo=[0,1,2,3,s.A,s.B,s.C,None][literal]
            
            
            if op=="adv":
                if combo is None:
                    return None
                s.A=int((s.A)/(1<<combo))
            elif op=="bdv":
                if combo is None:
                    return None
                s.B=int((s.A)/(1<<combo))
            elif op=="cdv":
                if combo is None:
                    return None
                s.C=int((s.A)/(1<<combo))
            elif op=="bxl":
                s.B=s.B ^ literal
            elif op=="bst":
                if combo is None:
                    return None
                s.B=combo%8
            elif op=="jnz":
                if not s.A==0:
                    s.pc=literal
            elif op=="bxc":
                s.B=s.B^s.C
            elif op=="out":
                if combo is None:
                    return None
                result=(1,combo%8)
                #print(output[-1])
            
            if result[0]:
                return result[1]
            
            
            
            
    def run(s):
        o=[]
        while 1:
            r=s.u()
            if r is None:
                break
            else:
                o.append(r)
        return o
    
    def setstate(s,x): 
        s.A,s.B,s.C,s.pc=x
    
    def getstate(s):
        return s.A,s.B,s.C,s.pc
    
    def pseudo(s):
        print("---pseudo start---")
        print("prog:",s.p)
        
        for i in range(0,len(s.p),2):
            ins =s.p[i]
            inst=M.inst[ins]
            
            literal=s.p[i+1]
            combo="0123ABC"[literal]
            expl="?"
            if inst=="adv":
                expl="A=A/(1<<%s)"%(combo)
            elif inst=="bdv":
                expl="B=A/(1<<%s)"%(combo)
            elif inst=="cdv":
                expl="C=A/(1<<%s)"%(combo)
            elif inst=="bxl":
                expl="B=xor(B,%s)"%(literal)
            elif inst=="bst":
                expl="B=%s%%8"%(combo)
            elif inst=="jnz":
                expl="jump to %s if A"%(literal)
            elif inst=="bxc":
                expl="B=xor(B,C)"
            elif inst=="out":
                expl="print %s%%8"%(combo)
            print("%02d:%d:%s:%s"%(i,ins,inst,expl))
        print("---pseudo end---")

