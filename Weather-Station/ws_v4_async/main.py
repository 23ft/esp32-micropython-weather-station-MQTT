# Implementacion station con programacion asincronica.
# Mañana resalto caracteristicas que e ido aprendiendo de este tipo de programacion.

from umqttAsyncio import MQTTClient
from machine import I2C, Pin
from configMQTT import config as configMQTT
import uasyncio as asyncio
import BMP280
import sys
import utime
import ujson


class StationExample1():
    def __init__(self, cnf):
        # BPM280
        sda = Pin(21)
        scl = Pin(22)
        self.green = Pin(19, Pin.OUT)
        self.bmpPin = I2C(0, scl=scl, sda=sda)
        self.bmpSensor = BMP280.BMP280(self.bmpPin)
        self.sensor = self.bmpSensor

        self.flagThreadSafe = False

        # config Broker
        self.SERVER = '35.199.113.247'
        self.configMQTT = cnf
        self.configMQTT['subs_cb'] = self.callback # callback for recived sms from server.
        self.configMQTT['connect_coro'] = self.conn_han # handler for subscribers
        self.configMQTT['server'] = self.SERVER # ip broker MQTT
        self.topicPub = b'tempTabogo/DHT11'
        

        MQTTClient.DEBUG = True  # Optional: print diagnostic messages
        self.client = MQTTClient(self.configMQTT)

    # callback for recived new sms.
    def callback(self, topic, msg, retained):
        print((topic, msg, retained))
    
    # Function for check connection to Broker.
    async def checkBroker(self):
        print("check")
        await self.client.broker_up()

    # Handler for subscriber to topics.
    async def conn_han(self, client):
        await self.client.subscribe('foo_topic', 1)
    
    # second task function for v2.
    # in v2 the unque task present is taskMain.
    # measure andr generate the JSON string.
    async  def sensorTask(self):
        if self.flagThreadSafe:
                print("Bye task BMP280")
                sys.exit()

        # Tomando datos del sensor.
        self.temp = self.sensor.getTemp()
        self.press = self.sensor.getPress()
        
        # Generando objeto python [diccionario]
        self.jsonFiles += 1
        self.jsonLocal = {
            "id": self.jsonFiles,
            "Temp": self.temp,
            "Hum": self.press
        } 
        
        # conviertiendo objeto python en JSON-STRING
        self.jsonSend = ujson.dumps(self.jsonLocal)
        
        
    # Second task for measure sensor BMP280. v1
    async def sensorMeasure(self, sensor=None):
        #print("> Task measure is active!")
        self.jsonFiles = 0
        while True:
            if self.flagThreadSafe:
                print("Bye task BMP280")
                sys.exit()

            # Tomando datos del sensor.
            self.temp = self.sensor.getTemp()
            self.press = self.sensor.getPress()
            
            # Generando objeto python [diccionario]
            self.jsonFiles += 1
            self.jsonLocal = {
                "id": self.jsonFiles,
                "Temp": self.temp,
                "Hum": self.press
            } 

            # conviertiendo objeto python en JSON-STRING
            self.jsonSend = ujson.dumps(self.jsonLocal)
            await asyncio.sleep(3)

    # taskMain is a loop for measure and publish data for the MQTT broker. v2
    async def taskMain(self):
        # connection for MQTT server using the client.
        await self.client.connect()
        
        # flags for the time manage.
        self.timeMQTTone = utime.time()
        self.timeMQTTtwo = 0
        
        # variable for id JSON.
        self.jsonFiles = 0
        
        #print("time1 = ", self.timeMQTTone)
        
        # loop main.
        while True:
            if self.flagThreadSafe:
                print("Bye task mqtt")
                sys.exit()
            
            if (self.timeMQTTtwo - self.timeMQTTone) > 20:
                print("b")
                await self.checkBroker()
                self.timeMQTTone = utime.time()
            
            # Trying to measure data.
            try:
                await self.sensorTask()
            except Exception as e:
                print("[taskMain] Error in method sensorTask: ", e)
            
            # trying to publish in server.
            try:
                print('publish #', self.jsonFiles, " >> ", self.jsonSend)
                await self.client.publish(self.topicPub, self.jsonSend)
                await asyncio.sleep(2)
            
            except Exception as e:
                print("[taskMain] Error in publish: ", e)
                try:
                    print("[sys] Finish the tasks!")
                    sys.exit()
                finally:
                    print("[taskMain] Cerrando conexion con broker MQTT")
                    self.client.close()
                    
            self.timeMQTTtwo = utime.time()
            #print("time 2 ", self.timeMQTTtwo)
    
    # this task is a client for MQTT and publish data generate from method sensorMeasure(). v1
    async def mqttTask(self):
        #print("> Task mqtt is active!")
        await self.client.connect()
        self.timeMQTTone = utime.time()
        print("time1 = ", self.timeMQTTone)
        self.timeMQTTtwo = 0
        
        while True:
            if self.flagThreadSafe:
                print("Bye task mqtt")
                sys.exit()
            
            if (self.timeMQTTtwo - self.timeMQTTone) > 20:
                print("b")
                await self.checkBroker()
                self.timeMQTTone = utime.time()
            
            # trying to publish in server.
            try:
                print('publish #', self.jsonFiles, " >> ", self.jsonSend)
                await self.client.publish(self.topicPub, self.jsonSend)
                await asyncio.sleep(2)
            
            except Exception as e:
                print("[Task MQTT] Error in publish: ", e)
                try:
                    print("[sys] Finish the tasks!")
                    sys.exit()
                finally:
                    print("[Task MQTT] Cerrando conexion con broker MQTT")
                    self.client.close()
            self.timeMQTTtwo = utime.time()
            #print("time 2 ", self.timeMQTTtwo)
    
    # rutine for events in button user.
    async def buttonCheck(self):
        button = Pin(4, Pin.OUT)
        cont = 0
        while True:
            await asyncio.sleep(1)
            if button.value():
                cont += 1
                print("\t\t button: ", cont)
                if cont == 5:
                    print("\t\t EXIT")
                    cont = 0
                    #self.flagThreadSafe = True
                    sys.exit()
                await asyncio.sleep(1)
    
    # contructor de tareas.
    async def createTasks(self):
        
        # for v1
        #asyncio.create_task(self.mqttTask())
        #asyncio.create_task(self.sensorMeasure())
        
        asyncio.create_task(self.taskMain())
        asyncio.create_task(self.buttonCheck())

    # loop de eventos o loop de task.
    async def main(self):

        await self.createTasks()
        # await asyncio.gather(t1, t2)
        # await asyncio.run(t1)
        # await asyncio.run(t2)

        while True:
            self.green.value(not self.green.value())
            await asyncio.sleep(2)

        print("finish main")

    def run(self):
        asyncio.run(self.main())


app = StationExample1(configMQTT)

try:
    app.run()
finally:
    print("[ESP32 STOP TASK] Stop the task main and disconnect from broker MQTT")
    app.client.close()  # Prevent LmacRxBlk:1 errors

