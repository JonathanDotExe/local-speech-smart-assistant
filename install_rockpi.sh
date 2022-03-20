mkdir venv
python3 -m virtualenv --python=python3 ./venv
mkdir master/data
mkdir master/data/plugins
 mkdir libs
cd libs
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-cp37-cp37m-linux_aarch64.whl
cd ..
source venv/bin/activate
pip install libs/deepspeech-0.9.3-cp37-cp37m-linux_aarch64.whl
./update_rockpi.sh
