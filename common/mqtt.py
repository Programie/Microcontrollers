import uasyncio as asyncio
from umqtt.simple import MQTTClient

QOS_FIRE_AND_FORGET = 0
QOS_AT_LEAST_ONCE = 1
#QOS_ONLY_ONCE = 2 # Not supported in umqtt

class Subscription:
    def __init__(self, callback, qos: int = QOS_FIRE_AND_FORGET):
        self.callback = callback
        self.qos = qos

class MQTT:
    def __init__(self, host: str, username: str, password: str) -> None:
        self.client = MQTTClient(server=host, user=username, password=password, client_id=username)

        self.topics: dict[str, Subscription] = {}
        self.callback = None

    async def connect(self) -> bool:
        try:
            self.client.connect(clean_session=False)
            print("MQTT connected")

            self.client.set_callback(self.on_message)

            for topic in self.topics.keys():
                self.register_subscription(topic)

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

    def subscribe(self, topic: str, callback = None, qos: int = 0):
        self.topics[topic] = Subscription(callback=callback, qos=qos)

        self.register_subscription(topic)

    def register_subscription(self, topic: str):
        if topic not in self.topics:
            return

        qos = self.topics[topic].qos

        print(f"Subscribing to MQTT topic '{topic}' with QoS {qos}")

        try:
            self.client.subscribe(topic, qos=qos)
        except Exception as exception:
            print("Unable to subscribe to MQTT topic:", exception)

    def on_message(self, topic_bytes: bytes, message_bytes: bytes):
        topic = topic_bytes.decode("utf-8")
        message = message_bytes.decode("utf-8")

        if topic in self.topics:
            self.topics[topic].callback(topic, message)

        if self.callback:
            self.callback(topic, message)

    def set_callback(self, callback):
        self.callback = callback
