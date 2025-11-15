import argparse
import json
import signal
import sys
from typing import List

from kafka import KafkaConsumer

import encoder


STOP = False


def handle_sigterm(signum, frame):
    global STOP
    STOP = True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--bootstrap", default="iot.redesuvg.cloud:9092")
    parser.add_argument("--mode", choices=["json", "compact"], default="json")
    parser.add_argument("--group", default="lab9-group")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    if args.mode == "json":
        consumer = KafkaConsumer(
            args.topic,
            bootstrap_servers=[args.bootstrap],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id=args.group,
            # for JSON mode we deserialize here
            value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        )
    else:
        # In compact mode we receive raw bytes and decode inside the loop
        consumer = KafkaConsumer(
            args.topic,
            bootstrap_servers=[args.bootstrap],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id=args.group,
            value_deserializer=lambda b: b,
        )

    temps: List[float] = []
    hums: List[int] = []
    winds: List[str] = []

    print(f"Listening to {args.topic} at {args.bootstrap} (mode={args.mode})")
    try:
        for msg in consumer:
            if STOP:
                break
            # msg.value may be bytes (compact) or already-deserialized JSON
            payload = msg.value
            if args.mode == "compact":
                # show raw bytes for evidence (hex) then decode
                try:
                    if isinstance(msg.value, (bytes, bytearray)):
                        print("Raw bytes:", msg.value.hex())
                except Exception:
                    pass
                try:
                    payload = encoder.decode_compact(msg.value)
                except Exception:
                    print("Warning: failed to decode compact payload; skipping")
                    continue
            print("Received:", payload)
            try:
                temps.append(float(payload.get("temperatura")))
                hums.append(int(payload.get("humedad")))
                winds.append(payload.get("direccion_viento"))
            except Exception:
                print("Warning: received payload missing expected keys")

    finally:
        try:
            consumer.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
