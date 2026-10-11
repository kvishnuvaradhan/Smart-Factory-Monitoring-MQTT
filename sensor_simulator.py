"""
Smart Factory MQTT Sensor Simulator
Publishes simulated readings for three machines to:
    factory/machine1/sensors
    factory/machine2/sensors
    factory/machine3/sensors

Start Mosquitto first, then run:
    python sensor_simulator.py
"""
import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
PUBLISH_INTERVAL_SECONDS = 2

MACHINES = ["machine1", "machine2", "machine3"]


def generate_readings(machine_id: str) -> dict:
    """Generate realistic-looking demo readings; these are simulated, not sensors."""
    # Occasionally create a high reading so warning/critical states can be demonstrated.
    event = random.random()
    if event < 0.08:
        vibration = round(random.uniform(8.0, 12.0), 2)
        temperature = round(random.uniform(90.0, 110.0), 1)
        current = round(random.uniform(18.0, 25.0), 2)
        pressure = round(random.uniform(2.0, 3.5), 2)
    elif event < 0.22:
        vibration = round(random.uniform(5.0, 7.5), 2)
        temperature = round(random.uniform(75.0, 89.0), 1)
        current = round(random.uniform(14.0, 17.9), 2)
        pressure = round(random.uniform(3.5, 4.5), 2)
    else:
        vibration = round(random.uniform(1.0, 4.5), 2)
        temperature = round(random.uniform(35.0, 74.0), 1)
        current = round(random.uniform(5.0, 13.9), 2)
        pressure = round(random.uniform(4.5, 7.0), 2)

    return {
        "machine_id": machine_id,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "vibration": vibration,
        "temperature_c": temperature,
        "current_a": current,
        "pressure_bar": pressure,
    }


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="smart-factory-simulator",
    )
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    print(f"Connected to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
    print("Publishing simulated readings. Press Ctrl+C to stop.")

    try:
        while True:
            for machine_id in MACHINES:
                topic = f"factory/{machine_id}/sensors"
                payload = generate_readings(machine_id)
                result = client.publish(topic, json.dumps(payload), qos=1)
                result.wait_for_publish()
                print(f"[PUBLISHED] {topic}: {payload}")
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopping sensor simulator...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
