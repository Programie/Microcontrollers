import uasyncio as asyncio

import config as config

from common.wlan import WLAN
from common.mqtt import MQTT, QOS_AT_LEAST_ONCE
from common.rgb import Fader
from common.utils import PinManager

PIN_LED_RED = 16
PIN_LED_GREEN = 17
PIN_LED_BLUE = 18
PIN_PUMP = 19


class App:
    def __init__(self):
        self.rgb_fader = Fader(PIN_LED_RED, PIN_LED_GREEN, PIN_LED_BLUE, 0.02)
        self.pin_manager = PinManager()

        self.rgb_fader_task = None

    async def async_main_task(self):
        wlan = WLAN(config.WLAN_SSID, config.WLAN_PASSWORD)
        mqtt = MQTT(config.MQTT_HOST, config.MQTT_USERNAME, config.MQTT_PASSWORD)

        await wlan.connect()
        await mqtt.connect()

        mqtt.subscribe(config.MQTT_TOPIC_CONTROL, self.handle_message, QOS_AT_LEAST_ONCE)

        asyncio.create_task(wlan.loop())
        asyncio.create_task(mqtt.loop())

        # Main loop sleeping for 10 ms to keep tasks responsive
        while True:
            await asyncio.sleep(0.01)

    def handle_message(self, topic: str, message: str):
        if message == "on":
            self.power_on()
        elif message == "off":
            self.power_off()

    def power_on(self):
        if self.rgb_fader_task and not self.rgb_fader_task.done():
            try:
                self.rgb_fader_task.cancel()
            except RuntimeError:
                # Ignore RuntimeError (can't cancel self) raised in some cases
                pass

        self.rgb_fader_task = asyncio.create_task(self.rgb_fader.fade())
        self.pin_manager.on(PIN_PUMP)

    def power_off(self):
        self.rgb_fader.stop()
        self.pin_manager.off(PIN_PUMP)

    def main(self):
        asyncio.run(self.async_main_task())


if __name__ == "__main__":
    App().main()
