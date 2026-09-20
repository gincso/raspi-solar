# Raspberry Pi 5 Solar Monitoring

Remote monitoring of a **SunGoldPower 10kW hybrid inverter** from a **Raspberry Pi 5**,
exposed to **Home Assistant** over the network.

## Overview

This project monitors a SunGoldPower 10kW hybrid inverter via USB serial (Modbus RTU) and publishes all measurements to Home Assistant via MQTT.

## Features

- Reads SunGoldPower inverter data over USB serial (9600 baud, Modbus RTU)
- Publishes battery voltage, PV power, grid power, inverter temperature, fault codes, and energy totals
- Integrates with Home Assistant via MQTT auto-discovery
- Runs as a systemd service for reliable operation

## Requirements

- Raspberry Pi 5 (4 GB+ recommended), Raspberry Pi OS Lite or Bookworm
- SunGoldPower 10kW hybrid inverter with USB serial port (or USB-UART adapter)
- Home Assistant with MQTT integration (Hass.io / Home Assistant OS / standalone)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/gincso/raspi-solar.git
   cd raspi-solar
   ```

2. **Setup**
   ```bash
   ./setup.sh
   ```
   This installs Python dependencies (paho-mqtt, pyserial), copies the service and config files, and enables the systemd service.

3. **Start the service**
   ```bash
   sudo systemctl start raspi-solar
   sudo systemctl enable raspi-solar
   ```

4. **Verify Home Assistant MQTT connectivity**
   ```bash
   # Check if MQTT broker is reachable
   nc -z gincso:raspi-solar 1883
   
   # Verify Home Assistant discovers topics
   mosquitto_sub -t 'home/solar/#' -v
   ```

## Configuration

Edit `config/config.yaml` to adjust:

- **inverter** – Port, baud rate, slave ID, poll interval
- **mqtt** – Broker host, port, username/password (optional), topic prefix

Example `config.yaml`:

```yaml
inverter:
  port: /dev/ttyUSB0
  baudrate: 9600
  slave_id: 1
  poll_interval: 5

mqtt:
  host: gincso:raspi-solar
  port: 1883
  username: ""
  password: ""
  topic_prefix: home/solar
```

## Home Assistant Integration

The project publishes to these MQTT topics (auto-discovered by Home Assistant):

| Topic | Entity Type | Description |
|-------|-------------|-------------|
| `home/solar/battery_voltage/state` | sensor | Battery voltage (V) |
| `home/solar/battery_power/state` | sensor | Battery power (W) |
| `home/solar/pv_voltage/state` | sensor | PV array voltage (V) |
| `home/solar/pv_current/state` | sensor | PV array current (A) |
| `home/solar/pv_power/state` | sensor | PV array power (W) |
| `home/solar/grid_voltage/state` | sensor | Grid voltage (V) |
| `home/solar/grid_power/state` | sensor | Grid power (W) |
| `home/solar/load_power/state` | sensor | Load power (W) |
| `home/solar/inverter_temp/state` | sensor | Inverter temperature (°C) |
| `home/solar/fault_code/state` | boolean | Active fault flag |
| `home/solar/energy_today/state` | float | Today's energy generation (kWh) |

## Troubleshooting

- **MQTT not connecting** – Verify Home Assistant MQTT integration is enabled
- **No topics discovered** – Check `config.yaml` MQTT settings and network connectivity
- **Service won't start** – Run `sudo systemctl status raspi-solar`

## Files

- `sungoldpower.py` – Reads inverter data via Modbus RTU
- `ha_bridge.py` – Publishes data to Home Assistant MQTT
- `raspi-solar.service` – systemd service definition
- `config/config.yaml` – Configuration for inverter and MQTT
- `homeassistant/solar.yaml` – Home Assistant MQTT entity configuration
- `docs/registers.md` – SunGoldPower register map
- `docs/troubleshooting.md` – Common issues and solutions
- `scripts/verify_ha_mqtt.py` – Script to verify HA MQTT connectivity

