# Mode Parameters
GroundProximitry = False  #1
Ascending = False #2
Descending = False #4
InFlight = False #8
Stationary = False #16
HasGpsFix = False #32

def ModeBitArray():
    value = 0
    if GroundProximitry:
        value += 1
    if Ascending:
        value += 2
    if Descending:
        value += 4
    if InFlight:
        value += 8
    if Stationary:
        value += 16
    if HasGpsFix:
        value += 32      
    return value