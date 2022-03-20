#!/bin/sh

git clone https://github.com/coqui-ai/TTS TTS
cd TTS
git checkout 540d811
pip install -r requirements.txt
python setup.py install