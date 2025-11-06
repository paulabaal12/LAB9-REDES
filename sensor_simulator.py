import random
from typing import Dict
import numpy as np

WIND_DIRECTIONS = ["N", "NO", "O", "SO", "S", "SE", "E", "NE"]


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def generate_reading(
    temp_mean: float = 25.0,
    temp_std: float = 5.0,
    hum_mean: float = 50.0,
    hum_std: float = 10.0,
    seed: int | None = None,
) -> Dict:

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)

    # Temperature: gaussian, clamp to [0,110], round to 2 decimals
    temp = float(np.random.normal(loc=temp_mean, scale=temp_std))
    temp = clamp(temp, 0.0, 110.0)
    temp = round(temp, 2)

    # Humidity: gaussian, clamp to [0,100], integer
    hum = float(np.random.normal(loc=hum_mean, scale=hum_std))
    hum = clamp(hum, 0.0, 100.0)
    hum = int(round(hum))

    # Wind direction: uniform choice
    wind = random.choice(WIND_DIRECTIONS)

    return {"temperatura": temp, "humedad": hum, "direccion_viento": wind}


if __name__ == "__main__":
    # Quick demo: print 5 sample readings
    for i in range(5):
        r = generate_reading(seed=i)
        print(r)
