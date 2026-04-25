import sys
import os

def patch_clean():
    with open('darkbox_clean.py', 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_menu = False
    for line in lines:
        # 1. Branding
        if 'install_path = "/root/DaRkb0x/"' in line:
            new_lines.append('    install_path = "/home/kali/DaRkb0x/"\n')
            continue
        
        # 2. Main Menu Restructure
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
            new_lines.append('            [" View Auto Logs",  lambda: Explorer("/home/kali/DaRkb0x/loot/insomnia/", ".log")],\n')
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
            skip_menu = True
            continue
            
        if skip_menu:
            if '        "ag": (' in line:
                skip_menu = False
                new_lines.append(line)
            continue
        
        # 3. Button Mapping (K1, K2, K3)
        if 'if btn == "KEY_DOWN_PIN":' in line:
            new_lines.append('        if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
            continue
        if 'elif btn == "KEY_UP_PIN":' in line:
            new_lines.append('        elif btn == "KEY_UP_PIN" or btn == "KEY1_PIN":\n')
            continue
        if 'elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN"):' in line:
            new_lines.append('        elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN", "KEY2_PIN"):\n')
            continue
            
        new_lines.append(line)
        
    with open('darkbox_final_v3.py', 'w') as f:
        f.writelines(new_lines)
    print("Patch V3 applied.")

if __name__ == '__main__':
    patch_clean()
