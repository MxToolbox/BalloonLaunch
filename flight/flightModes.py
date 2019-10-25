# Mode Parameters stored in a bit array  (Set/Get)

GroundProximitry = False  #1
Ascending = False #2
Descending = False #4
InFlight = False #8
Stationary = False #16
HasGpsFix = False #32

def GetModeBitArray():
    global GroundProximitry
    global Ascending
    global Descending
    global InFlight
    global Stationary
    global HasGpsFix
    value = 0
    if GroundProximitry == True:
        value += 1
    if Ascending == True:
        value += 2
    if Descending == True:
        value += 4
    if InFlight == True:
        value += 8
    if Stationary == True:
        value += 16
    if HasGpsFix == True:
        value += 32    
    return value

def SetModeBitArray(value):
    global GroundProximitry
    global Ascending
    global Descending
    global InFlight
    global Stationary
    global HasGpsFix       
    if value & 1 > 0:
        GroundProximitry = True
    if value & 2 > 0:
        Ascending = True
    if value & 4 > 0:
        Descending = True
    if value & 8 > 0:
        InFlight = True
    if value & 16 > 0:
        Stationary = True
    if value & 32 > 0:
        HasGpsFix = True                                        


# Test Cases
#SetModeBitArray(35)
#print("GroundProximitry=" + str(GroundProximitry))
#print("Ascending=" + str(Ascending))
#print("Descending=" + str(Descending))
#print("HasGpsFix=" + str(HasGpsFix))
