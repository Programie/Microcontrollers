import network
import time

class WLAN:
    def __init__(self, ssid: str, password: str) -> None:
        self.ssid = ssid
        self.password = password

    def connect(self):
        wlan = network.WLAN(network.STA_IF)

        if not wlan.active():
            wlan.active(True)

        if not wlan.isconnected():
            wlan.connect(self.ssid, self.password)

            timeout = 10
            while not wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1

        if wlan.isconnected():
            return True
        else:
            return False

    def is_connected(self) -> bool:
        return network.WLAN(network.STA_IF).isconnected()
