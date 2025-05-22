import uasyncio as asyncio
from umqtt.simple import MQTTClient

class MQTT(MQTTClient):
    def __init__(self, host: str, username: str, password: str) -> None:
        super().__init__(server=host, user=username, password=password, client_id=username)

    async def connect(self) -> bool:
        try:
            super().connect()
            print("MQTT connected")
            return True
        except Exception as exception:
            print("MQTT connection failed:", exception)
            return False

    async def loop(self):
        while True:
            try:
                self.ping()
            except Exception as exception:
                print("MQTT connection lost, trying to reconnect...", exception)
                await self.connect()

            await asyncio.sleep(5)
