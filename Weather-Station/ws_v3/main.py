import sys
import utime
from machine import unique_id, soft_reset, Pin, reset, I2C
import ubinascii
import ujson
import _thread
from lib.umqtt.simple2 import MQTTClient
import BMP280

class WeatherStation():
    def __init__(self):

        #
        #     ~Dates MQTT~
        #
        self.mqtt_id = ubinascii.hexlify(unique_id())
        self.mqtt_host = "35.199.113.247"
        self.mqtt_port = 1883
        self.mqtt_user = None
        self.mqtt_pass = None
        self.mqtt_topics_sub = []
        self.mqtt_topics_pub = []
        self.flag_broker = False

        #
        #     ~Flags Threads~
        #
        self.flagBroker_th0 = False
        self.flagBroker_th1 = False
        self.flagErrorTh0 = False
        self.flagErrorTh1 = False
        self.flagStop_ths = False
        self.flagClientCon = False
        self.flagErrorDHT = 0

        #
        #     ~Thread 0 Propietys~
        #
        self.jsons_send = 0
        self.topicx = b'tempTabogo/DHT11'

        # probe pin for stop program.
        self.json_broker = {}
        self.jsonGod = None
        
        #
        #     ~Configuracion Pines~
        # 

        # Pin for STOP button.
        self.stopPin = Pin(4, Pin.IN)
        
        # BMP280 Propietis.
        self.sda = Pin(21)
        self.scl = Pin(22)
        self.bmpPin = I2C(0, scl= self.scl, sda= self.sda)
        self.bmpSensor = BMP280.BMP280(self.bmpPin)

    def getBPM280(self):
        self.temp = self.bmpSensor.getTemp()
        self.hum = self.bmpSensor.getPress()
        utime.sleep(1)
        
        return True
    def MQTTsubs(self):

        pass
        # for topic in self.mqtt_topics_sub:
        #print("[Client MQTT] Subscribe to topic: ", topic)
        # self.client.subscribe(topic)

    def MQTTCallBack(self, topic, string):
        print("[SMS NEW] topic: ", topic,
              "\n [SMS NEW] payload: ", string, "\n\n")

    def MQTTconnect(self):
        print("[Client MQTT] Client try connect to broker...")

        self.client = MQTTClient(
            self.mqtt_id, self.mqtt_host, self.mqtt_port, keepalive=20)
        self.client.set_callback(self.MQTTCallBack)
        try:
            if(self.client.connect()):
                self.flagClientCon = True
                print("[Client MQTT] The Client is connect to broker!")
                # self.MQTTsubs()
        except:
            print("[Client MQTT] Error in connection client to broker")

    def resetMachine(self):
        print("[resetMachine] Threads was stoped, continue with reset")
        with open('./data.json', 'w') as f:
            try:
                f.write(self.jsonGod)
                print("[resetMachine] writed data in data.json.")
            except:
                f.close()
        print("[resetMachine] reseting...")
        utime.sleep(5)

        print(self.json_broker)
        print(self.jsonGod)
        soft_reset()

    def stop(self):
        self.flagStop_ths = True

        while not (self.flagBroker_th0 and self.flagBroker_th1):
            pass

        self.flagStop_ths = False
        return True

    # Thread 0 = Control and monitoring sensor and publish.
    # Thread 1 = Recived sms from broker.
    def thread0(self):
        print("[Thread 0] Start thread!")
        print("[Thread 0] ID = ", _thread.get_ident())

        while True:
            if self.flagStop_ths:
                self.flagBroker_th0 = True
                print("[Thread 0] Exit thread 0!")
                _thread.exit()

            try:
                while not self.getBPM280():
                    pass
                # print("[Thread 0] Measure is realized")
            except Exception as e:
                print("[Thread 0] Error:", e)
                self.flagErrorTh0 = True

            finally:
                # Contador numero de JSON enviados.
                self.jsons_send += 1

                # creacion JSON.
                self.json_broker = {
                    "id": self.jsons_send,
                    "Temp": self.temp,
                    "Hum": self.hum,
                    "logESP": {
                        "verifyReset": False
                    }
                }

                # convierte un Obj Python a JSON string para poder ser enviada.
                self.jsonGod = ujson.dumps(self.json_broker)

                try:
                    self.client.publish(self.topicx, self.jsonGod)
                    print("~~ Publish #", self.jsons_send, "-> ", self.jsonGod)
                except:
                    print("Wait for republish...")
                    utime.sleep(5)
                    print("[Thread 0] Error to publish JSON ID: ",
                    self.jsons_send, "Trying to publish now...")
                    self.client.publish(self.topicx, self.jsonGod)
                    self.flagErrorTh0 = True
                    self.flagBroker_th0 = True
                    _thread.exit()

    def thread1(self):
        print("[Thread 1] Start thread!")
        print("[Thread 1] ID = ", _thread.get_ident())
        while True:
            if self.flagStop_ths:
                self.flagBroker_th1 = True
                print("[Thread 1] Exit thread 1!")
                _thread.exit()

            try:
                self.client.check_msg()
                utime.sleep(1)

            except:
                print(
                    "[Thread 1] Error in check to new message, trying to check now...")
                try:
                    utime.sleep(1)
                    self.client.check_msg()
                except:
                    self.flagErrorTh1 = True
                    self.flagBroker_th1 = True
                    print('[Thread 1] The thread is stoped for errors...')
                    _thread.exit()

    def monitorThreads(self):
        print("[Monitor] The monitor is initialized!")
        while True:
            if self.flagErrorTh0 or self.flagErrorTh1:
                self.flagStop_ths = True
                print('[Monitor] Stop the threads...')
                while not (self.flagBroker_th1 and self.flagBroker_th0):
                    pass

                print("[Monitor] wait 3 seconds for no erros with threads")
                utime.sleep(3)
                self.resetMachine()
            
            if self.stopPin.value():
                self.timeStop = 0
                while True:
                    if self.timeStop == 5:
                        if self.stop():
                            print("[Monitor the ESP32 is stopped total.]")
                            sys.exit()
                             
                    if self.stopPin.value():
                        self.timeStop += 1
                        utime.sleep(1)

    def Run(self):
        _thread.start_new_thread(self.thread1, ())
        _thread.start_new_thread(self.thread0, ())
        self.monitorThreads()


# Start program!
station = WeatherStation()
station.MQTTconnect()
station.Run()


