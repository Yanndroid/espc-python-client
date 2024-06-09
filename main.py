import os
from dataclasses import dataclass
import json
import re

import tui
import coap
import network

STORGAE_FILE = "clocks.json"

@dataclass
class Clock:
    name: str
    ip: str
    mac: str


def load_clocks():
    if not os.path.exists(STORGAE_FILE):
        return []
    json_data = json.load(open(STORGAE_FILE, "r"))
    return [Clock(**data) for data in json_data]


def save_clocks(clocks):
    json.dump([clock.__dict__ for clock in clocks], open(STORGAE_FILE, "w"))


def option_main_add_clock(clocks):
    print("After setting up or plugging in the clock, two hexadecimal number will appear in red and green for a short while.")

    ip_start = re.match(r'([0-9]{1,3})\.([0-9]{1,3}).*', network.get_route_ip())

    ip_end_hex = None
    while ip_end_hex is None:
        ip_end_hex = re.match(r'([0-9a-fA-F]{2})\.([0-9a-fA-F]{2})', tui.prompt_input("Numbers (xx.xx)"))

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
            # tui.Option("Setup new Clock", todo),
            tui.Option("Add Clock", option_main_add_clock, clocks),
        ]
        for clock in clocks:
            main_options.append(
                tui.Option(f"Clock: {clock.name}", option_main_clock, clock)
            )

        if tui.show_menu("Main menu", main_options):
            break


if __name__ == "__main__":
    main()
