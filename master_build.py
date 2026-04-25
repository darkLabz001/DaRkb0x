import sys
import os

def build_insomnia_box():
    # 1. Start from a clean slate
    os.system('git checkout darkbox.py')
    with open('darkbox.py', 'r') as f:
        content = f.read()
    
    # --- MONKEYPATCH FONT & DISABLE ICONS ---
    patch = """#!/usr/bin/env python3
import PIL.ImageFont
PIL.ImageFont.truetype = lambda *a, **k: PIL.ImageFont.load_default()
"""
    # Replace shebang and inject patch
    content = content.replace('#!/usr/bin/env python3', patch)
    
    # Disable icons entirely to prevent UnicodeEncodeError
    content = content.replace('icon = _menu_icon_for_label(txt, "")', 'icon = ""')
    content = content.replace('if icon:', 'if False:')
    
    # --- BRANDING & PATHS ---
    content = content.replace('install_path = "/root/DaRkb0x/"', 'install_path = "/home/kali/DaRkb0x/"')
    content = content.replace('DaRkb0x', 'DaRkb0x')
    
    # --- STABILITY ---
    # Be VERY precise with the replace to avoid duplicate fragments
    content = content.replace('import threading, smbus, time, pyudev, serial, struct, json', 'import threading, smbus2 as smbus, time, pyudev, serial, struct, json')
    
    # --- BUTTONS ---
    content = content.replace('if btn == "KEY_DOWN_PIN":', 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":')
    content = content.replace('elif btn == "KEY_UP_PIN":', 'elif btn == "KEY_UP_PIN" or btn == "KEY1_PIN":')
    content = content.replace('elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN"):', 'elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN", "KEY2_PIN"):')

    # --- MENU RESTRUCTURE ---
    # We do a direct string replacement for the menu dictionary start
    # Note: Using a shorter anchor to find it reliably
    menu_anchor = '    menu = {\n        "a": ('
    new_menu_content = """    menu = {
        "a": (
            [" AUTO-PILOT",     "auto"],
            [" NETWORK",        "net"],
            [" WIRELESS",       "aw"],
            [" PAYLOADS",       "ap_root"],
            [" SYSTEM",         "ag"],
            [" Lock",           OpenLockMenu],
        ),

        "auto": (
            [" Run DaRkb0x", partial(exec_payload, "insomnia_suite/insomnia_auto")],
            [" View Auto Logs",  lambda: ReadTextFileInsomnia()],
        ),

        "net": (
            [" Scan Nmap",      "ab"],
            [" Responder",      "ad"],
            [" MITM & Sniff",   "ai"],
            [" DNS Spoofing",   "aj"],
            [" Network info",   ShowInfo],
        ),

        "ap_root": (
            [" Reverse Shell",  "ac"],
            [" All Payloads",   "ap"],
        ),"""
    
    # We find the end of the original "a" block to replace it
    # This is safer than replacing the whole dictionary if we don't have it all perfectly
    import re
    # Match from 'menu = {' to the end of the first tuple member "a"
    content = re.sub(r'menu = \{\s+"a": \([^)]+\),', new_menu_content, content, flags=re.DOTALL)
    
    # Add Log Viewer Menu Entry
    content = content.replace('[" Nmap",      ReadTextFileNmap],', '[" Nmap",      ReadTextFileNmap],\n            [" DaRkb0x",   ReadTextFileInsomnia],')

    # --- INJECT FUNCTIONS ---
    log_viewer_func = """
def ReadTextFileInsomnia():
    while 1:
        rfile = Explorer("/home/kali/DaRkb0x/loot/insomnia/", extensions=".log")
        if rfile == "": break
        with open(rfile) as f:
            content = f.read().splitlines()
        GetMenuString(content)

def ReadTextFileNmap():"""
    content = content.replace('def ReadTextFileNmap():', log_viewer_func)

    with open('darkbox_master_v3.py', 'w') as f:
        f.write(content)
    print("Master DaRkb0x file (v3) created.")

if __name__ == '__main__':
    build_insomnia_box()
