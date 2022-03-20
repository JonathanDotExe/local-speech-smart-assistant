#!/bin/bash
if [[ -v LIRC_PIN ]]
then

apt-get install lirc -y
cat >> /etc/modules << EOF
lirc_dev
lirc_rpi gpio_out_pin=$LIRC_PIN
EOF
cat >> /etc/lirc/hardware.conf << EOF
LIRCD_ARGS="--uinput"
LOAD_MODULES=true
DRIVER="default"
DEVICE="/dev/lirc0"
MODULES="lirc_rpi"
LIRCD_CONF=""
LIRCMD_CONF=""
EOF
cat >> /boot/config.txt << EOF
dtoverlay=lirc-rpi,gpio_out_pin=$LIRC_PIN
EOF

else

echo "The environment variable 'LIRC_PIN' needs to be set to the pin at which the IR LED is connected!"
echo "To set it directly, run this script as follows:"
echo "  LIRC_PIN=<pin> sudo ./install-lirc.sh"
echo "To find the placement of GPIO pins use 'pinout'"
fi
