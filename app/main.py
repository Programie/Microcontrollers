import uasyncio as asyncio

import config

from wlan import WLAN
from mqtt import MQTT

async def main():
    wlan = WLAN(config.WLAN_SSID, config.WLAN_PASSWORD)
    mqtt = MQTT(config.MQTT_HOST, config.MQTT_USERNAME, config.MQTT_PASSWORD)

    await wlan.connect()
    await mqtt.connect()

    asyncio.create_task(wlan.loop())
    asyncio.create_task(mqtt.loop())

    # main loop
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
