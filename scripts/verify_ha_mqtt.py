#!/usr/bin/env python3
"""
verify_ha_mqtt.py — Verify Home Assistant MQTT connectivity and entity discovery
"""
import json
import sys
import time
import yaml

import paho.mqtt.client as mqtt


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config_path = "/etc/raspi-solar/config.yaml"
    config = load_config(config_path)
    mqtt_cfg = config["mqtt"]
    topic_prefix = mqtt_cfg.get("topic_prefix", "home/solar")

    print(f"Connecting to MQTT broker at {mqtt_cfg['host']}:{mqtt_cfg.get('port', 1883)}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if mqtt_cfg.get("username"):
        client.username_pw_set(mqtt_cfg["username"], mqtt_cfg.get("password", ""))

    connected = False

    def on_connect(c, u, f, rc, p):
        nonlocal connected
        if rc == 0:
            print("✓ Connected to MQTT broker")
            connected = True
        else:
            print(f"✗ Failed to connect (code {rc})")
            sys.exit(1)

    def on_disconnect(c, u, f, rc, p):
        nonlocal connected
        connected = False

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(mqtt_cfg["host"], mqtt_cfg.get("port", 1883), 10)
    except Exception as e:
        print(f"✗ Connection error: {e}")
        sys.exit(1)

    client.loop_start()

    for _ in range(30):
        if connected:
            break
        time.sleep(0.2)
    else:
        print("✗ Connection timeout")
        sys.exit(1)

    # Check for HA discovery topics
    print(f"\nChecking Home Assistant discovery topics for '{topic_prefix}'...")
    entities = [
        "battery_voltage", "battery_power", "pv_voltage", "pv_current",
        "pv_power", "grid_voltage", "grid_power", "load_power",
        "inverter_temp", "fault_code", "energy_today"
    ]

    discovered = 0
    for entity in entities:
        topic = f"homeassistant/sensor/raspi_solar_{entity}/config"
        result = client.subscribe(topic, qos=0)
        if result[0] == 0:
            print(f"  ✓ {entity} discovery topic subscribed")
            discovered += 1
        else:
            print(f"  ✗ {entity} discovery topic failed")

    # Publish a test state
    test_topic = f"{topic_prefix}/battery_voltage/state"
    client.publish(test_topic, json.dumps({"value": 48.5, "unit": "V"}), retain=True)
    print(f"\nPublished test state to {test_topic}")

    client.loop_stop()
    client.disconnect()

    print(f"\nSummary: {discovered}/{len(entities)} discovery topics available")
    if discovered > 0:
        print("✓ Home Assistant MQTT integration is working")
    else:
        print("⚠ No discovery topics found - ensure MQTT integration is enabled in HA")


if __name__ == "__main__":
    main()
