import sys
import os

PATH = '/home/kali/DaRkb0x/darkbox.py'
with open(PATH, 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
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
        # Also update ah menu to include insomnia
        if '[" Nmap",      ReadTextFileNmap],' in line:
             new_lines.append('            [" DaRkb0x",   ReadTextFileInsomnia],\n')
        new_lines.append(line)

with open(PATH, 'w') as f:
    f.writelines(new_lines)
print("Menu updated successfully")
