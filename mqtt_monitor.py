"""
Smart Factory MQTT Edge Monitor
Subscribes to factory/+/sensors, classifies each machine as Normal, Warning,
or Critical, and prints maintenance recommendations.

Start Mosquitto first, then run:
    python mqtt_monitor.py
"""
import json
from datetime import datetime

import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
SUBSCRIBE_TOPIC = "factory/+/sensors"

# Demo thresholds. Adjust for the equipment and units in a real deployment.
WARNING_LIMITS = {
    "vibration": 5.0,
    "temperature_c": 75.0,
    "current_a": 14.0,
}
CRITICAL_LIMITS = {
    "vibration": 8.0,
    "temperature_c": 90.0,
    "current_a": 18.0,
}


def classify_machine(reading: dict) -> tuple[str, list[str]]:
    """Classify a reading using threshold rules, not a trained ML model."""
    warnings = []
    criticals = []

    for key, value in reading.items():
        if key not in WARNING_LIMITS:
            continue
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            continue

        if numeric_value >= CRITICAL_LIMITS[key]:
            criticals.append(key)
        elif numeric_value >= WARNING_LIMITS[key]:
            warnings.append(key)

    if criticals:
        return "Critical", criticals + warnings
    if warnings:
        return "Warning", warnings
    return "Normal", []


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"Connected to MQTT broker at {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(SUBSCRIBE_TOPIC, qos=1)
        print(f"Subscribed to {SUBSCRIBE_TOPIC}")
    else:
        print(f"MQTT connection failed: {reason_code}")


def on_message(client, userdata, message):
    try:
        reading = json.loads(message.payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        print(f"[INVALID MESSAGE] {message.topic}: payload is not valid JSON")
        return

    status, flagged = classify_machine(reading)
    machine_id = reading.get("machine_id", message.topic.split("/")[1])
    timestamp = reading.get("timestamp", datetime.now().isoformat(timespec="seconds"))

    print("\n" + "=" * 68)
    print(f"Machine: {machine_id} | Status: {status} | Time: {timestamp}")
    print(
        "Vibration: {vibration} | Temperature: {temperature_c} °C | "
        "Current: {current_a} A | Pressure: {pressure_bar} bar".format(
            vibration=reading.get("vibration", "N/A"),
            temperature_c=reading.get("temperature_c", "N/A"),
            current_a=reading.get("current_a", "N/A"),
            pressure_bar=reading.get("pressure_bar", "N/A"),
        )
    )

    if status == "Critical":
        print(f"[CRITICAL ALERT] Inspect machine; abnormal parameter(s): {', '.join(flagged)}")
        print("Maintenance decision: stop for inspection according to site procedures.")
    elif status == "Warning":
        print(f"[WARNING] Monitor machine; abnormal parameter(s): {', '.join(flagged)}")
        print("Maintenance decision: schedule an inspection.")
    else:
        print("Maintenance decision: continue monitoring.")


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="smart-factory-edge-monitor",
    )
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        print("Edge monitor running. Press Ctrl+C to stop.")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping edge monitor...")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
