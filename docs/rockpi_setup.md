# Raspi Setup - Ohne fertiges Image

## Image
* Balena Etcher installieren
* Armbian Buster Mainline Kernel für Rock Pi 4B auf SD-Karte brennen

## Rock Pi 4b
* SD-Karte einstecken und hochfahren
* Einrichten (Admin User wurde localspeech genannt)
* Anmelden
* Am Computer: `ssh localspeech@rockpi-4b` (kann jetzt ferngesteuert werden)
* Keyboard-Layout umstellen: `sudo dpkg-reconfigure keyboard-configuration`
* Password ändern: `passwd`

## Dependencies
```bash
    wget -q https://ftp-master https://ftp-master.debian.org/keys/release-10.asc -O- | sudo apt-key add
    echo "deb http://deb.debian.org/debian buster non-free" | sudo tee -a /etc/apt/sources.list
    sudo apt update
    sudo apt upgrade
    sudo apt install git libespeak-dev libsdl2-dev libsdl2-mixer-dev python3 python3-pip python3-virtualenv python3-numpy nodejs npm default-jre zip portaudio19-dev gfortran libatlas-base-dev libblas-dev liblapack-dev libblis-dev libpython3-dev lirc youtube-dl libttspico-utils sox
```


## Local Speech User
```bash
    sudo adduser local-speech
    sudo mkhomedir_helper local-speech
    sudo usermod -a -G audio local-speech
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


## MaryTTS installieren (optional)
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
    ./install_rockpi.sh
```

## Install LIRC
(as localspeech)

```bash
    sudo armbian-config
    # System -> Bootenv -> Insert following lines
    # dtoverlay=gpio-ir-tx,gpio_pin=146
    # dtoverlay=gpio-ir,gpio-pin=150
    sudo nano /etc/modules-load.d/gpio-ir-tx.conf
    # Insert: gpio-ir-tx gpio_pin=146
    cd /home/local-speech/raspi-smart-office
    sudo LIRC_PIN=3 ./install-lirc.sh
    cd /etc/lirc/lircd.conf.d
    sudo touch samsung.conf
    sudo wget -O samsung.conf http://lirc.sourceforge.net/remotes/samsung/BN59-00940A
```
The different config files can be found under http://lirc.sourceforge.net/remotes/

## Optional: Set default audio device
(as localspeech)
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

## Auto-Login
(as localspeech)
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
    python3 wait.py && ./update_rockpi.sh && cd master && ./start.sh && sudo shutdown 0
fi
```
Insert for slave device:
```bash
if [ $(tty) = "/dev/tty1" ] ; then
    cd /home/local-speech/marytts-installer
    ./marytts &
    cd ../raspi-smart-office
    python3 wait.py && ./update_rockpi.sh && cd slave && ./start.sh && sudo shutdown 0
fi
```
## Auto-Start for both slave and master on one device:
(as local-speech)
```bash
    cd
    nano start2.sh
    chmod u+x start2.sh
```
Insert:
```bash
    cd master
    ./start.sh &
    cd ..
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
    python3 wait.py && ./update_rockpi.sh && ../start2.sh && python3 wait.py && cd slave && ./start.sh && sudo shutdown 0
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