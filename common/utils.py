import uasyncio as asyncio

from machine import Pin

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
    def __init__(self, callback = None, callback_pressed = None, callback_released = None):
        self.old_state = None
        self.callback = callback
        self.callback_pressed = callback_pressed
        self.callback_released = callback_released

    def register_irq(self, port: int):
        pin = Pin(port, Pin.IN, Pin.PULL_UP)

        self.old_state = not pin.value()

        pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.handler)

    def handler(self, pin: Pin):
        pressed = not pin.value()

        if pressed != self.old_state:
            self.old_state = pressed

            if pressed:
                if self.callback_pressed:
                    self.callback_pressed()
            else:
                if self.callback_released:
                    self.callback_released()

            if self.callback:
                self.callback()
