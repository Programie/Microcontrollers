import uasyncio as asyncio

from machine import Pin, PWM


class RGBFader:
    def __init__(self, red_port: int, green_port: int, blue_port: int, delay: float):
        self.red = PWM(Pin(red_port), freq=1000)
        self.green = PWM(Pin(green_port), freq=1000)
        self.blue = PWM(Pin(blue_port), freq=1000)

        self.delay = delay

        self.red_value = 0
        self.green_value = 0
        self.blue_value = 0

        self.fading_active = False

        # Force off on init
        self.set_color(0, 0, 0)

    def set_color(self, red: int, green: int, blue: int):
        self.red_value = red
        self.green_value = green
        self.blue_value = blue

        self.red.duty(red)
        self.green.duty(green)
        self.blue.duty(blue)

    async def fade_to(self, red: int = 0, green: int = 0, blue: int = 0, check_fading_active: bool = True):
        red_value = self.red_value
        green_value = self.green_value
        blue_value = self.blue_value

        steps = max(abs(red_value - red), abs(green_value - green), abs(blue_value - blue))

        for value in range(steps + 1):
            if check_fading_active and not self.fading_active:
                return

            red_color   = round(red_value   + (red   - red_value)   * value / steps)
            green_color = round(green_value + (green - green_value) * value / steps)
            blue_color  = round(blue_value  + (blue  - blue_value)  * value / steps)

            self.set_color(red_color, green_color, blue_color)
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


class PinManager:
    def __init__(self):
        self.pins = {}

    def get(self, port: int) -> Pin:
        if port not in self.pins:
            self.pins[port] = Pin(port, Pin.OUT)

        return self.pins[port]

    def on(self, port: int):
        self.get(port).on()

    def off(self, port: int):
        self.get(port).off()

    async def impulse(self, port: int, duration: float):
        pin = self.get(port)

        pin.on()
        await asyncio.sleep(duration)
        pin.off()


class ButtonHandler:
    def __init__(self, callback = None, callback_pressed = None, callback_released = None, delay = 0.1):
        self.old_state = None
        self.callback = callback
        self.callback_pressed = callback_pressed
        self.callback_released = callback_released
        self.delay = delay
        self.debounce_task = None

        self.event_loop = asyncio.get_event_loop()

    def register_irq(self, port: int):
        pin = Pin(port, Pin.IN, Pin.PULL_UP)

        self.old_state = not pin.value()

        pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.handler)

    async def handle_event(self, pressed: bool):
        if self.delay:
            try:
                await asyncio.sleep(self.delay)
            except asyncio.CancelledError:
                return

        if pressed:
            if self.callback_pressed:
                self.callback_pressed()
        else:
            if self.callback_released:
                self.callback_released()

        if self.callback:
            self.callback(pressed)

    def handler(self, pin: Pin):
        pressed = not pin.value()

        if pressed != self.old_state:
            self.old_state = pressed

            if self.debounce_task and not self.debounce_task.done():
                try:
                    self.debounce_task.cancel()
                except RuntimeError:
                    # Ignore RuntimeError (can't cancel self) raised in some cases
                    pass

            self.debounce_task = self.event_loop.create_task(self.handle_event(pressed))
