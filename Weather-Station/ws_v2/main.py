import utime
from machine import unique_id
import ubinascii
import ujson
import _thread
from umqtt.simple2 import MQTTClient
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
        self.cont_send = 0
        self.topicx = b'tempTabogo/DHT11'
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

    def reconBroker(self):
        try:
            while not (self.flagBroker_th1 and self.flagBroker_th0):
                print("[RECON] Wait for close all threads!")
                pass

            # reinitialize flags.
            self.flagStop_ths = False
            self.flagBrokerError_ths = False
            self.flagBroker_th0 = False
            self.flagBroker_th1 = False
            self.flagClientCon = False

            # reconnection
            del self.client
            self.MQTTconnect()
            if self.flagClientCon:
                print("[RECON] Success full connect to broker! Running program...")
                self.Run()
        except:
            print("[RECON] Error in reconnection to Broker")
        
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
        print("[Thread 1] ID = ", _thread.get_ident())

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

            self.cont_send += 1
            self.json_broker = {
                "id": self.cont_send,
                "Temp": self.temp,
                "Hum": self.hum
            }

            self.json_broker = ujson.dumps(self.json_broker)
            try:
                self.client.publish(self.topicx, self.json_broker)
                print(self.json_broker)
            except:
                if not self.flagBrokerError_ths:
                    self.flagBrokerError_ths = True
                    print("[Thread 0] Error in publish JSON DATA to broker, posible errors in connection.")
                    print("[Thread 0] Trying new connection to Broker server")
                    self.flagBroker_th0 = True
                    self.flagStop_ths = True
                    print("[Thread 0] Exit thread 0!")
                    _thread.exit()
                else:
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
            except:
                if not self.flagBrokerError_ths:
                    self.flagBrokerError_ths = True
                    print('[Thread 1] Error to check new sms from broker, posible error in connection')
                    print('[Thread 1] Trying new connection to Broker server.')
                    self.flagBroker_th1 = True
                    self.flagStop_ths = True
                    print("[Thread 1] Exit thread 1!")
                    _thread.exit()
                else:
                    continue
    
    def monitor(self):
        print("[Monitor] The monitor is initialized!")
        while True:
            if self.flagBroker_th1 or self.flagBroker_th0 or self.flagStop_ths: 
                print("[Monitor] Detected error in threads, processing with reconnection to broker")
                self.reconBroker()
                
            if self.stop_pin.value() == 1:
                utime.sleep(2)
                if self.stop():
                    print("[STOP] The ESP32 is total stoped!")
                    break
                
    def Run(self):
        _thread.start_new_thread(self.thread1, ())
        _thread.start_new_thread(self.thread0, ())
        self.monitor()


# Start program!
station = WeatherStation(pinDHT11=pins["DHT11"])
station.MQTTconnect()
station.Run()
