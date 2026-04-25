import os

with open('darkbox_recovery.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Fix the _enter_pin_via_keypad indentation
    if 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":' in line and 'elif' not in line and 'row = (row + 1)' in lines[lines.index(line)+1]:
         new_lines.append('            elif btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
    elif 'if btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":' in line and 'elif' not in line and 'col = (col - 1)' in lines[lines.index(line)+1]:
         new_lines.append('            elif btn == "KEY_LEFT_PIN" or btn == "KEY1_PIN":\n')
    elif 'elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":' in line and 'col = (col + 1)' in lines[lines.index(line)+1]:
         new_lines.append('            elif btn == "KEY_RIGHT_PIN" or btn == "KEY2_PIN":\n')
    # Fix the other one in Start_MITM
    elif 'if btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":' in line and 'idx = min(len(options)' in lines[lines.index(line)+1]:
         new_lines.append('                elif btn == "KEY_DOWN_PIN" or btn == "KEY3_PIN":\n')
    else:
        new_lines.append(line)

with open('darkbox_final_fix.py', 'w') as f:
    f.writelines(new_lines)
print("Fix applied.")
