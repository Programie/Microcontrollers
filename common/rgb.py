import uasyncio as asyncio

from machine import Pin, PWM


class Channel:
    def __init__(self, port: int):
        self.pwm = PWM(Pin(port), freq=1000)
        self.value = 0

        # Force off on init
        self.pwm.duty(0)

    def set_value(self, value: int):
        self.value = value
        self.pwm.duty(value)

    def fade_to_step(self, old_value: int, new_value: int, current_step: int, steps: int):
        self.set_value(round(old_value + (new_value - old_value) * current_step / steps))


class Fader:
    def __init__(self, red_port: int, green_port: int, blue_port: int, delay: float):
        self.red = Channel(red_port)
        self.green = Channel(green_port)
        self.blue = Channel(blue_port)

        self.delay = delay

        self.fading_active = False

    def set_color(self, red: int, green: int, blue: int):
        self.red.set_value(red)
        self.green.set_value(green)
        self.blue.set_value(blue)

    async def fade_to(self, red: int = 0, green: int = 0, blue: int = 0, check_fading_active: bool = True):
        red_value = self.red.value
        green_value = self.green.value
        blue_value = self.blue.value

        steps = max(abs(red_value - red), abs(green_value - green), abs(blue_value - blue))

        for value in range(steps + 1):
            if check_fading_active and not self.fading_active:
                return

            self.red.fade_to_step(red_value, red, value, steps)
            self.green.fade_to_step(green_value, green, value, steps)
            self.blue.fade_to_step(blue_value, blue, value, steps)

            await asyncio.sleep(self.delay)

        self.set_color(red, green, blue)

    async def fade(self):
        self.fading_active = True

        await self.fade_to(red=1023)

        while self.fading_active:
            await self.fade_to(green=1023)
            await self.fade_to(blue=1023)
            await self.fade_to(red=1023)

        await self.fade_to(check_fading_active=False)

        self.fading_active = False

    def stop(self):
        self.fading_active = False
