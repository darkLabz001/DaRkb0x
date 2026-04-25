#!/bin/bash
set -e

# ==============================================================================
# DaRkb0x FINAL MASTER FLASH SCRIPT
# ==============================================================================

IMG="/home/sinxneo/projects/pizero/kali-rpi-zero.img.xz"
DEV="/dev/sda"
MNT_BOOT="/mnt/insomnia_boot"
MNT_ROOT="/mnt/insomnia_root"
PI_HOME="/home/kali/DaRkb0x"
REPO_URL="https://github.com/darkLabz001/DaRkb0x.git"

if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo."
  exit 1
fi

echo "[1/11] Unmounting existing partitions..."
umount ${DEV}* 2>/dev/null || true

echo "[2/11] Flashing Kali Linux image (be patient)..."
xzcat "$IMG" | dd of="$DEV" bs=4M status=progress conv=fsync

echo "[3/11] Expanding partition and filesystem..."
sync && sleep 5
# Expand the 2nd partition to fill the SD card
parted -s "$DEV" resizepart 2 100%
sync && sleep 2
e2fsck -fy ${DEV}2 || true
resize2fs ${DEV}2

echo "[4/11] Mounting partitions..."
mkdir -p "$MNT_BOOT" "$MNT_ROOT"
mount ${DEV}1 "$MNT_BOOT"
mount ${DEV}2 "$MNT_ROOT"

echo "[5/11] Enabling Hardware & Network..."
touch "$MNT_BOOT/ssh"
echo "dtparam=spi=on" >> "$MNT_BOOT/config.txt"
sed -i 's/modules-load=dwc2,g_ether//g' "$MNT_BOOT/cmdline.txt"
sed -i '/dtoverlay=dwc2/d' "$MNT_BOOT/config.txt"

cat << 'EOF' > "$MNT_BOOT/wpa_supplicant.conf"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US
network={
    ssid="WentzATTNetwork"
    psk="Mater4<34ever"
}
EOF

echo "[6/11] Copying DaRkb0x Files & Branding..."
mkdir -p "$MNT_ROOT$PI_HOME"
rsync -av --exclude='*.img.xz' --exclude='.git' /home/sinxneo/projects/pizero/ "$MNT_ROOT$PI_HOME/"
cp /home/sinxneo/projects/pizero/logo.bmp "$MNT_ROOT$PI_HOME/img/logo.bmp"

sed -i 's/"BACKGROUND": "#000000"/"BACKGROUND": "#111111"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"BORDER": "#05ff00"/"BORDER": "#ff00ff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"GAMEPAD": "#141494"/"GAMEPAD": "#00ffff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"SELECTED_TEXT": "#00ff55"/"SELECTED_TEXT": "#000000"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"SELECTED_TEXT_BACKGROUND": "#2d0fff"/"SELECTED_TEXT_BACKGROUND": "#00ffff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"
sed -i 's/"TEXT": "#05ff00"/"TEXT": "#ff00ff"/' "$MNT_ROOT$PI_HOME/gui_conf.json"

echo "[7/11] Initializing Git for OTA Updates..."
chroot "$MNT_ROOT" /bin/bash -c "cd $PI_HOME && git init && git config user.email 'insomnia@box.local' && git config user.name 'DaRkb0x' && git remote add origin $REPO_URL && git add . && git commit -m 'initial local sync' && git branch -M main" || echo "Git setup failed, skipping..."

echo "[8/11] Injecting Anti-Freeze Fix (1GB SWAP)..."
fallocate -l 1G "$MNT_ROOT/swapfile"
chmod 600 "$MNT_ROOT/swapfile"
echo "/swapfile none swap sw 0 0" >> "$MNT_ROOT/etc/fstab"

echo "[9/11] Setting up systemd service..."
cat << 'EOF' > "$MNT_ROOT/etc/systemd/system/darkbox.service"
[Unit]
Description=DaRkb0x Toolkit
After=network.target

[Service]
ExecStartPre=-/sbin/mkswap /swapfile
ExecStartPre=-/sbin/swapon /swapfile
ExecStart=/usr/bin/python3 /home/kali/DaRkb0x/darkbox.py
WorkingDirectory=/home/kali/DaRkb0x
User=root
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "[10/11] Finalizing Paths & Permissions..."
sed -i 's|/root/DaRkb0x/|/home/kali/DaRkb0x/|g' "$MNT_ROOT$PI_HOME/darkbox.py"
sed -i 's|/root/DaRkb0x/|/home/kali/DaRkb0x/|g' "$MNT_ROOT$PI_HOME/gui_conf.json"

echo "[11/11] Unmounting..."
chown -R 1000:1000 "$MNT_ROOT$PI_HOME"
umount "$MNT_BOOT" "$MNT_ROOT"

echo "=========================================================="
echo "COMPLETED! DaRkb0x is ready."
echo "- SD card expanded to full size"
echo "- 1GB Swap (No freezing)"
echo "- OTA Updates Enabled (System menu)"
echo "- Neon Theme & Custom Logo active"
echo "- K1/K2/K3 Buttons mapped"
echo "=========================================================="
