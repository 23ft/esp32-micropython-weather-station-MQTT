import machine as m
import utime

class Pins():
    def __init__(self, pinsIn=[], pinsOut=[], pinsPWM=[], PWMfrec=0, dht11=None, dht22=None, dhtili=None):
        self.pIn = pinsIn
        self.pOut = pinsOut
        self.pPwm = pinsPWM
        self.PWMfrec = PWMfrec
        self.dht11 = dht11
        self.dht22 = dht22
        self.dhtili = dhtili
        
        self.pIns = []
        self.pOuts = []
        self.pPwms = []

        # Config the sensor DHT.    
        if ((self.dht11 != None) and (self.dht22 != None) and (self.dhtili == None)):
            print('[pin module error] ERROR in select sensor and the parameter for tow sensor is false')

        elif (self.dht11 != None):
            try:
                from dht import DHT11
                self.sensordht = DHT11(m.Pin(int(self.dht11)))
            except:
                print('[pin module error] ERROR trying initialization pin DHT11')
            
        elif (self.dht22 != None):
            try:
                from dht import DHT22
                self.sensordht = DHT22(m.Pin(int(self.dht22)))
            except:
                print('[pin module error] ERROR trying initialization pin DHT22')
              
    def restartduty(self):
        for resduty in self.pPwms:
            self.pPwms[resduty].duty(0)
        
    def Start(self):
        if (not self.pIn == []):
            self.pIns = {str(pinin): m.Pin(pinin, m.Pin.IN) for pinin in self.pIn}

        if (not self.pOut == []):
            self.pOuts = {str(pinout): m.Pin(pinout, m.Pin.OUT) for pinout in self.pOut}

        if (not self.pPwm == []):
            self.pPwms = {str(pinpwm): m.PWM(m.Pin(pinpwm, m.Pin.OUT), freq=self.PWMfrec, duty=0) for pinpwm in self.pPwm}
            self.restartduty()

        print('\n[Config GPIO] Pins-IN, Pins-OUT, Pins-PWM is started!')
        return {
            'IN':self.pIns, 
            'OUT':self.pOuts, 
            'PWM':self.pPwms, 
            'DHT11':self.sensordht, 
            'DHT22':self.dht22
            }
