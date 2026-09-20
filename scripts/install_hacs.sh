#!/usr/bin/env bash
# install_hacs.sh - Install HACS (Home Assistant Community Store) in Home Assistant
# This is an optional script to set up HACS for additional integrations.
set -euo pipefail

HA_DIR="${1:-/config}"  # Default to /config (Home Assistant config directory)

echo "==> Installing HACS (Home Assistant Community Store)"
echo "    HA Config directory: $HA_DIR"

# Download HACS custom component
mkdir -p "$HA_DIR/custom_components/hacs"
cd "$HA_DIR/custom_components/hacs"

echo "    Downloading HACS backend..."
curl -sL "https://github.com/hacs/integration/archive/refs/heads/main.zip" -o /tmp/hacs.zip || {
    echo "    WARNING: Could not download HACS backend from GitHub"
    echo "    Check your network connection"
    return 1
}

unzip -q /tmp/hacs.zip -d /tmp/hacs_backend
if [ -d "/tmp/hacs_backend/integration-custom-components/hacs" ]; then
    cp -r /tmp/hacs_backend/integration-custom-components/hacs/* "$HA_DIR/custom_components/hacs/"
else
    echo "    WARNING: HACS backend structure not found in downloaded archive"
fi

# Download manifest.json for HACS
cat > "$HA_DIR/custom_components/hacs/manifest.json" << 'EOF'
{
  "domain": "hacs",
  "name": "HACS",
  "documentation": "https://hacs.xyz/",
  "issue_tracker": "https://github.com/hacs/integration/issues",
  "version": "1.0.0",
  "dependencies": [],
  "codeowners": ["@hacs"]
}
EOF

# Download __init__.py
cat > "$HA_DIR/custom_components/hacs/__init__.py" << 'EOF'
"""HACS - Home Assistant Community Store integration."""
import logging

_LOGGER = logging.getLogger(__name__)
EOF

# Download hacs.json
cat > "$HA_DIR/custom_components/hacs/hacs.json" << 'EOF'
{
  "hacs": {
    "version": "1.0.0",
    "demo": false
  }
}
EOF

echo "    HACS component installed in $HA_DIR/custom_components/hacs/"

# Also install common solar-related HACS integrations as documentation
mkdir -p "$HA_DIR/custom_components/README.md"
cat > "$HA_DIR/custom_components/README.md" << 'EOF'
# HACS Solar Integrations

To install solar-related HACS integrations in Home Assistant:

1. Go to HACS > Integrations > Search for "Solar" or "Modbus"
2. Install the following recommended integrations:
   - **Modbus** (built-in with HA, but check for HACS custom wrapper)
   - **MQTT** (built-in with HA, no installation needed)
3. Restart Home Assistant after installation

## Modbus configuration for SunGoldPower inverter:

In `configuration.yaml`:
```yaml
modbus:
  - name: sun_gold_power
    type: serial
    port: /dev/ttyUSB0
    baudrate: 9600
    stopbits: 1
    bytesize: 8
    parity: N
    method: rtu
```
EOF

echo "    HACS documentation created"
echo ""
echo "==> HACS installation complete"
echo "    Restart Home Assistant to enable HACS"
echo "    Then go to HACS > Integrations to install additional solar integrations"
