import requests
import random
import time

URL = "http://13.219.254.20/weather"

device_id = "hostel"

while True:

    temperature = round(random.uniform(25, 42), 2)
    humidity = round(random.uniform(50, 95), 2)

    response = requests.post(
        URL,
        params={
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity
        }
    )

    print("Hostel Sensor:", response.json())

    time.sleep(7)