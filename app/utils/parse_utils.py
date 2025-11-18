# agent/parse_utils.py
import re

def parse_netsh_interfaces(raw: str):
    data = {}
    for line in raw.splitlines():
        if ':' in line:
            k,v = line.split(':',1)
            data[k.strip().lower()] = v.strip()
    def maybe_int(s):
        if not s: return None
        m = re.sub('[^0-9]', '', s)
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

def parse_ipconfig(raw: str):
    blocks = raw.split("\r\n\r\n")
    for b in blocks:
        if "Wireless LAN adapter" in b or "Ethernet adapter" in b:
            lines = b.splitlines()
            info = {}
            for line in lines:
                if ':' in line:
                    k,v = line.split(':',1)
                    info[k.strip()] = v.strip()
            # return first block that contains IPv4
            for k in info:
                if "IPv4" in k:
                    return {"ipv4": info.get(k), "gateway": info.get("Default Gateway")}
    return {}
