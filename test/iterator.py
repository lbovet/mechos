def a(b):    
    for i in range(3):
        print b+" "+str(i)
        yield
        
c = a("hello")
        
print "defined"
        
for i in c:
    pass
