#!/bin/sh

git clone -q https://github.com/respeaker/usb_4_mic_array.git mic-config
cd mic-config
git checkout -q b0410c728c91376bfc8e8ae76da2f54192349ce1
python dfu.py --download 1_channel_firmware.bin
cd ..
rm -rf mic-config

