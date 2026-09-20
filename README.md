# Raspberry Pi 5 Solar Monitoring

Remote monitoring of a **SunGoldPower 10kW hybrid inverter** from a **Raspberry Pi 5**,
exposed to **Home Assistant** over the network.

## Overview

```
[Raspberry Pi 5]
  │
  ├─ USB ← SunGoldPower 10kW Hybrid Inverter (modbus/serial)
  │
  ├─ [sungoldpower.py]  parses inverter data over USB serial
  │
  ├─ [ha_bridge.py]      publishes data to Home Assistant via MQTT
  │
  └─ [homeassistant/]   YAML configs + MQTT entities
```

The Pi reads the inverter's USB serial stream, decodes the SunGoldPower
modbus-like register map, and publishes every value as an MQTT topic so
Home Assistant can display it on dashboards remotely.

## Features

- Reads SunGoldPower 10kW hybrid inverter over USB (CP210x/CH340 USB-UART adapter)
- Decodes battery voltage, PV voltage/current/power, grid voltage/current/power,
  load power, inverter temp, fault codes, and daily energy totals
- Publishes to Home Assistant via MQTT with auto-discovery
- Runs as a systemd service, survives reboots, auto-restarts
- Optional: push notifications on fault / low battery via HA automation

## Requirements

- Raspberry Pi 5 (4 GB+ recommended), Raspberry Pi OS Lite or Bookworm
- SunGoldPower 10kW hybrid inverter with USB serial port (or USB-UART adapter)
- Home Assistant with MQTT integration (Hass.io / Home Assistant OS / standalone)

## Quick start

```bash
# On the Raspberry Pi 5
git clone https://github.com/<your-user>/raspi-solar.git
cd raspi-solar
./setup.sh
```

`setup.sh` installs python deps, copies the service, and enables it:

```bash
sudo systemctl enable --now raspi-solar.service
sudo systemctl status raspi-solar.service
```

Then in Home Assistant:

1. Add the **MQTT** integration
2. Entities auto-discover (no YAML needed), or copy `homeassistant/solar.yaml` into
   your `configuration.yaml` / `packages/` folder

## Configuration

Edit `config/config.yaml`:

```yaml
inverter:
  port: /dev/ttyUSB0        # USB serial device
  baudrate: 9600
  slave_id: 1               # inverter modbus slave id
  poll_interval: 5          # seconds

mqtt:
  host: 192.168.1.10        # Home Assistant / MQTT broker host
  port: 1883
  username: ""
  password: ""
  topic_prefix: home/solar
```

## Dashboard entities

| Entity | Unit | Description |
| --- | --- | --- |
| `solar.battery_voltage` | V | Battery voltage |
| `solar.battery_power` | W | Battery charge/discharge power |
| `solar.pv_voltage` | V | PV array voltage |
| `solar.pv_current` | A | PV array current |
| `solar.pv_power` | W | PV array power |
| `solar.grid_voltage` | V | Grid voltage |
| `solar.grid_power` | W | Grid import/export power |
| `solar.load_power` | W | Load power |
| `solar.inverter_temp` | °C | Inverter temperature |
| `solar.fault_code` | — | Active fault code |
| `solar.energy_today` | kWh | Energy generated today |

## Docs

- `docs/registers.md` — SunGoldPower register map
- `docs/troubleshooting.md` — common USB / modbus issues

## License

MIT — see `LICENSE`.
