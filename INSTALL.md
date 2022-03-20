# Create virtual env
## Install Python 3.7/3.6 using this tutorial:
https://linuxize.com/post/how-to-install-python-3-7-on-ubuntu-18-04/
sudo apt install python3.7-dev

## Create virtualenv:
python3.7 -m pip install virtualenv
virtualenv --python=python3.7 ./
source ./bin/activate

## Install dependencies
Go into project folder
sudo apt install pkg-config libcairo2-dev gcc python3-dev libgirepository1.0-dev libvlc-dev
pip install --upgrade -r requirements.txt

## Run server
python main.py

## Run client
python slave_main.py
