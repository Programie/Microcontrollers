import uasyncio as asyncio
from umqtt.simple import MQTTClient

QOS_FIRE_AND_FORGET = 0
QOS_AT_LEAST_ONCE = 1
# QOS_ONLY_ONCE = 2 # Not supported in umqtt


class Subscription:
    def __init__(self, callback, qos: int = QOS_FIRE_AND_FORGET):
        self.callback = callback
        self.qos = qos


class QueueItem:
    def __init__(self, topic: str, message: str):
        self.topic = topic
        self.message = message


class MQTT:
    def __init__(self, host: str, username: str, password: str) -> None:
        self.client = MQTTClient(server=host, user=username, password=password, client_id=username, keepalive=60)

        self.lwt_topic = f"tele/{username}/LWT"
        self.topics: dict[str, Subscription] = {}
        self.callback = None
        self.message_queue = []

        self.client.set_last_will(topic=self.lwt_topic, msg="Offline", retain=True)

    async def connect(self) -> bool:
        try:
            print("Connecting to MQTT")
            self.client.connect(clean_session=False)
            print("MQTT connected")

            self.client.set_callback(self.on_message)

            for topic in self.topics.keys():
                self.register_subscription(topic)

            self.client.publish(topic=self.lwt_topic, msg="Online", retain=True)

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

    def publish(self, topic: str, message: str, retain: bool = False, qos: int = QOS_FIRE_AND_FORGET):
        self.client.publish(topic, message, retain=retain, qos=qos)

    def subscribe(self, topic: str, callback=None, qos: int = 0):
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

        self.message_queue.append(QueueItem(topic, message))

    def set_callback(self, callback):
        self.callback = callback

    def get_next_queue_item(self) -> QueueItem | None:
        if not self.message_queue:
            return None

        return self.message_queue.pop(0)

    async def process_message_queue(self):
        while True:
            queue_item = self.get_next_queue_item()
            if not queue_item:
                await asyncio.sleep(0.5)
                continue

            topic = queue_item.topic
            message = queue_item.message

            if topic in self.topics:
                self.topics[topic].callback(topic, message)

            if self.callback:
                self.callback(topic, message)
