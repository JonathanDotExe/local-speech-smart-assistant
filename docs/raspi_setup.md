# Raspi Setup - Ohne fertiges Image

## Image
* Raspberry Pi Imager installieren
* Raspberry Pi OS Lite (32 Bit) auf SD-Karte brennen

## Rasperry Pi
* SD-Karte einstecken und hochfahren
* Anmelden
* `sudo raspi-config`
* Interfaces -> SSH aktivieren
* Localisation -> Locale setzen
* Am Computer: `ssh pi@raspberrypi` (kann jetzt ferngesteuert werden)
* Keyboard-Layout umstellen: `sudo dpkg-reconfigure keyboard-configuration`
* Password ändern: `passwd`

## Dependencies
```bash
    sudo apt update
    sudo apt upgrade
    sudo apt install git libespeak-dev libsdl2-dev libsdl2-mixer-dev python3 python3-pip python3-virtualenv nodejs npm default-jre zip portaudio19-dev libttspico-utils sox libatlas-base-dev lirc 
```

# Install RUST
(as loca-speech)
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```
https://www.rust-lang.org/tools/install
Added `. "$HOME/.cargo/env"` line to .profile of local-speech

## Local Speech User
```bash
    sudo adduser local-speech
```

## USB - Gruppe für Speaker
```bash
    sudo groupadd usbdev
    sudo usermod -a -G usbdev local-speech
    cd /etc/udev/rules.d/
    sudo nano usbdev.rules
```
Insert:
```
SUBSYSTEM=="usb", MODE="0660", GROUP="usbdev"
```


## MaryTTS installieren
(as local-speech)
```bash
    git clone https://github.com/marytts/marytts-installer
    cd marytts-installer
    ./marytts list
    ./marytts install voice-bits3-hsmm
```

## Install Local Speech
(as local-speech)
```bash
    git clone [url]
    mv HTL%20Diplomarbeit%20-%20Spracherkennung/ raspi-smart-office
    cd raspi-smart-office/
    ./install.sh
```

## Install LIRC
(as pi)

```bash
    sudo nano /boot/config.txt
    # Insert
    dtoverlay=gpio-ir,gpio_out_pin=27
    dtoverlay=gpio-ir-tx,gpio_pin=17

    cd /etc/lirc/
    sudo nano lirc_options.conf
    Update lines
    driver          = default  
    device          = /dev/lirc1

    cd lircd.conf.d
    sudo touch samsung.conf
    sudo wget -O samsung.conf http://lirc.sourceforge.net/remotes/samsung/BN59-00940A
    
    mode2 --driver default --device /dev/lirc1 #For recieving
```
Excute LIRC patch from https://blog.gc2.at/post/ir/#
Pins for our reciver (left to right): GND 3V3 GPIO27
https://daniel-ziegler.com/arduino/esp/mikrocontroller/2017/07/28/arduino-universalfernbedienung/
https://www.mythtv.org/wiki/FTDI_USB_IR_Blaster_/_Transmitter_using_LIRC

The different config files can be found under http://lirc.sourceforge.net/remotes/

## Record remote
bash`
    sudo irrecord -H default -d /dev/lirc1 --disable-namespace
    sudo cp Goove_LED.lircd.conf /etc/lirc/lircd.conf.d
`

## Optional: Set default audio device
(as pi)
* `aplay -l` zum sehen der Audio-Karten
* `sudo nano /usr/share/alsa/alsa.conf`
* Diese Zeilen auf den Index der Audio-Karte setzen:
```
    defaults.ctl.card 2
    defaults.pcm.card 2  
    defaults.pcm.device 0
```
* Lautstärke bei `alsamixer` anpassen
* Sensitivität evtl in config file anpassen

Source: https://superuser.com/questions/989385/how-to-make-raspberry-pi-use-an-external-usb-sound-card-as-a-default

## Use HDMI Port
* `sudo nano /boot/config.txt`
* `hdmi_force_hotplug=1` entkommentieren

## Auto-Login
(as pi)
```bash
    sudo mkdir /etc/systemd/system/getty@tty1.service.d
    sudo nano /etc/systemd/system/getty@tty1.service.d/override.conf
```
Insert:
```
    [Service]
    ExecStart=
    ExecStart=-/sbin/agetty --autologin local-speech --noclear %I $TERM
    Type=idle
```

## Reboot/Shutdown privileges
`sudo nano /etc/sudoers.d/shutdown`
Insert:
```
    local-speech ALL = NOPASSWD: /sbin/halt, /sbin/poweroff, /sbin/shutdown, /sbin/reboot
```

https://unix.stackexchange.com/questions/85663/poweroff-or-reboot-as-normal-user

## Auto-Start
(as local-speech)
```bash
    cd
    nano .profile
```
Insert for master device:
```bash
if [ $(tty) = "/dev/tty1" ] ; then
    cd /home/local-speech/raspi-smart-office
    python3 wait.py && ./update.sh && cd master && ./start.sh && sudo shutdown 0
fi
```
Insert for slave device:
```bash
if [ $(tty) = "/dev/tty1" ] ; then
    cd /home/local-speech/marytts-installer
    ./marytts &
    cd ../raspi-smart-office
    python3 wait.py && ./update.sh && cd slave && ./start.sh && sudo shutdown 0
fi
```
## Auto-Start for both slave and master on one device:
(as local-speech)
```bash
    cd
    nano start2.sh
```
Insert:
```bash
    cd raspi-smart-office
    cd master
    ./start.sh &
    cd ../..
```
```bash
    cd
    nano .profile
```
Insert:
```bash
if [ $(tty) = "/dev/tty1" ] ; then
    cd /home/local-speech/marytts-installer
    ./marytts &
    cd ../raspi-smart-office
    python3 wait.py && ./update.sh && ../start2.sh && python3 wait.py && cd slave && ./start.sh && sudo shutdown 0
fi
```


# Raspi Setup - mit fertigen Image
## Image
* Balena Etcher installieren
* Image auf SD-Karte brennen

## Remote setzen
* Mit `ssh local-speech@raspberrypi` (Passwort: password1234)
* `cd raspi-smart-office`
* `git remote set-url origin [url]`