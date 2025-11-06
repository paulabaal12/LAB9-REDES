# Laboratorio 9
## IoT: Estación Meteorológica


Preparar entorno (PowerShell)

```powershell
cd D:\Documentos\GitHub\LAB9-REDES
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Levantar Kafka local (opcional, Docker Desktop requerido)

```powershell
docker-compose up -d
docker-compose logs -f kafka   # para seguir logs
```

Cómo ejecutar los scripts

- Ejecutar el Consumer (escucha y muestra lecturas):

```powershell
.\.venv\Scripts\Activate.ps1
python consumer.py --topic 12345678 --bootstrap localhost:9092 --mode json
```

- Ejecutar el Producer (envía lecturas periódicas):

```powershell
.\.venv\Scripts\Activate.ps1
python producer.py --topic 12345678 --bootstrap localhost:9092 --mode json
```

Parámetros importantes

- `--topic`: nombre del topic a usar; cada pareja debe usar un topic único (por ejemplo, el número de carné).
- `--bootstrap`: dirección del broker (por defecto en los scripts está `164.92.76.15:9092` — cambiar a `localhost:9092` si usas Docker local).
- `--mode`: `json` o `compact`. En `json` se envían objetos JSON legibles; en `compact` se envían 3 bytes codificados (implementación en `encoder.py`).

Pruebas y validación

- Para ejecutar los tests unitarios (encoder):

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q tests/test_encoder.py
```

Breve descripción de archivos

- `sensor_simulator.py`: genera lecturas simuladas de temperatura (float con 2 decimales, muestreado desde una gaussiana), humedad (int) y `direccion_viento` (una de las 8 direcciones).
- `encoder.py`: funciones `encode_json`/`decode_json` y `encode_compact`/`decode_compact`. La codificación compacta usa 24 bits (14 bits para temperatura escalada ×100, 7 bits para humedad, 3 bits para dirección) y devuelve exactamente 3 bytes.
- `producer.py`: script que genera lecturas y las publica en Kafka. Soporta `--mode json|compact` y envía mensajes periódicamente (intervalo por defecto 15–30 s).
- `consumer.py`: script que se suscribe al topic, decodifica mensajes según el modo y acumula/visualiza la telemetría (actualmente imprime y prepara datos para graficar).
- `docker-compose.yml`: definición para levantar Zookeeper y Kafka localmente (útil cuando el broker remoto no es accesible).
- `requirements.txt`: dependencias Python (`kafka-python`, `numpy`, `matplotlib`, ...).
- `tests/test_encoder.py`: tests unitarios para comprobar encode/decode (JSON y compact).

