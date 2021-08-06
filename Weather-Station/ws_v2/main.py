import utime
from machine import unique_id
import ubinascii
import ujson
import _thread
import MQTT
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
        self.mqtt_topics_sub = [
            b'fDWsZDAVg7/ESP32_RGB/MODE', b'fDWsZDAVg7/ESP32/JSINF']
        self.mqtt_topics_pub = [b'fDWsZDAVg7/ESP32_RGB/response']

    def _MQTTCallBack(self, topic, string):
        pass

    def MQTTconnect(self):
        print("[Client MQTT] Client try connect to broker...")

        self.client = MQTT.MQTTClient(
            self.mqtt_id, self.mqtt_host, self.mqtt_port)
        self.client.set_callback(self.MQTTCallBack)
        try:
            print(self.client.connect())
        except:
            print("[Client MQTT] Error to connect client to broker")

        print("[Client MQTT] The Client is connect to broker!")
        self.MQTTsubs()

        return True

    def MQTTpubluish(self, topic, string):
        self.client.publish(topic, string)

    # Thread 0 = Control and monitoring sensor and publish.
    # Thread 1 = Recived sms from broker.
    def _thread0(self):
        print("[Thread 0] Start thread!")

        cont_data = 0
        while True:
            utime.sleep(1)
            self.dht11.measure()

            self.temp = sensor.temperature()
            self.hum = sensor.humidity()

            self.cont_data += 1
            self.data_broker =
            {
                "id": self.cont_data,
                "Temp": self.temp,
                "Hum": self.hum
            }

            self.data_broker = ujson.dumps(self.data_broker)
            self.client.publish(self.data_broker)

    def _thread1(self):
        print("[Thread 1] Start thread!")
        
        self.interval_ping = 30
        self.smstime = 0
            
        while True:
            if ((utime.time() - self.smstime) > self.interval):
                self.client.ping()
                self.smstime = utime.time()
                
            self.client.check_msg()


    def Run(self):
        _thread.start_new_thread(self.thread0, ())
        _thread.start_new_thread(self.thread1, ())


# Start program!
station = WeatherStation(pinDHT11=pins["DHT11"])
if station.MQTTconnect():
    station.Run()
