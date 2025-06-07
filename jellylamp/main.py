import json
import uasyncio as asyncio

import config as config

from common.wlan import WLAN
from common.mqtt import MQTT, QOS_AT_LEAST_ONCE
from common.rgb import Fader
from common.utils import PinManager

PIN_LED_GREEN = 16
PIN_LED_RED = 17
PIN_LED_BLUE = 18
PIN_PUMP = 19


class App:
    def __init__(self):
        self.rgb_fader = Fader(PIN_LED_RED, PIN_LED_GREEN, PIN_LED_BLUE)
        self.pin_manager = PinManager()

        self.mqtt = MQTT(config.MQTT_HOST, config.MQTT_USERNAME, config.MQTT_PASSWORD)

        self.rgb_fader_task = None

    async def async_main_task(self):
        wlan = WLAN(config.WLAN_SSID, config.WLAN_PASSWORD)

        await wlan.connect()
        await self.mqtt.connect()

        self.mqtt.subscribe(config.MQTT_TOPIC_CONTROL, self.handle_message, QOS_AT_LEAST_ONCE)

        asyncio.create_task(wlan.loop())
        asyncio.create_task(self.mqtt.loop())

        # Main loop sleeping for 10 ms to keep tasks responsive
        while True:
            await asyncio.sleep(0.01)

    def handle_message(self, topic: str, message: str):
        try:
            data = json.loads(message)
        except json.JSONDecodeError as error:
            print(error)
            return

        state = data.get("state")
        if state is None:
            print("State not specified!")
            return

        state = state.lower()

        if state == "on":
            self.power_on(data)
        elif state == "off":
            self.power_off(data)
        elif state == "fade_to":
            self.fade_to(data)
        elif state == "pump_on":
            self.pin_manager.on(PIN_PUMP)
        elif state == "pump_off":
            self.pin_manager.off(PIN_PUMP)
        else:
            print(f"Invalid state: {state}")

    def power_on(self, data: dict):
        if self.rgb_fader_task and not self.rgb_fader_task.done():
            try:
                self.rgb_fader_task.cancel()
            except RuntimeError:
                # Ignore RuntimeError (can't cancel self) raised in some cases
                pass

        fade_in = data.get("fadeIn", {})
        fade = data.get("fade", {})
        fade_out = data.get("fadeOut", {})

        fade_steps = fade.get("steps", 1)
        fade_delay = fade.get("delay", 0.02)

        self.rgb_fader_task = asyncio.create_task(self.rgb_fader.fade(
            fade_in_steps=fade_in.get("steps", fade_steps),
            fade_in_delay=fade_in.get("delay", fade_delay),
            fade_steps=fade_steps,
            fade_delay=fade_delay,
            fade_out_steps=fade_out.get("steps", fade_steps),
            fade_out_delay=fade_out.get("delay", fade_delay)
        ))
        self.pin_manager.on(PIN_PUMP)

    def power_off(self, data: dict):
        self.rgb_fader.stop()
        self.pin_manager.off(PIN_PUMP)

    def fade_to(self, data: dict):
        if self.rgb_fader_task and not self.rgb_fader_task.done():
            try:
                self.rgb_fader_task.cancel()
            except RuntimeError:
                # Ignore RuntimeError (can't cancel self) raised in some cases
                pass

        self.rgb_fader_task = asyncio.create_task(self.fade_to_wait(data))

    async def fade_to_wait(self, data: dict):
        self.rgb_fader.fading_active = True

        await self.rgb_fader.fade_to(
            red=data.get("red", 0),
            green=data.get("green", 0),
            blue=data.get("blue", 0),
            values_per_step=data.get("steps", 1),
            delay=data.get("delay", 0.02),
        )

        self.rgb_fader.fading_active = False

        self.mqtt.publish(config.MQTT_TOPIC_CALLBACK, json.dumps({
            "id": data.get("id"),
            "name": "fade_to_finished"
        }))

    def main(self):
        asyncio.run(self.async_main_task())


if __name__ == "__main__":
    App().main()
