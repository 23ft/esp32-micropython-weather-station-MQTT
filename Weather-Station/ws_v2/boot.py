import esp
from conf import pin
from conf import wifi

esp.osdebug(None)

# 
#     ~Conexion Wifi ESP32~
# 

ssid = 'Sebas y Felipe'
password = '@LSISENSSSNMYMS060201@'

# Using personal module wifi for connection.
internet = wifi.Wifi(ssid, password, mode_sta=True)
internet.connect()

#
#     ~Configuracion Pines~
# 

s_dht11 = 14

gpio = pin.Pins(dht11 = s_dht11)
pins = gpio.Start()

print("\n[Boot log] Pin DHT11 enable: ", pins["DHT11"])
# print("\n[Boot log] Pin's IN enables: ", pins['IN'])
# print("[Boot log] Pin's OUT enables: ", pins['OUT'])
# print("[Boot log] Pin's PWM enables: ", pins['PWM'])
