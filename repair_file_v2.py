import os
import sys

# 1. READ THE ORIGINAL BACKUP (the one we downloaded from the Pi before my broken local fix)
with open('darkbox.py.bak', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # --- 1. Fix Indentation in _enter_pin_via_keypad ---
    if 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":' in line and i > 1200 and i < 1250:
        new_lines.append('            elif btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        i += 1
        continue
    if 'if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":' in line and i > 1200 and i < 1250:
        new_lines.append('            elif btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":\n')
        i += 1
        continue
    if 'elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":' in line and i > 1200 and i < 1250:
        new_lines.append('            elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":\n')
        i += 1
        continue

    # --- 2. Fix GetMenuString logic (ListView) ---
    if 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":' in line and i > 2150 and i < 2200:
        new_lines.append('        if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        new_lines.append('            index = (index + 1) % total\n')
        new_lines.append('        elif btn == "KEY_UP_PIN" or btn == "KEY1_PIN":\n')
        new_lines.append('            index = (index - 1) % total\n')
        new_lines.append('        elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN", "KEY2_PIN"):\n')
        new_lines.append('            raw = inlist[index]\n')
        new_lines.append('            if empty: return (-2, "") if duplicates else ""\n')
        new_lines.append('            if duplicates:\n')
        new_lines.append('                idx, txt = raw.split("#", 1)\n')
        new_lines.append('                return int(idx), txt\n')
        new_lines.append('            return raw\n')
        new_lines.append('        elif btn == "KEY_LEFT_PIN":\n')
        new_lines.append('            return (-1, "") if duplicates else ""\n')
        
        # Skip the original broken block until we reach the next function or section
        i += 1
        while i < len(lines) and '### Draw up down triangles ###' not in lines[i]:
            i += 1
        continue

    # --- 3. Fix GetMenuCarousel ---
    if 'if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":' in line and i > 4250 and i < 4350:
        new_lines.append('        if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":\n')
        new_lines.append('            index = (index - 1) % total\n')
        new_lines.append('        elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":\n')
        new_lines.append('            index = (index + 1) % total\n')
        new_lines.append('        elif btn == "KEY_UP_PIN":\n')
        new_lines.append('            index = (index - 1) % total\n')
        new_lines.append('        elif btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        new_lines.append('            index = (index + 1) % total\n')
        new_lines.append('        elif btn == "KEY_PRESS_PIN":\n')
        new_lines.append('            if index < total:\n')
        new_lines.append('                m.select = index\n')
        new_lines.append('                return inlist[index] if not duplicates else inlist[index].split("#", 1)[1]\n')
        
        # Skip original broken block
        i += 1
        while i < len(lines) and 'def GetMenuGrid' not in lines[i]:
            i += 1
        continue

    # --- 4. Fix GetMenuGrid ---
    if 'if btn == "KEY_UP_PIN":' in line and i > 4400 and i < 4450:
        new_lines.append('        if btn == "KEY_UP_PIN" or btn == "KEY1_PIN":\n')
        new_lines.append('            if index >= GRID_COLS: index -= GRID_COLS\n')
        new_lines.append('        elif btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        new_lines.append('            if index + GRID_COLS < total: index += GRID_COLS\n')
        new_lines.append('        elif btn == "KEY_LEFT_PIN":\n')
        new_lines.append('            if index > 0 and index % GRID_COLS != 0: index -= 1\n')
        new_lines.append('        elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":\n')
        new_lines.append('            if index < total - 1 and (index + 1) % GRID_COLS != 0: index += 1\n')
        new_lines.append('        elif btn == "KEY_PRESS_PIN":\n')
        
        # Skip original broken block
        i += 1
        while i < len(lines) and 'def toggle_view_mode' not in lines[i]:
            i += 1
        continue

    # --- 5. Remove duplicate auto-pilot launch ---
    if 'subprocess.Popen(["python3", "/home/kali/DaRkb0x/payloads/insomnia_suite/insomnia_auto.py"])' in line:
        if i > 4450: # The one in main()
             i += 1
             continue

    new_lines.append(line)
    i += 1

with open('darkbox_fixed_v2.py', 'w') as f:
    f.writelines(new_lines)
print("File repaired locally (v2).")
