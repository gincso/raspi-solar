# Troubleshooting

## No data received

1. Verify USB connection: `ls -l /dev/ttyUSB*`
2. Check permissions: `sudo usermod -aG dialout <user>`
3. Test port: `sudo python3 -c "import serial; s=serial.Serial('/dev/ttyUSB0',9600); print('OK')"`
4. Confirm slave_id matches inverter address (usually 1)
5. Confirm baudrate (9600 is default for SunGoldPower 10kW)

## CRC mismatch errors

- Check cable quality and USB adapter driver
- Reduce poll interval to 5 seconds
- Try different USB port or adapter

## Home Assistant entities not showing

1. Verify MQTT broker is reachable from HA
2. Check `homeassistant/sensor/raspi_solar_battery_voltage/config` topic exists
3. Ensure `homeassistant/solar.yaml` or auto-discovery is enabled
4. Restart Home Assistant

## Service not running

```bash
sudo systemctl status raspi-solar
sudo journalctl -u raspi-solar -n 50 --no-pager
```
