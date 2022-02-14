import utime
from machine import unique_id, soft_reset
import ubinascii
import ujson
import _thread
from lib.umqtt.simple2 import MQTTClient
global pins


class WeatherStation():
    def __init__(self, pinDHT11=None, pinDHT22=None):
        self.dht11 = pinDHT11
        self.dht22 = pinDHT22

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
        self.flagStop_ths = False
        self.flagBrokerError_ths = False
        self.flagClientCon = False

        #
        #     ~Thread 0 Propietys~
        #
        self.jsons_send = 0
        self.topicx = b 'tempTabogo/DHT11'
        self.sensor = self.dht11
        
        # probe pin for stop program.
        self.stop_pin = machine.Pin(18, machine.Pin.IN)

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
        
        self.client = MQTTClient(self.mqtt_id, self.mqtt_host, self.mqtt_port, keepalive=20)
        self.client.set_callback(self.MQTTCallBack)
        try:
            if(self.client.connect()):
                self.flagClientCon = True
                print("[Client MQTT] The Client is connect to broker!")
                # self.MQTTsubs()
        except:
            print("[Client MQTT] Error in connection client to broker")

    def resetMachine(self):
        self.flagStop_ths = True
        
        while not (self.flagBroker_th1 and self.flagBroker_th0):
            pass
        
        print("[resetMachine] Wait 3 seconds for not problems with threads...")
        utime.sleep(3)
        
        print("[resetMachine] Threads was stoped, continue with reset")
        json_file = open('./data.json', 'w')
        
        json_file.write(self.jsonGod)
        json_file.close()
        print("[resetMachine] Json of program is save in file data.json! reset...")
        
                

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
                utime.sleep(1)
                self.sensor.measure()
            except:
                print('[Thread 0] Error to read sensor, trying new read...')
                continue

            self.temp = self.sensor.temperature()
            self.hum = self.sensor.humidity()
            
            # Contador numero de JSON enviados.
            self.jsons_send += 1
            
            # creacion JSON.
            self.json_broker = {
                "id": self.jsons_send,
                "Temp": self.temp,
                "Hum": self.hum
            }
            
            # convierte un Obj Python a JSON string para poder ser enviada.
            self.jsonGod = ujson.dumps(self.json_broker)
            try:
                self.client.publish(self.topicx, self.jsonGod)
                print(self.json_broker)
            except:
                print("[Thread 0] Error to publish JSON ID: ", self.jsons_send, "Trying to publish now...")
                self.client.publish(self.topicx, self.json_broker)
                continue
                
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
                utime.sleep(0.5)
            except:
                print("[Thread 1] Error in check to new message, trying to check now...")
                try:
                    utime.sleep(1) 
                    self.client.check_msg()
                except:
                    print("[Thread 1] Error in new check, soft reset machine...")
                    self.flagBroker_th1 = True
                    self.resetMachine()
    
    def monitorThreads(self):
        print("[Monitor] The monitor is initialized!")
        while True:
            if self.stop_pin.value() == 1:
                utime.sleep(2)
                if self.stop():
                    print("[STOP] The ESP32 is total stoped!")
                    break
                
    def Run(self):
        _thread.start_new_thread(self.thread1, ())
        _thread.start_new_thread(self.thread0, ())
        self.monitorThreads()


# Start program!
station = WeatherStation(pinDHT11=pins["DHT11"])
station.MQTTconnect()
station.Run()
