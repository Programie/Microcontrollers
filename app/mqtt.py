from umqtt.simple import MQTTClient

class MQTT(MQTTClient):
    def __init__(self, host: str, username: str, password: str) -> None:
        super().__init__(server=host, user=username, password=password, client_id=username)

    def connect(self) -> bool:
        try:
            super().connect()
            return True
        except Exception as exeption:
            return False

    def is_connected(self) -> bool:
        try:
            self.ping()
            return True
        except Exception as exception:
            return False
