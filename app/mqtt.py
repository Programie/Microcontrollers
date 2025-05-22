import uasyncio as asyncio
from umqtt.simple import MQTTClient

class MQTT:
    def __init__(self, host: str, username: str, password: str) -> None:
        self.client = MQTTClient(server=host, user=username, password=password, client_id=username)

        self.topic_callbacks = {}

        self.client.set_callback(lambda topic, message: self.on_message(topic.decode("utf-8"), message.decode("utf-8")))

    async def connect(self) -> bool:
        try:
            self.client.connect()
            print("MQTT connected")

            for topic in self.topic_callbacks.keys():
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

                self.client.ping()
                await asyncio.sleep(0.1)
            except Exception as exception:
                print("MQTT connection lost, trying to reconnect...", exception)
                await self.connect()
                await asyncio.sleep(1)

    async def subscribe(self, topic: str, callback):
        print("Subscribing to MQTT topic:", topic)

        self.topic_callbacks[topic] = callback
        self.client.subscribe(topic)

    def on_message(self, topic: str, message: str):
        if topic not in self.topic_callbacks:
            print("Received message for unknown MQTT topic:", topic)
            return

        self.topic_callbacks[topic](message)
