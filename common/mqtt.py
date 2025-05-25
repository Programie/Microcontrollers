import uasyncio as asyncio
from umqtt.simple import MQTTClient

class MQTT:
    def __init__(self, host: str, username: str, password: str) -> None:
        self.client = MQTTClient(server=host, user=username, password=password, client_id=username)

        self.topics = set()
        self.topic_callbacks = {}
        self.callback = None

    async def connect(self) -> bool:
        try:
            self.client.connect()
            print("MQTT connected")

            self.client.set_callback(self.on_message)

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
                print("MQTT connection lost, trying to reconnect in 10 seconds...", exception)
                await asyncio.sleep(10)
                await self.connect()
                await asyncio.sleep(1)

    def subscribe(self, topic: str, callback = None):
        print("Subscribing to MQTT topic:", topic)

        if callback:
            self.topic_callbacks[topic] = callback

        self.topics.add(topic)

        try:
            self.client.subscribe(topic)
        except Exception as exception:
            print("Unable to subscribe to MQTT topic:", exception)

    def on_message(self, topic_bytes: bytes, message_bytes: bytes):
        topic = topic_bytes.decode("utf-8")
        message = message_bytes.decode("utf-8")

        if topic in self.topic_callbacks:
            self.topic_callbacks[topic](topic, message)

        if self.callback:
            self.callback(topic, message)

    def set_callback(self, callback):
        self.callback = callback
