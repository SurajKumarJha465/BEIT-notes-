import requests
import random
import time

URL = "http://13.219.254.20/weather"

device_id = "lab_room"

while True:

    temperature = round(random.uniform(20, 40), 2)
    humidity = round(random.uniform(40, 90), 2)

    response = requests.post(
        URL,
        params={
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity
        }
    )

    print(response.json())

    time.sleep(5)