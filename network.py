import netifaces
import subprocess
import platform
import re


def get_route_ip():
    gateways = netifaces.gateways()
    default_route = gateways["default"]
    return default_route[netifaces.AF_INET][0]


def find_clock_aps():
    system = platform.system()
    results = []

    if system == "Linux":
        command = ["nmcli", "-t", "-f", "BSSID,SSID", "dev", "wifi", "list", "--rescan", "yes"]
        output = subprocess.run(command, capture_output=True, text=True)
        if output.returncode != 0:
            raise Exception(f"Failed to list Wi-Fi networks: {output.stderr}")

        for line in output.stdout.splitlines():
            ssid = line[23:]
            bssid = line[0:22].replace("\\", "")
            results.append({"ssid": ssid, "bssid": bssid})

    elif system == "Windows":
        command = ["netsh", "wlan", "show", "network", "mode=Bssid"]
        output = subprocess.run(command, capture_output=True, text=True)
        if output.returncode != 0:
            raise Exception(f"Failed to list Wi-Fi networks: {output.stderr}")

        matches = re.findall(r"(SSID [0-9]* : (.+\n)*\n)", output.stdout)
        for match in matches:
            ssid = re.match(r"SSID [0-9]* : (.+)", match[0]).group(1)
            bssids = re.findall(r"BSSID [0-9]*\s*: (.+)", match[0])
            for bssid in bssids:
                results.append({"ssid": ssid, "bssid": bssid})
    else:
        raise Exception(f"Unsupported operating system: {system}")
    
    return [result for result in results if result["bssid"].startswith("46:44:")]


def connect_to_ap(ssid, bssid, password):
    system = platform.system()

    if system == "Linux":
        command = ["nmcli", "d", "wifi", "connect", ssid, "bssid", bssid, "password", password]
    elif system == "Windows":
        command = ["netsh", "wlan", "connect", f"name={ssid}", f"bssid={bssid}", "key", f"{password}"]
    else:
        raise Exception(f"Unsupported operating system: {system}")

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to connect to Wi-Fi network: {result.stderr}")