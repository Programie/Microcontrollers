import uasyncio as asyncio

import config as config

from common.wlan import WLAN
from common.mqtt import MQTT
from common.utils import PinManager

class App:
    def __init__(self):
        self.pin_manager = PinManager()

    def handle_mqtt_message(self, topic: str, message: str):
        try:
            port = int(topic.split("/")[2])
        except Exception as exception:
            print(f"Unable to parse port from topic '{topic}':", exception)
            return

        message_parts = message.split()
        if not message_parts:
            print(f"Missing message for topic '{topic}'")
            return

        action = message_parts[0]

        if action == "on":
            self.pin_manager.on(port)
        elif action == "off":
            self.pin_manager.off(port)
        elif action == "impulse":
            if len(message_parts) >= 2:
                try:
                    duration = float(message_parts[1])
                except Exception as exception:
                    print(f"Unable to parse duration from message '{message}':", exception)
                    return

                asyncio.create_task(self.pin_manager.impulse(port, duration))
        else:
            print(f"Invalid action '{action}'")

    async def main(self):
        wlan = WLAN(config.WLAN_SSID, config.WLAN_PASSWORD)
        mqtt = MQTT(config.MQTT_HOST, config.MQTT_USERNAME, config.MQTT_PASSWORD)

        await wlan.connect()
        await mqtt.connect()

        await mqtt.set_callback(self.handle_mqtt_message)
        await mqtt.subscribe(config.MQTT_TOPIC)

        asyncio.create_task(wlan.loop())
        asyncio.create_task(mqtt.loop())

        # main loop
        while True:
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(App().main())
