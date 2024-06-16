import os
from dataclasses import dataclass
import json
import re

import tui
import coap
import network

STORAGE_FILE = "clocks.json"

@dataclass
class Clock:
    name: str
    ip: str
    mac: str


def load_clocks():
    if not os.path.exists(STORAGE_FILE):
        return []
    json_data = json.load(open(STORAGE_FILE, "r"))
    return [Clock(**data) for data in json_data]


def save_clocks(clocks):
    json.dump([clock.__dict__ for clock in clocks], open(STORAGE_FILE, "w"))


def setup_clock():
    ip = "192.168.4.1"
    info = coap.request_info(ip)
    if info is None:
        print("Clock not found.")
        return
    device = info["device"]
    print(f'Setup: {device["name"]} ({device["mac"]}) {device["version"]}')
    ssid = tui.prompt_input("WiFi SSID")
    password = tui.prompt_secret("WiFi password")
    username = tui.prompt_input("WiFi enterprise username (leave blank if not required)")

    coap.request_setup(ip, ssid, password, username)
    print("Setup complete.")


def option_setup_clock(clock: Clock):
    print("Connecting to clock...")
    try:
        network.connect_to_ap(clock.name, clock.mac, "yanndroid")
    except Exception as e:
        print(f"Error: {e}")
        print(f'Please connect to the "{clock.name}" wifi manually using "yanndroid" as the password.')
        input("Press <enter> when done.")

    setup_clock()


def option_main_setup_clock(*agrs):
    print("Scanning for new clocks...")
    try:
        aps = network.find_clock_aps()
        if len(aps) == 0:
            raise Exception("No clocks found.")
        
        options = []
        for ap in aps:
            options.append(tui.Option(f"{ap['ssid']} ({ap['bssid']})", option_setup_clock, Clock(ap['ssid'], "", ap['bssid'])))
        tui.show_menu("Select a clock to setup", options)
    except Exception as e:
        print(f"Error: {e}")
        print(f'Please connect to the clock wifi manually using "yanndroid" as the password.')
        input("Press <enter> when done.")
        setup_clock()



def option_main_add_clock(clocks):
    print("After setting up or plugging in the clock, two hexadecimal number will appear in red and green for a short while.")

    ip_start = re.match(r'([0-9]{1,3})\.([0-9]{1,3}).*', network.get_route_ip())

    ip_end_hex = None
    while ip_end_hex is None:
        ip_end_hex = re.match(r'([0-9a-fA-F]{2})\.([0-9a-fA-F]{2})', tui.prompt_input("Numbers (rr.gg)"))

    ip = f'{ip_start.group(1)}.{ip_start.group(2)}.{int(ip_end_hex.group(1), 16)}.{int(ip_end_hex.group(2), 16)}'

    print("IP:", ip)
    response = coap.request_info(ip)
    if response is None:
        print("Clock not found.")
        return
    device = response["device"]
    print("MAC:", device["mac"])
    print("Name:", device["name"])
    
    clocks.append(Clock(device["name"], ip, device["mac"]))
    save_clocks(clocks)


def option_clock_locate(clock: Clock):
    coap.request_locate(clock.ip)
    print("Locating clock.")


def option_clock_brightness(clock: Clock):
    prev = coap.request_get_brightness(clock.ip)["brightness"]
    max = tui.prompt_number(f"Max brightness ({prev["max"]})", 0, 255)
    min = tui.prompt_number(f"Min brightness ({prev["min"]})", 0, 255)
    margin = int(tui.prompt_number(f"Transition hours ({int(prev["margin"]*2/3600)})", 0, 8) * 3600 / 2)
    coap.request_set_brightness(clock.ip, max, min, margin)


def option_clock_reset(clock: Clock):
    confirm = tui.prompt_input('Type "YES" to reset.')
    if confirm != "YES":
        print("Reset cancelled.")
        return False
    coap.request_reset(clock.ip)
    print("Resetting clock.")
    return True


def option_clock_restart(clock: Clock):
    coap.request_restart(clock.ip)
    print("Restarting clock.")


def option_clock_update(clock: Clock):
    url = tui.prompt_input("URL")
    signature = tui.prompt_input("Signature")
    coap.request_update(clock.ip, url, signature)


def option_main_clock(clock: Clock):
    response = coap.request_info(clock.ip)
    if response is None:
        print("Clock not found.")
        return
    
    device = response["device"]
    tui.show_menu_loop(
        f'{device["name"]} ({device["mac"]}) {device["version"]}',
        [
            tui.Option("Locate", option_clock_locate, clock),
            tui.Option("Set Brightness", option_clock_brightness, clock),
            # tui.Option("Set Color", todo, clock),
            tui.Option("Reset", option_clock_reset, clock),
            tui.Option("Restart", option_clock_restart, clock),
            tui.Option("Update", option_clock_update, clock),
        ],
    )


def main():
    clocks = load_clocks()

    while True:
        main_options = [
            tui.Option("Setup new Clock", option_main_setup_clock),
            tui.Option("Add Clock", option_main_add_clock, clocks),
        ]
        for clock in clocks:
            main_options.append(
                tui.Option(f"Clock: {clock.name} ({clock.ip}) ({clock.mac})", option_main_clock, clock)
            )

        if tui.show_menu("Main menu", main_options):
            break


if __name__ == "__main__":
    main()
