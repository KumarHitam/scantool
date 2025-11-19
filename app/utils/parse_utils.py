# agent/parse_utils.py
import re

# ============================================
# PARSER: netsh wlan show interfaces
# ============================================

def parse_netsh_interfaces(raw: str):
    data = {}

    # ambil key: value
    for line in raw.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip().lower()] = v.strip()

    # fungsi konversi angka
    def maybe_int(s):
        if not s:
            return None
        m = re.sub(r"[^0-9]", "", s)
        return int(m) if m.isdigit() else None

    return {
        "ssid": data.get("ssid"),
        "state": data.get("state"),
        "bssid": data.get("bssid"),
        "signal_pct": maybe_int(data.get("signal")),
        "radio_type": data.get("radio type"),
        "channel": maybe_int(data.get("channel")),
        "authentication": data.get("authentication"),
        "cipher": data.get("cipher")
    }


# ============================================
# PARSER: ipconfig /all
# ============================================

def parse_ipconfig(raw: str):
    """
    Parser diperbaiki:
    - Menangani Default Gateway multiline
    - Membersihkan IPv4 dari '(Preferred)'
    - Compatible untuk Ethernet & WiFi
    """

    ipv4 = None
    gateway = None

    lines = raw.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # -------------------------------
        # IPv4 Address
        # -------------------------------
        if "IPv4 Address" in stripped or ("IPv4" in stripped and ":" in stripped):
            match = re.search(r"IPv4.*?:\s*([\d\.]+)", stripped)
            if match:
                ipv4 = match.group(1).strip()

        # -------------------------------
        # Default Gateway
        # Format kemungkinan:
        # Default Gateway . . . : 192.168.1.1
        # Default Gateway . . . :
        #                         192.168.1.1
        # -------------------------------
        if stripped.startswith("Default Gateway"):
            parts = stripped.split(":", 1)

            # case 1: gateway ada di baris yang sama
            if len(parts) > 1 and parts[1].strip():
                gw = parts[1].strip()
                if re.match(r"^\d+\.\d+\.\d+\.\d+$", gw):
                    gateway = gw

            # case 2: gateway di baris berikutnya (multiline)
            if gateway is None and i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if re.match(r"^\d+\.\d+\.\d+\.\d+$", next_line):
                    gateway = next_line

    return {
        "ipv4": ipv4,
        "gateway": gateway
    }
