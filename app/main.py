import time

import config

from wlan import WLAN
from mqtt import MQTT

def main():
    wlan = WLAN(config.WLAN_SSID, config.WLAN_PASSWORD)
    mqtt = MQTT(config.MQTT_HOST, config.MQTT_USERNAME, config.MQTT_PASSWORD)

    while True:
        if wlan.is_connected():
            if not mqtt.is_connected():
                print("MQTT not connected, trying to connect...")
                if mqtt.connect():
                    print("MQTT connected")
                else:
                    print("MQTT connection failed!")
        else:
            print("WLAN not connected, trying to connect...")
            if wlan.connect():
                print("WLAN connected")
            else:
                print("WLAN connection failed!")

        time.sleep(10)

if __name__ == "__main__":
    main()
