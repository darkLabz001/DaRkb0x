import sys
import os

PATH = '/home/kali/DaRkb0x/darkbox.py'
with open(PATH, 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    # 1. Fix the reboot loop (restore menu dictionary)
    if 'menu = {' in line:
        new_lines.append('    menu = {\n')
        new_lines.append('        "a": (\n')
        new_lines.append('            [" AUTO-PILOT",     "auto"],\n')
        new_lines.append('            [" NETWORK",        "net"],\n')
        new_lines.append('            [" WIRELESS",       "aw"],\n')
        new_lines.append('            [" PAYLOADS",       "ap_root"],\n')
        new_lines.append('            [" SYSTEM",         "ag"],\n')
        new_lines.append('            [" Lock",           OpenLockMenu],\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "auto": (\n')
        new_lines.append('            [" Run DaRkb0x", partial(exec_payload, "insomnia_suite/insomnia_auto")],\n')
        new_lines.append('            [" View Auto Logs",  ReadTextFileInsomnia],\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "net": (\n')
        new_lines.append('            [" Scan Nmap",      "ab"],\n')
        new_lines.append('            [" Responder",      "ad"],\n')
        new_lines.append('            [" MITM & Sniff",   "ai"],\n')
        new_lines.append('            [" DNS Spoofing",   "aj"],\n')
        new_lines.append('            [" Network info",   ShowInfo],\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ap_root": (\n')
        new_lines.append('            [" Reverse Shell",  "ac"],\n')
        new_lines.append('            [" All Payloads",   "ap"],\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ab": tuple(\n')
        new_lines.append('            [f" {name}", partial(run_scan, name, args)]\n')
        new_lines.append('            for name, args in SCANS.items()\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ac": (\n')
        new_lines.append('            [" Defaut Reverse",  defaut_Reverse],\n')
        new_lines.append('            [" Remote Reverse",  remote_Reverse]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ad": (\n')
        new_lines.append('            [" Responder ON",   responder_on],\n')
        new_lines.append('            [" Responder OFF",  responder_off]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ag": (\n')
        new_lines.append('            [" Browse Images", ImageExplorer],\n')
        new_lines.append('            [" Discord status", ShowDiscordInfo],\n')
        new_lines.append('            [" Options",       "ae"],\n')
        new_lines.append('            [" System",        "af"],\n')
        new_lines.append('            [" Read file",      "ah"]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ae": (\n')
        new_lines.append('            [" Colors",         "aea"],\n')
        new_lines.append('            [" Flip screen 180", ToggleFlip],\n')
        new_lines.append('            [" Refresh config", LoadConfig],\n')
        new_lines.append('            [" Save config!",   SaveConfig]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "aea": (\n')
        new_lines.append('            [" Background",          [SetColor, 0]],\n')
        new_lines.append('            [" Text",                [SetColor, 2]],\n')
        new_lines.append('            [" Selected text",       [SetColor, 3]],\n')
        new_lines.append('            [" Selected background", [SetColor, 4]],\n')
        new_lines.append('            [" Border",              [SetColor, 1]],\n')
        new_lines.append('            [" Gamepad border",      [SetColor, 5]],\n')
        new_lines.append('            [" Gamepad fill",        [SetColor, 6]]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "af": (\n')
        new_lines.append('            [" Shutdown system", [Leave, True]],\n')
        new_lines.append('            [" Restart UI",      Restart]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ah": (\n')
        new_lines.append('            [" Nmap",      ReadTextFileNmap],\n')
        new_lines.append('            [" Responder logs", ReadTextFileResponder],\n')
        new_lines.append('            [" Wardriving", ReadTextFileWardriving],\n')
        new_lines.append('            [" DNSSpoof",  ReadTextFileDNSSpoof],\n')
        new_lines.append('            [" DaRkb0x",   ReadTextFileInsomnia]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ai": (\n')
        new_lines.append('            [" Start MITM & Sniff", Start_MITM],\n')
        new_lines.append('            [" Stop MITM & Sniff",  Stop_MITM]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "aj": (\n')
        new_lines.append('            [" Start DNSSpoofing",  Start_DNSSpoofing],\n')
        new_lines.append('            [" Select site",        "ak"],\n')
        new_lines.append('            [" Stop DNS&PHP",       Stop_DNSSpoofing]\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "ak": tuple(\n')
        new_lines.append('            [f" {site}", partial(spoof_site, site)]\n')
        new_lines.append('            for site in SITES\n')
        new_lines.append('        ),\n\n')
        
        new_lines.append('        "aw": (\n')
        new_lines.append('            [" Full WiFi Manager", partial(exec_payload, "utilities/wifi_manager_payload")],\n')
        new_lines.append('            [" FAST WiFi Switcher", launch_wifi_manager],\n')
        new_lines.append('            [" INSTANT Toggle 0↔1", quick_wifi_toggle],\n')
        new_lines.append('            [" Switch Interface", switch_interface_menu],\n')
        new_lines.append('            [" Show Interface Info", show_interface_info],\n')
        new_lines.append('            [" WebUI", launch_webui],\n')
        new_lines.append('            [" Route Control", "awr"],\n')
        new_lines.append('        ) if WIFI_AVAILABLE else (\n')
        new_lines.append('            [" WiFi Not Available", lambda: Dialog_info("WiFi system not found\\nRun wifi_manager_payload", wait=True)],\n')
        new_lines.append('        ),\n\n')
        
        skip = True
        continue
    
    if skip and '    }' in line and line.strip() == '}':
        new_lines.append('        "awr": (\n')
        new_lines.append('            [" Show Routing Status", show_routing_status],\n')
        new_lines.append('            [" Switch to WiFi", switch_to_wifi],\n')
        new_lines.append('            [" Switch to Ethernet", switch_to_ethernet],\n')
        new_lines.append('            [" Interface Switcher", launch_interface_switcher]\n')
        new_lines.append('        ),\n')
        new_lines.append('    }\n')
        skip = False
        continue
        
    if not skip:
        # 2. Fix the button handling (use KEY1, KEY2, KEY3)
        if 'if btn == "KEY_DOWN_PIN":' in line:
            new_lines.append('        if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        elif 'elif btn == "KEY_UP_PIN":' in line:
            new_lines.append('        elif btn == "KEY_UP_PIN" or btn == "KEY1_PIN":\n')
        elif 'elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN"):' in line:
            new_lines.append('        elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN", "KEY2_PIN"):\n')
        # Also fix similar logic in GetMenuGrid and GetMenuCarousel if they differ
        elif 'if btn == "KEY_LEFT_PIN":' in line:
             new_lines.append('        if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":\n')
        elif 'elif btn == "KEY_RIGHT_PIN":' in line:
             new_lines.append('        elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":\n')
        # Skip the original KEY1_PIN/KEY3_PIN logic since we re-mapped them
        elif 'elif btn == "KEY1_PIN" and m.which == "a":' in line:
            continue
        elif 'toggle_view_mode()' in line and 'elif' not in line:
             continue
        elif 'elif btn == "KEY3_PIN" and m.which == "a":' in line:
            continue
        elif '_handle_main_menu_key3_double_click()' in line:
            continue
        else:
            new_lines.append(line)

with open(PATH, 'w') as f:
    f.writelines(new_lines)
print("Menu and buttons updated successfully")
