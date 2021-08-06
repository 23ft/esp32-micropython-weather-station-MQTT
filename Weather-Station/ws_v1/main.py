global sensor

import utime

cont = 1

while True:
    utime.sleep(1)
    sensor.measure()
    
    temp = sensor.temperature()
    hum = sensor.humidity()
    
    print("Measure #", cont)
    print("> Temp is: ", temp, "\n> Humidity is: ", hum, "\n")
    
    
    cont += 1
    
    