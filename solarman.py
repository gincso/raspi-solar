#!/usr/bin/env python3
"""
solarman.py — SolarMan WiFi integration for SunGoldPower inverters
===================================================================

This module communicates with SunGoldPower hybrid inverters that are
connected via a WiFi dongle (SolarMan protocol). It is an alternative
to the direct USB Modbus RTU connection.

Connection: WiFi dongle connected to inverter, provides TCP/IP endpoint
Protocol:   SolarMan proprietary protocol (over TCP/IP)
"""

import argparse
import json
import logging
import socket
import struct
import time
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def crc16(data):
    """Calculate Modbus CRC-16 (Modbus RTU frame checksum)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc & 0xFFFF


def modbus_frame(address, function, start_addr, qty):
    """Build a Modbus RTU request frame."""
    body = bytes([address, function]) + struct.pack(">H", start_addr) + struct.pack(">H", qty)
    crc = crc16(body)
    return body + bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def read_registers(host, port, address, function, start_addr, qty, timeout=5):
    """Read registers from inverter over TCP (SolarMan WiFi dongle)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        frame = modbus_frame(address, function, start_addr, qty)
        sock.sendall(frame)
        time.sleep(0.05)
        response = sock.recv(1024)
        if len(response) < 5:
            return None
        byte_count = response[2]
        if len(response) < 3 + byte_count + 2:
            return None
        data = response[3:3 + byte_count]
        received_crc = response[-2] | (response[-1] << 8)
        calculated_crc = crc16(response[:-2])
        if received_crc != calculated_crc:
            logging.warning("CRC mismatch in modbus response")
            return None
        if response[0] != address or response[1] != function:
            return None
        values = []
        for i in range(0, byte_count, 2):
            values.append(struct.unpack(">H", data[i:i + 2])[0])
        return values
    except Exception as e:
        logging.error("Error reading registers: %s", e)
        return None
    finally:
        sock.close()


# ---------------------------------------------------------------------------
# SunGoldPower register map (SP6548 / 10kW hybrid)
# ---------------------------------------------------------------------------

DEFAULT_REGISTER_MAP = {
    "battery_voltage":   (30000, "V", 0.1),
    "battery_current":   (30001, "A", 0.1),
    "pv_voltage":        (30002, "V", 0.1),
    "pv_current":        (30003, "A", 0.1),
    "grid_voltage":      (30004, "V", 0.1),
    "grid_current":      (30005, "A", 0.1),
    "load_voltage":      (30006, "V", 0.1),
    "battery_power":     (30007, "W", 1.0, True),
    "pv_power":          (30008, "W", 1.0),
    "grid_power":        (30009, "W", 1.0, True),
    "load_power":        (30010, "W", 1.0),
    "inverter_power":    (30011, "W", 1.0),
    "battery_temp":      (30012, "C", 0.1),
    "rectifier_temp":    (30013, "C", 0.1),
    "inverter_temp":     (30014, "C", 0.1),
    "rectifier_current": (30015, "A", 0.1),
    "inverter_current":  (30016, "A", 0.1),
    "fault_code":        (30100, "", 1.0),
    "energy_today":      (30101, "kWh", 0.1),
}


def load_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def read_all(config_path="/etc/raspi-solar/config.yaml"):
    """Read all registers from inverter over WiFi (SolarMan protocol)."""
    config = load_config(config_path)
    inverter_cfg = config["inverter"]
    register_map = DEFAULT_REGISTER_MAP.copy()
    register_map.update(config.get("register_map", {}))

    host = inverter_cfg.get("host", "192.168.1.100")
    port = int(inverter_cfg.get("port", 8899))
    slave_id = int(inverter_cfg.get("slave_id", 1))

    logging.info("Reading from SolarMan WiFi dongle at %s:%s", host, port)

    readings = {}
    for name, spec in register_map.items():
        addr, unit, scale = spec[0], spec[1], spec[2]
        signed = spec[3] if len(spec) > 3 else False
        values = read_registers(host, port, slave_id, 4, addr, 1)
        if values is None:
            continue
        value = values[0]
        if signed and value & 0x8000:
            value -= 0x10000
        readings[name] = {"value": round(value / scale, 2), "unit": unit}

    return readings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--dump", action="store_true", help="dump raw registers as JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    inverter_cfg = config["inverter"]
    register_map = DEFAULT_REGISTER_MAP.copy()
    register_map.update(config.get("register_map", {}))

    host = inverter_cfg.get("host", "192.168.1.100")
    port = int(inverter_cfg.get("port", 8899))
    slave_id = int(inverter_cfg.get("slave_id", 1))
    interval = float(inverter_cfg.get("poll_interval", 5))

    logging.info("Opening SolarMan WiFi connection at %s:%s", host, port)

    while True:
        readings = {}
        for name, (addr, unit, scale, *rest) in register_map.items():
            signed = rest[0] if rest else False
            values = read_registers(host, port, slave_id, 4, addr, 1)
            if values is None:
                continue
            value = values[0]
            if signed and value & 0x8000:
                value -= 0x10000
            readings[name] = {"value": round(value / scale, 2), "unit": unit}

        logging.info("Read %d registers", len(readings))
        if args.dump:
            print(json.dumps(readings, indent=2))
        time.sleep(interval)


if __name__ == "__main__":
    main()
