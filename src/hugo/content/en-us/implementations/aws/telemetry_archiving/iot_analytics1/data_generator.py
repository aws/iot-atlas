#!/usr/bin/env python3

import random
import time
import boto3
import json
from multiprocessing import Pool
from datetime import datetime


iot_client = boto3.client(
    "iot-data", endpoint_url="a25fj3umhflvxq-ats.iot.us-east-1.amazonaws.com"
)


def read(sensor):
    message = {}
    message["device_id"] = f"sensor{sensor}"
    message["temperature"] = random.randrange(45, 92, 2)
    message["humidity"] = random.randrange(0, 100, 2)
    message["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(message)

    topic = f"dt/{message['device_id']}/aggregate"
    iot_client.publish(topic=topic, payload=json.dumps(message))


if __name__ == "__main__":
    sensor_count = 5  # maps to physical threads on your machine
    seconds_between_publishing = 10
    publishes = 10

    with Pool(sensor_count) as p:
        for _ in range(publishes):
            p.map(read, range(sensor_count))
            time.sleep(seconds_between_publishing)
