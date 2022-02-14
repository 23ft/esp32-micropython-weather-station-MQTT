import esp
import gc
from conf import pin
from conf import wifi

gc.enable()
gc.collect()

esp.osdebug(None)

# 
#     ~Conexion Wifi ESP32~
# 

ssid = 'Sebas y felipe'
password = 'Manuelpipe1'

# Using personal module wifi for connection.
internet = wifi.Wifi(ssid, password, mode_sta=True)
if internet.check():
    print("[Boot] The ESP already connect to wifi.")
else:
    print('[Boot] The ESP not connect to wifi...')
    internet.connect()

#
#     ~Configuracion Pines~
# 

s_dht11 = 13

gpio = pin.Pins(dht11 = s_dht11)
pins = gpio.Start()

print("\n[Boot log] Pin DHT11 enable: ", pins["DHT11"])
# print("\n[Boot log] Pin's IN enables: ", pins['IN'])
# print("[Boot log] Pin's OUT enables: ", pins['OUT'])
# print("[Boot log] Pin's PWM enables: ", pins['PWM'])
