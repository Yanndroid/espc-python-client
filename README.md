# ESP Clock

<img align="right" src="https://github.com/Yanndroid/espc-hardware/raw/main/readme-res/clock.jpg" alt="ESP Clock" width="30%">

ESPC stands for [ESP](https://www.espressif.com/) Clock and is a digital IoT clock. It's connected to WiFi, automatically syncs time, shows weather information, and most importantly, has RGB! At its core, there is an ESP8266, and the display is made of WS2812B LEDs.  
It's a project I've been working on over the past few years, and it has allowed me to learn a lot about the C language and PCB designs.

This project consists of multiple repositories:

- [espc-firmware](https://github.com/Yanndroid/espc-firmware)
- [espc-hardware](https://github.com/Yanndroid/espc-hardware)
- espc-python-client
- [espc-dev-tools](https://github.com/Yanndroid/espc-dev-tools)

# ESP Clock Python Client

This repository contains a simple python client for the ESPC. It provides the bare minimum to be able to configure and control an ESPC.

### Features (W.I.P)

- Setup
- Locate
- Set Brightness
- Reset
- Restart
- Update

### Usage
1. Install dependencies: `pip install -r requirements.txt`
2. Run: `python main.py`