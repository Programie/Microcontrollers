import uasyncio as asyncio
from umqtt.simple import MQTTClient

class MQTT:
    def __init__(self, host: str, username: str, password: str) -> None:
        self.client = MQTTClient(server=host, user=username, password=password, client_id=username)

        self.topics = set()

    async def connect(self) -> bool:
        try:
            self.client.connect()
            print("MQTT connected")

            for topic in self.topics:
                print("Subscribing to MQTT topic:", topic)
                self.client.subscribe(topic)

            return True
        except Exception as exception:
            print("MQTT connection failed:", exception)
            return False

    async def loop(self):
        while True:
            try:
                for _ in range(100):
                    self.client.check_msg()
                    await asyncio.sleep(0.1)
            except Exception as exception:
                print("Error while handling message:", exception)

            try:
                self.client.ping()
                await asyncio.sleep(0.1)
            except Exception as exception:
                print("MQTT connection lost, trying to reconnect...", exception)
                await self.connect()
                await asyncio.sleep(1)

    async def subscribe(self, topic: str):
        print("Subscribing to MQTT topic:", topic)

        self.topics.add(topic)
        self.client.subscribe(topic)

    async def set_callback(self, callback):
        self.client.set_callback(lambda topic, message: callback(topic.decode("utf-8"), message.decode("utf-8")))
