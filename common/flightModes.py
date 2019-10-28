# Mode Parameters stored in a bit array  (Set/Get)
class Modes:

    def __init__(self):
        self.GroundProximity = False  #1
        self.Ascending = False #2
        self.Descending = False #4
        self.InFlight = False #8
        self.Stationary = False #16
        self.HasGpsFix = False #32

    def GetModeBitArray(self):
        value = 0
        if self.GroundProximity:
            value += 1
        if self.Ascending:
            value += 2
        if self.Descending:
            value += 4
        if self.InFlight:
            value += 8
        if self.Stationary:
            value += 16
        if self.HasGpsFix:
            value += 32    
        return value

    def SetModeBitArray(self,bitValues):
        value = int(bitValues)
        if value & 1 > 0:
            self.GroundProximity = True
        if value & 2 > 0:
            self.Ascending = True
        if value & 4 > 0:
            self.Descending = True
        if value & 8 > 0:
            self.InFlight = True
        if value & 16 > 0:
            self.Stationary = True
        if value & 32 > 0:
            self.HasGpsFix = True                                        

    def StatusMessage(self):
        msg = ""
        if self.InFlight:
            if self.Ascending:
                msg = msg + " Ascending "
            elif self.Descending:
                msg = msg + " Descending "
        elif self.Stationary:
            msg = msg + "  Stationary "
        if self.GroundProximity == True:
            msg = msg + " Ground Proximity "        
        if self.HasGpsFix == False:
            msg = msg + " No Gps Fix. "
        return msg



# Test Cases
#SetModeBitArray(35)
#print("GroundProximitry=" + str(GroundProximitry))
#print("Ascending=" + str(Ascending))
#print("Descending=" + str(Descending))
#print("HasGpsFix=" + str(HasGpsFix))
