import argparse
import signal
import sys
import time
from collections import deque

import matplotlib.pyplot as plt
from kafka import KafkaConsumer

import encoder
import sensor_simulator


STOP = False


def handle_sigterm(signum, frame):
    global STOP
    STOP = True


def make_consumer(topic: str, bootstrap: str, group: str, mode: str) -> KafkaConsumer:
    if mode == "json":
        return KafkaConsumer(
            topic,
            bootstrap_servers=[bootstrap],
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id=group,
            value_deserializer=lambda b: encoder.decode_json(b),
            consumer_timeout_ms=1000,
        )
    else:
        # compact mode: receive raw bytes and decode later
        return KafkaConsumer(
            topic,
            bootstrap_servers=[bootstrap],
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id=group,
            value_deserializer=lambda b: b,
            consumer_timeout_ms=1000,
        )


def run_plot(topic: str, bootstrap: str, group: str, mode: str):
    consumer = make_consumer(topic, bootstrap, group, mode)

    # Data buffers
    times = deque(maxlen=200)
    temps = deque(maxlen=200)
    hums = deque(maxlen=200)
    winds = deque(maxlen=200)

    # map wind categories to integers for plotting
    wind_categories = {d: i for i, d in enumerate(sensor_simulator.WIND_DIRECTIONS)}

    plt.ion()
    fig, axes = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    ax_t, ax_h, ax_w = axes

    ax_t.set_ylabel("Temperatura (°C)")
    ax_h.set_ylabel("Humedad (%)")
    ax_w.set_ylabel("Direccion (index)")
    ax_w.set_yticks(list(wind_categories.values()))
    ax_w.set_yticklabels(list(wind_categories.keys()))

    ax_t.grid(True)
    ax_h.grid(True)
    ax_w.grid(True)

    print(f"Listening to {topic} at {bootstrap} (mode={mode})")

    try:
        while not STOP:
            # poll for records (non-blocking up to consumer_timeout_ms)
            records = consumer.poll(timeout_ms=1000)
            got = False
            for tp, msgs in records.items():
                for msg in msgs:
                    got = True
                    raw = msg.value
                    if mode == "json":
                        payload = raw
                    else:
                        try:
                            payload = encoder.decode_compact(raw)
                        except Exception as e:
                            print("Failed to decode compact payload:", e)
                            continue

                    # debug print for received payloads (helps verify ingestion)
                    print("Received:", payload)

                    ts = time.time()
                    times.append(ts)
                    temps.append(float(payload.get("temperatura", 0)))
                    hums.append(int(payload.get("humedad", 0)))
                    winds.append(payload.get("direccion_viento", "?"))

            # update plots if we received data or periodically
            if got or len(times) > 0:
                ax_t.clear(); ax_h.clear(); ax_w.clear()
                ax_t.plot(list(times), list(temps), '-o', color='tab:red')
                ax_h.plot(list(times), list(hums), '-s', color='tab:blue')
                # map wind categories to ints
                wind_idxs = [wind_categories.get(w, -1) for w in winds]
                ax_w.scatter(list(times), wind_idxs, c='tab:green')

                ax_t.set_ylabel("Temperatura (°C)")
                ax_h.set_ylabel("Humedad (%)")
                ax_w.set_ylabel("Direccion (index)")
                ax_w.set_yticks(list(wind_categories.values()))
                ax_w.set_yticklabels(list(wind_categories.keys()))

                # format x axis as relative time (avoid singular limits)
                if len(times) > 0:
                    t0 = times[0]
                    ax_w.set_xlabel("t (s)")
                    if len(times) > 1 and times[-1] > t0:
                        ax_t.set_xlim(t0, times[-1])
                    else:
                        # small padding when only a single sample exists
                        ax_t.set_xlim(t0 - 1.0, t0 + 1.0)

                plt.pause(0.01)

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        try:
            consumer.close()
        except Exception:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--bootstrap", default="164.92.76.15:9092")
    parser.add_argument("--mode", choices=["json", "compact"], default="json")
    parser.add_argument("--group", default="lab9-plot-group")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    run_plot(args.topic, args.bootstrap, args.group, args.mode)


if __name__ == "__main__":
    main()
