import os

with open('darkbox_fixed_v2.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'if index < total:\\n' in line:
        new_lines.append('            if index < total:\n')
        new_lines.append('                m.select = index\n')
        new_lines.append('                return inlist[index] if not duplicates else inlist[index].split("#", 1)[1]\n')
    else:
        new_lines.append(line)

with open('darkbox_final.py', 'w') as f:
    f.writelines(new_lines)
print("Final repair complete.")
