import json
from typing import Dict
import sensor_simulator


def encode_json(payload: Dict) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def decode_json(data: bytes) -> Dict:
    return json.loads(data.decode("utf-8"))


def encode_compact(payload: Dict) -> bytes:

    # Extract and validate fields
    try:
        temp = float(payload["temperatura"])  # degrees Celsius
        hum = int(payload["humedad"])  # percent
        wind = str(payload["direccion_viento"])  # direction code
    except Exception as e:
        raise ValueError("Payload must contain temperatura, humedad, direccion_viento") from e

    # Clamp ranges
    if temp < 0.0:
        temp = 0.0
    if temp > 110.0:
        temp = 110.0
    if hum < 0:
        hum = 0
    if hum > 100:
        hum = 100

    # map wind direction to index
    try:
        wind_idx = sensor_simulator.WIND_DIRECTIONS.index(wind)
    except ValueError:
        raise ValueError(f"Unknown wind direction '{wind}'")

    # scale temperature to two decimals
    temp_scaled = int(round(temp * 100))
    if temp_scaled >= (1 << 14):
        raise ValueError("Scaled temperature does not fit in 14 bits")

    if hum >= (1 << 7):
        raise ValueError("Humidity does not fit in 7 bits")

    # pack bits: [temp_scaled (14 bits)] [hum (7 bits)] [wind_idx (3 bits)]
    combined = (temp_scaled << 10) | (hum << 3) | (wind_idx & 0x7)

    return combined.to_bytes(3, byteorder="big")


def decode_compact(data: bytes) -> Dict:
 
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError("data must be bytes")
    if len(data) != 3:
        raise ValueError("Compact data must be exactly 3 bytes long")

    combined = int.from_bytes(data, byteorder="big")

    wind_idx = combined & 0x7
    hum = (combined >> 3) & 0x7F
    temp_scaled = combined >> 10  # remaining top 14 bits

    if wind_idx >= len(sensor_simulator.WIND_DIRECTIONS):
        raise ValueError("Decoded wind index out of range")

    temp = temp_scaled / 100.0

    return {"temperatura": round(temp, 2), "humedad": int(hum), "direccion_viento": sensor_simulator.WIND_DIRECTIONS[wind_idx]}
