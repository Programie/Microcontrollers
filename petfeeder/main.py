import uasyncio as asyncio

import config as config

from common.wlan import WLAN
from common.mqtt import MQTT, QOS_AT_LEAST_ONCE
from common.utils import ButtonHandler, PinManager

PIN_MOTOR_RELAY = 16
PIN_MOTOR_SWITCH = 17
PIN_MANUAL_FEED_BUTTON = 13


class App:
    def __init__(self):
        self.pin_manager = PinManager()
        self.manual_feed_button_handler = ButtonHandler(callback_released=self.trigger_feed)
        self.motor_switch_handler = ButtonHandler(callback_released=self.stop_motor)

    def trigger_feed(self):
        self.pin_manager.on(PIN_MOTOR_RELAY)

    def stop_motor(self):
        self.pin_manager.off(PIN_MOTOR_RELAY)

    async def async_main_task(self):
        wlan = WLAN(config.WLAN_SSID, config.WLAN_PASSWORD)
        mqtt = MQTT(config.MQTT_HOST, config.MQTT_USERNAME, config.MQTT_PASSWORD)

        await wlan.connect()
        await mqtt.connect()

        mqtt.subscribe(config.MQTT_TOPIC_TRIGGER_FEED, lambda topic, message: self.trigger_feed(), QOS_AT_LEAST_ONCE)

        asyncio.create_task(wlan.loop())
        asyncio.create_task(mqtt.loop())
        asyncio.create_task(mqtt.process_message_queue())

        # Main loop sleeping for 10 ms to keep tasks responsive
        while True:
            await asyncio.sleep(0.01)

    def main(self):
        self.manual_feed_button_handler.register_irq(PIN_MANUAL_FEED_BUTTON)
        self.motor_switch_handler.register_irq(PIN_MOTOR_SWITCH)

        asyncio.run(self.async_main_task())


if __name__ == "__main__":
    App().main()
