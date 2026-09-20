#!/usr/bin/env python3
"""
ha_bridge.py — MQTT bridge to Home Assistant
============================================

Publishes solar inverter data to Home Assistant via MQTT with auto-discovery.
"""

import json
import logging
import signal
import sys
import time
import yaml

import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


class HABridge:
    def __init__(self, config_path):
        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

        self.mqtt_cfg = cfg["mqtt"]
        self.topic_prefix = self.mqtt_cfg.get("topic_prefix", "home/solar")
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="raspi-solar")
        self.client.username_pw_set(self.mqtt_cfg.get("username", ""), self.mqtt_cfg.get("password", ""))
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.running = True

        signal.signal(signal.SIGTERM, lambda *_: self.stop())
        signal.signal(signal.SIGINT, lambda *_: self.stop())

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        log.info("MQTT connected (code %s)", reason_code)
        self._publish_discovery()

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        log.warning("MQTT disconnected (code %s)", reason_code)

    def connect(self):
        log.info("Connecting to MQTT at %s:%s", self.mqtt_cfg["host"], self.mqtt_cfg.get("port", 1883))
        self.client.connect(self.mqtt_cfg["host"], self.mqtt_cfg.get("port", 1883), 60)
        self.client.loop_start()

    def stop(self):
        log.info("Stopping...")
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()

    def _publish_discovery(self):
        """Publish Home Assistant MQTT auto-discovery configs."""
        entities = [
            ("battery_voltage", "voltage", "V", "mdi:battery", "voltage"),
            ("battery_power", "power", "W", "mdi:battery-charging", "power"),
            ("pv_voltage", "voltage", "V", "mdi:solar-panel", "voltage"),
            ("pv_current", "current", "A", "mdi:current-dc", "current"),
            ("pv_power", "power", "W", "mdi:solar-power", "power"),
            ("grid_voltage", "voltage", "V", "mdi:transmission-tower", "voltage"),
            ("grid_power", "power", "W", "mdi:transmission-tower", "power"),
            ("load_power", "power", "W", "mdi:home", "power"),
            ("inverter_temp", "temperature", "°C", "mdi:thermometer", "temperature"),
            ("fault_code", None, "", "mdi:alert", None),
            ("energy_today", "energy", "kWh", "mdi:solar-power", "energy"),
        ]

        for name, device_class, unit, icon, state_class in entities:
            unique_id = f"raspi_solar_{name}"
            topic = f"homeassistant/sensor/{unique_id}/config"
            payload = {
                "name": f"Solar {name.replace('_', ' ').title()}",
                "state_topic": f"{self.topic_prefix}/{name}/state",
                "unique_id": unique_id,
                "device": {
                    "identifiers": ["raspi_solar"],
                    "name": "SunGoldPower 10kW Inverter",
                    "manufacturer": "SunGoldPower",
                    "model": "10kW Hybrid",
                },
                "icon": icon,
            }
            if device_class:
                payload["device_class"] = device_class
            if unit:
                payload["unit_of_measurement"] = unit
            if state_class:
                payload["state_class"] = state_class
            self.client.publish(topic, json.dumps(payload), retain=True)

    def publish(self, readings):
        """Publish readings to MQTT state topics."""
        for name, data in readings.items():
            topic = f"{self.topic_prefix}/{name}/state"
            payload = json.dumps({"value": data["value"], "unit": data["unit"]})
            self.client.publish(topic, payload, retain=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="/etc/raspi-solar/config.yaml")
    args = parser.parse_args()

    bridge = HABridge(args.config)
    bridge.connect()

    # Import the sungoldpower module
    sys.path.insert(0, "/opt/raspi-solar")
    import sungoldpower as sg

    interval = 5.0
    while bridge.running:
        # Get readings from inverter
        readings = sg.read_all()  # We'll add this function
        bridge.publish(readings)
        time.sleep(interval)


if __name__ == "__main__":
    main()
