# Mode Parameters
Mode_GroundProximitry = False  #1
Mode_Ascending = False #2
Mode_Descending = False #4
Mode_InFlight = False #8
Mode_Stationary = False #16
Mode_HasGpsFix = False #32

def ModeBitArray():
    value = 0
    if Mode_GroundProximitry:
        value += 1
    if Mode_Ascending:
        value += 2
    if Mode_Descending:
        value += 4
    if Mode_InFlight:
        value += 8
    if Mode_Stationary:
        value += 16
    if Mode_HasGpsFix:
        value += 32      
    return value