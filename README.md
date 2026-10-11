# Smart Factory Monitoring and Maintenance System

An Industrial IoT (IIoT) demonstration based on the supplied project presentation. Simulated factory machines publish timestamped sensor readings through MQTT; a Python edge-monitor program subscribes, evaluates readings against threshold rules, and prints machine health and maintenance decisions.

## Architecture

```text
Simulated Machines (Python publisher)
          |
          | MQTT: factory/machine1/sensors
          | MQTT: factory/machine2/sensors
          | MQTT: factory/machine3/sensors
          v
Mosquitto MQTT Broker (localhost:1883)
          |
          | subscription: factory/+/sensors
          v
Python Edge Monitor
          |
          v
Terminal output: Normal / Warning / Critical + maintenance recommendation
```

The publisher and subscriber are separate programs to reflect the architecture described in the presentation. The `+` wildcard subscribes to one topic level, allowing the edge monitor to receive readings from all machine topics.

## Sensor values simulated

Each machine publishes:
- `vibration`
- `temperature_c`
- `current_a`
- `pressure_bar`
- `timestamp`
- `machine_id`

**These values are randomly simulated for demonstration. They are not collected from physical sensors.**

## Tools

- Python 3
- Mosquitto MQTT broker
- Paho-MQTT Python client

## Setup on Windows

### 1. Install and start Mosquitto

Install Mosquitto for Windows from the official Eclipse Mosquitto website. Start its Windows service or run the broker manually. The examples expect the broker to listen on `localhost`, port `1883`.

You can check whether the broker is listening on port 1883 in Windows. If your broker uses another host or port, update `BROKER_HOST` and `BROKER_PORT` in both Python files.

### 2. Install Python dependencies

Open Command Prompt in this project folder and run:

```bash
python -m pip install -r requirements.txt
```

### 3. Start the edge monitor

In the first Command Prompt window:

```bash
python mqtt_monitor.py
```

It should connect to the broker and subscribe to `factory/+/sensors`.

### 4. Start the simulated factory

Open a second Command Prompt in the same folder and run:

```bash
python sensor_simulator.py
```

The simulator publishes readings for three machines every two seconds. Watch the edge-monitor window for live readings and status messages. Stop either program with `Ctrl+C`.

## Health classification

The monitor uses editable example thresholds:
- **Warning:** vibration >= 5, temperature >= 75 °C, or current >= 14 A.
- **Critical:** vibration >= 8, temperature >= 90 °C, or current >= 18 A.
- **Normal:** none of the configured warning limits are reached.

These thresholds are demonstration values only. They are not validated limits for any real industrial machine. The current implementation is rule-based threshold classification, not machine-learning-based failure prediction.

## Repository files

- `sensor_simulator.py` — publishes simulated readings for three machines.
- `mqtt_monitor.py` — subscribes, classifies machine health, and prints maintenance recommendations.
- `requirements.txt` — Python dependency.
- `screenshots/` — add your own terminal screenshots or dashboard images here.

## Limitations and future work

This version uses simulated readings and terminal output. Future extensions could connect physical sensors or PLCs, store time-series data, build a web dashboard, integrate a computerized maintenance management system (CMMS), and evaluate a trained failure-prediction model.

## Safety and scope

This is an educational software simulation. Do not use the example thresholds or maintenance messages as the sole basis for operating or shutting down real industrial equipment.
