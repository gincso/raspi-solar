#!/usr/bin/env bash
# setup.sh — install python deps, copy service, enable on Raspberry Pi 5,
#             and verify Home Assistant MQTT connectivity.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_SRC="$ROOT/raspi-solar.service"
SERVICE_DST="/etc/systemd/system/raspi-solar.service"
CONF_SRC="$ROOT/config/config.yaml"
CONF_DST="/etc/raspi-solar/config.yaml"
CONF_DIR="/etc/raspi-solar"

echo "==> Installing python dependencies"
python3 -m pip install --upgrade pip -q
python3 -m pip install -q paho-mqtt pyserial

echo "==> Copying scripts to /opt/raspi-solar"
install -d -m 0755 /opt/raspi-solar
cp "$ROOT"/sungoldpower.py "$ROOT"/ha_bridge.py "$ROOT"/scripts /opt/raspi-solar/

echo "==> Installing config"
install -d -m 0755 "$CONF_DIR"
if [ ! -f "$CONF_DST" ]; then
    cp "$CONF_SRC" "$CONF_DST"
    echo "    copied default config to $CONF_DST  (edit it before starting)"
else
    echo "    keeping existing $CONF_DST"
fi

echo "==> Installing systemd service"
install -m 0644 "$SERVICE_SRC" "$SERVICE_DST"
systemctl daemon-reload
systemctl enable --now raspi-solar.service || true

echo "==> Verifying Home Assistant MQTT connectivity"
MQTT_HOST=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONF_DST')); print(c['mqtt']['host'])")
MQTT_PORT=$(python3 -c "import yaml; c=yaml.safe_load(open('$CONF_DST')); print(c['mqtt'].get('port',1883))")
if nc -z "$MQTT_HOST" "$MQTT_PORT" 2>/dev/null; then
    echo "    MQTT broker at $MQTT_HOST:$MQTT_PORT is reachable"
else
    echo "    WARNING: MQTT broker at $MQTT_HOST:$MQTT_PORT is NOT reachable"
    echo "    Check your Home Assistant MQTT configuration and network connectivity"
fi

echo ""
echo "==> Done. Check status with: sudo systemctl status raspi-solar.service"
echo "    Verify MQTT topics: mosquitto_sub -t 'home/solar/#' -v"
echo "    Check Home Assistant: Settings > Devices & Services > MQTT"
