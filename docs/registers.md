# SunGoldPower 10kW Hybrid Inverter Register Map

## Default register map (used by sungoldpower.py)

| Register | Name | Unit | Scale | Signed |
| --- | --- | --- | --- | --- |
| 30000 | battery_voltage | V | 0.1 | No |
| 30001 | battery_current | A | 0.1 | No |
| 30002 | pv_voltage | V | 0.1 | No |
| 30003 | pv_current | A | 0.1 | No |
| 30004 | grid_voltage | V | 0.1 | No |
| 30005 | grid_current | A | 0.1 | No |
| 30006 | load_voltage | V | 0.1 | No |
| 30007 | battery_power | W | 1.0 | Yes |
| 30008 | pv_power | W | 1.0 | No |
| 30009 | grid_power | W | 1.0 | Yes |
| 30010 | load_power | W | 1.0 | No |
| 30011 | inverter_power | W | 1.0 | No |
| 30012 | battery_temp | °C | 0.1 | No |
| 30013 | rectifier_temp | °C | 0.1 | No |
| 30014 | inverter_temp | °C | 0.1 | No |
| 30015 | rectifier_current | A | 0.1 | No |
| 30016 | inverter_current | A | 0.1 | No |
| 30100 | fault_code | - | 1.0 | No |
| 30101 | energy_today | kWh | 0.1 | No |

## Customization

To override register addresses, edit `config/config.yaml`:

```yaml
register_map:
  battery_voltage: [30000, "V", 0.1]
  pv_power: [30008, "W", 1.0]
```

## Protocol

- USB serial adapter (CP210x/CH340) connected to inverter USB port
- Modbus RTU protocol, 9600 baud, 8 data bits, no parity, 1 stop bit (8N1)
- Poll interval configurable in `config/config.yaml` (default: 5 seconds)
