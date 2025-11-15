import argparse
import json
import random
import signal
import sys
import time
from typing import Any

from kafka import KafkaProducer

import sensor_simulator
import encoder


STOP = False


def handle_sigterm(signum, frame):
    global STOP
    STOP = True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True, help="Kafka topic to publish to")
    parser.add_argument("--bootstrap", default="iot.redesuvg.cloud:9092", help="Bootstrap server")
    parser.add_argument("--mode", choices=["json", "compact"], default="json")
    parser.add_argument("--min-interval", type=int, default=15)
    parser.add_argument("--max-interval", type=int, default=30)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    if args.mode == "json":
        producer = KafkaProducer(
            bootstrap_servers=[args.bootstrap],
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
        )
    else:
        # compact mode: serializer expects raw bytes from encoder.encode_compact
        producer = KafkaProducer(bootstrap_servers=[args.bootstrap], value_serializer=lambda v: v)

    print(f"Connecting to Kafka at {args.bootstrap}, topic={args.topic}, mode={args.mode}")

    try:
        while not STOP:
            reading = sensor_simulator.generate_reading()
            if args.mode == "json":
                value = reading
            else:
                # will raise if encoder.encode_compact fails
                value = encoder.encode_compact(reading)

            # send (key can be None or sensor id)
            producer.send(args.topic, value=value)
            producer.flush()
            print(f"Sent: {reading}")

            interval = random.uniform(args.min_interval, args.max_interval)
            # sleep in small increments so SIGINT can stop faster
            slept = 0.0
            while slept < interval and not STOP:
                time.sleep(0.5)
                slept += 0.5

    finally:
        try:
            producer.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
