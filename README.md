# DaRkb0x

DaRkb0x is a comprehensive portable penetration testing and wardriving framework designed for Raspberry Pi devices (such as the Pi Zero 2W), featuring a clean UI, physical button navigation, external hardware support (GPS, WiFi adapters), and a massive suite of attack/recon payloads.

## Features
- **Wardriving:** Multi-card monitor mode, GPS tracking (u-blox, Quectel LC86L), Wigle.net CSV & JSON exports, real-time map plotting.
- **Wireless Attacks:** Deauth, Evil Twin, PMKID grabbing, Karma AP.
- **Networking:** Responder, Nmap, DNS Spoofing, Evil Ethernet.
- **Hardware Integration:** Support for ST7735/ST7789 LCD screens, dual WiFi interfaces, BLE.
- **Web UI:** Remote control and payload management via a built-in HTTP server.

## Installation

### 1. Prerequisites
- Raspberry Pi (Zero W, Zero 2W, 3, or 4).
- Waveshare 1.44" LCD HAT (or compatible ST7735/ST7789 screen).
- Kali Linux or Raspberry Pi OS (Bullseye/Bookworm).

### 2. Cloning the Repository
```bash
git clone https://github.com/darkLabz001/DaRkb0x.git ~/DaRkb0x
cd ~/DaRkb0x
```

### 3. Running the Installer
Make the installer executable and run it as root:
```bash
chmod +x install_darkbox.sh
sudo ./install_darkbox.sh
```

During installation, you will be prompted to select your screen type (e.g., ST7735_128 or ST7789_240). The script will automatically install all dependencies (`aircrack-ng`, `gpsd`, `python3-scapy`, etc.), configure the SPI interface, and set up systemd services.

### 4. Reboot
Once the installation finishes successfully, reboot your device:
```bash
sudo reboot
```

## Usage
Upon booting, the DaRkb0x UI will automatically appear on the attached LCD screen. Use the physical buttons on the HAT to navigate menus and launch payloads. You can also access the Web UI by navigating to the device's IP address (e.g., `https://172.20.10.3/` or `https://darkbox.local/`) in your browser.

## Directory Structure
- `payloads/`: Contains all attack and recon scripts categorized by type.
- `loot/`: Captured handshakes, pcaps, and wardriving CSVs are saved here.
- `config/`: System and payload configuration files.
- `web/`: Web UI HTML, CSS, and JS assets.

## Disclaimer
This project is intended for educational purposes and authorized penetration testing only. Do not use DaRkb0x against networks or devices you do not own or have explicit permission to test.
