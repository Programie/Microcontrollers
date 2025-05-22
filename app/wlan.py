import network
import uasyncio as asyncio

class WLAN:
    def __init__(self, ssid: str, password: str) -> None:
        self.ssid = ssid
        self.password = password

        self.wlan = network.WLAN(network.STA_IF)

    async def connect(self):
        if not self.wlan.active():
            self.wlan.active(True)

        if self.wlan.isconnected():
            return True

        self.wlan.connect(self.ssid, self.password)

        for _ in range(10):
            if self.wlan.isconnected():
                return True

            await asyncio.sleep(1)

        return False

    async def loop(self):
        while True:
            if not self.wlan.isconnected():
                await self.connect()

            await asyncio.sleep(5)
