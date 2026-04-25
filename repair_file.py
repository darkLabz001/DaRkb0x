import os
import sys

# 1. READ THE WHOLE FILE
with open('darkbox.py.bak', 'r') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # FIX INDENTATION IN _enter_pin_via_keypad (around line 1210)
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

    # FIX GetMenuString logic (around line 2180)
    if 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":' in line and i > 2100 and i < 2250:
        new_lines.append('        if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        new_lines.append('            index = (index + 1) % total\n')
        new_lines.append('        elif btn == "KEY_UP_PIN" or btn == "KEY1_PIN":\n')
        new_lines.append('            index = (index - 1) % total\n')
        new_lines.append('        elif btn in ("KEY_PRESS_PIN", "KEY_RIGHT_PIN", "KEY2_PIN"):\n')
        # Skip next few lines of original broken logic
        i += 1
        while i < len(lines) and 'if btn == "KEY_LEFT_PIN"' not in lines[i]:
            i += 1
        continue
    
    if 'if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":' in line and i > 2100 and i < 2250:
        new_lines.append('        elif btn == "KEY_LEFT_PIN":\n') # Keep original behavior for back
        i += 1
        continue

    # FIX GetMenuCarousel (around line 4300)
    if 'if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":' in line and i > 4250 and i < 4350:
        new_lines.append('        if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":\n')
        new_lines.append('            index = (index - 1) % total\n')
        new_lines.append('        elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":\n')
        new_lines.append('            index = (index + 1) % total\n')
        new_lines.append('        elif btn == "KEY_UP_PIN":\n')
        i += 1
        while i < len(lines) and 'if btn == "KEY_DOWN_PIN"' not in lines[i]:
            i += 1
        continue
    if 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":' in line and i > 4250 and i < 4350:
        new_lines.append('        elif btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        i += 1
        continue

    # FIX GetMenuGrid (around line 4400)
    if 'if btn == "KEY_UP_PIN":' in line and i > 4380 and i < 4450:
        new_lines.append('        if btn == "KEY_UP_PIN" or btn == "KEY1_PIN":\n')
        i += 1
        continue
    if 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":' in line and i > 4380 and i < 4450:
        new_lines.append('        elif btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
        i += 1
        continue
    if 'if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":' in line and i > 4380 and i < 4450:
        new_lines.append('        elif btn == "KEY_LEFT_PIN":\n')
        i += 1
        continue
    if 'elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":' in line and i > 4380 and i < 4450:
        new_lines.append('        elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":\n')
        i += 1
        continue

    # FIX main loop (around line 4480) - ensure auto-pilot doesn't loop
    if 'subprocess.Popen(["python3", "/home/kali/DaRkb0x/payloads/insomnia_suite/insomnia_auto.py"])' in line:
        # Check if we are in main()
        if i > 4450:
             i += 1 # Skip the extra popen in main()
             continue

    new_lines.append(line)
    i += 1

with open('darkbox_fixed.py', 'w') as f:
    f.writelines(new_lines)
print("File repaired locally.")
