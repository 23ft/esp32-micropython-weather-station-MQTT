# LIbreria creada con el fin de reutilizar codigo en la ESP32.
# Utilidad: conexion wifi de tarjeta ESP32.

"""
Documentacion.
"""
# Clase wifi.Wifi()
#
# obj = wifi.Wifi(red_name, red_password, mode_sta=(True/False), mode_ap=(True/False))
# Instanciamos la clase Wifi la cual le pasaremos 4 parametros.
#
# > nombre de red (red_name)
# > contraseña de la red (red_password)
# > activar o desactivar modo Station, si se le pasa True a la variable mode_sta se inicializa como Station. (mode_sta=(True/False))
# > activar o desactivar modo AccesPoint, si se le pasa True a la variable mode_sta se inicializa como AccesPoint. (mode_ap=(True/False))

#Methodos clase wifi.Wifi()
#
# obj.

import network

class Wifi():
    def __init__(self,  ssid, password, mode_sta=False,  mode_ap=False):
        if mode_sta:
            self.mode_sta = mode_sta
            self.ssid = str(ssid)
            self.password = str(password)
            self.modeSta()
            
        if mode_ap:
            self.mode_ap = mode_ap
            self.ssid = str(ssid)
            self.password = str(password)
            self.modeAp()
            
    def connect(self):
        if self.mode_sta:
            self.station.connect(self.ssid, self.password)
            print("[Wifi log - connect] conectando...")
            while self.station.isconnected() == False:
                pass
            
            print("[Wifi log - connect] Conectado a internet con extio!")
            print("[Wifi log - connect] Red conectado: ", self.ssid)
            print("[Wifi log - connect] Informacion conexion: ", self.station.ifconfig())
            
            return self.station.isconnected() == True
        
        if self.mode_ap:
            # Mode in study.
            pass
            
    def modeSta(self):
        try:
            # instanciamos modo Station.
            self.station = network.WLAN(network.STA_IF)
            
            # Activamos el modo Station
            self.station.active(True)
            print('[Wifi log] mode STATION actived.')
            
        except:
            print('[Wifi Error - modeSta] Error al intentar iniciar  en modo Station.')
            
    def modeAp(self):
        try:            
            # instanciamos modo Accespoint.
            self.ap = network.WLAN(network.STA_IF)
            
            # Activando AccesPoint modo.
            self.ap.active(True)
            print('[Wifi log] mode AP actived.')
            
        except:
            print('[Wifi Error - modeAp] Error al intentar iniciar  en modo Accespoint.')
        
    def check(self):
        print('[Wifi check] check conection... ')
        if self.station.isconnected():
            print('[Wifi check] The ESP32 is connected to wifi. ')
            print('[Wifi check] Dates connection: ',self.station.ifconfig())
            
            # Return true if the ESP32 is connect to wifi.
            return True
        else:
            print('[Wifi check] The ESP32 isnt connected to wifi. ')
            print('[Wifi check] Restart connection...')
            
            if self.connect():
                print('[Wifi check] The ESP32 logred reconect ')
                print('[Wifi check] wifi reconect dates: ' , self.station.ifconfig())
                
                # Return true if the ESP32 is connect to wifi.
                return True
            else:
                print('[Wifi check] connection refused... RESET ESP32')
                import machine
                machine.reset()
"""
Datos wifi personales.
"""

# Internet
ssid = 'Sebas y Felipe'
password = '@LSISENSSSNMYMS060201@'








