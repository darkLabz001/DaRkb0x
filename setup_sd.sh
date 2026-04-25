#!/bin/bash
set -e

IMG="/home/sinxneo/projects/pizero/kali-rpi-zero.img.xz"
DEV="/dev/sda"

if [ "$EUID" -ne 0 ]; then
  echo "Please run this script with sudo."
  exit 1
fi

echo "Unmounting any existing partitions on $DEV..."
umount ${DEV}1 2>/dev/null || true
umount ${DEV}2 2>/dev/null || true

echo "Flashing Kali Linux image to $DEV (this will take a few minutes)..."
xzcat "$IMG" | dd of="$DEV" bs=4M status=progress conv=fsync

echo "Flashing complete. Ensuring changes are synced..."
sync
sleep 3
partprobe "$DEV"
sleep 3

echo "Mounting partitions..."
mkdir -p /mnt/rpi_boot /mnt/rpi_root
mount ${DEV}1 /mnt/rpi_boot
mount ${DEV}2 /mnt/rpi_root

echo "Enabling SSH..."
touch /mnt/rpi_boot/ssh

echo "Enabling SPI in config.txt..."
sed -i 's/^#dtparam=spi=on/dtparam=spi=on/' /mnt/rpi_boot/config.txt
if ! grep -q "^dtparam=spi=on" /mnt/rpi_boot/config.txt; then
    echo "dtparam=spi=on" >> /mnt/rpi_boot/config.txt
fi

echo "Setting up Wi-Fi (wpa_supplicant)..."
cat << 'EOF' > /mnt/rpi_boot/wpa_supplicant.conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={
    ssid="WentzATTNetwork"
    psk="Mater4<34ever"
    key_mgmt=WPA-PSK
}
EOF

echo "Setting up Wi-Fi (NetworkManager)..."
mkdir -p /mnt/rpi_root/etc/NetworkManager/system-connections/
cat << 'EOF' > /mnt/rpi_root/etc/NetworkManager/system-connections/WentzATTNetwork.nmconnection
[connection]
id=WentzATTNetwork
type=wifi
interface-name=wlan0

[wifi]
mode=infrastructure
ssid=WentzATTNetwork

[wifi-security]
auth-alg=open
key-mgmt=wpa-psk
psk=Mater4<34ever

[ipv4]
method=auto

[ipv6]
addr-gen-mode=default
method=auto

[proxy]
EOF
chmod 600 /mnt/rpi_root/etc/NetworkManager/system-connections/WentzATTNetwork.nmconnection

echo "Copying DaRkb0x repository to the Pi..."
mkdir -p /mnt/rpi_root/home/kali/DaRkb0x
rsync -av --exclude='*.img.xz' /home/sinxneo/projects/pizero/ /mnt/rpi_root/home/kali/DaRkb0x/
chown -R 1000:1000 /mnt/rpi_root/home/kali/DaRkb0x

echo "Ensuring USB Host Mode is active (NO gadget mode)..."
sed -i 's/modules-load=dwc2,g_ether //g' /mnt/rpi_boot/cmdline.txt || true
sed -i 's/ modules-load=dwc2,g_ether//g' /mnt/rpi_boot/cmdline.txt || true
sed -i '/dtoverlay=dwc2/d' /mnt/rpi_boot/config.txt || true

echo "Unmounting partitions..."
umount /mnt/rpi_boot
umount /mnt/rpi_root

echo "=========================================================="
echo "DONE! The SD card is fully configured."
echo "Your USB dongles WILL work, and Wi-Fi is set to connect automatically."
echo "You can now safely eject the SD card and plug it into the Pi Zero."
echo "=========================================================="
