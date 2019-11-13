import math
# Mode Parameters stored in a bit array  (Set/Get)
class Modes:
    IsArmed = False
    THRESHOLD_ALTITUDE_METERS = 600  # arm once above this altitude, alarm after arming when falls below this altitude

    def __init__(self):
        self.GroundProximity = False  #1
        self.Ascending = False #2
        self.Descending = False #4
        self.InFlight = False #8
        self.Stationary = False #16
        self.HasGpsFix = False #32
        self.AirborneGpsMode = False #64

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
        if self.AirborneGpsMode:
            value += 64                 
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
        if value & 64 > 0:
            self.AirborneGpsMode = True               

    def StatusMessage(self, altitudeMeters, rateOfClimbMeters):
        msg = ""
        verticalPosition = " no altitude reading."
        try:
            climb = int(float(rateOfClimbMeters))
            verticalPosition = str(altitudeMeters) + " meters at " + str(climb) + " meters per second,"
        except:
            print("Invalid GPS altitude or climb indication.")     

        if self.GroundProximity:
            msg = msg + " Ground Proximity. "
        if self.Ascending:
            msg = msg + " Ascending through " + verticalPosition
        elif self.Descending:
            msg = msg + " Descending through " + verticalPosition  
        if self.HasGpsFix == False:
            msg = msg + " No Gps Fix, "
        return msg

    def SetStatus(self, GpsAltitudeMeters, PressureAltitudeMeters, verticalSpeed):
        altMeters = 0 
        try:
            altMeters = int(GpsAltitudeMeters)
        except:
            try:
                altMeters = int(PressureAltitudeMeters)
            except:
                print("Unable to get altitude from GPS or altimeter!")

        if altMeters > self.THRESHOLD_ALTITUDE_METERS:
            self.IsArmed = True
        if self.IsArmed and altMeters < self.THRESHOLD_ALTITUDE_METERS:
            print("Gound Alarm")
            self.GroundProximity = True
        else:
            self.GroundProximity = False

        if verticalSpeed > 0.25:
            self.Ascending = True
            self.Descending = False
            self.Stationary = False
        elif verticalSpeed < 0.25:
            self.Ascending = False
            self.Descending = True
            self.Stationary = False
        else:
            self.Ascending = False
            self.Descending = False
            self.Stationary = True      

# Ublox stuff.
# Poll for current model
#ubxtool -p CFG-NAV5
# Set model
#ubxtool -p MODEL -m 6
# Save config
#ubxtool -p SAVE


# Test Cases
#SetModeBitArray(35)
#print("GroundProximitry=" + str(GroundProximitry))
#print("Ascending=" + str(Ascending))
#print("Descending=" + str(Descending))
#print("HasGpsFix=" + str(HasGpsFix))
