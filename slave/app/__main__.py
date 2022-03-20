from slave.recorder import * 
from slave.speech import * 
from slave.client import * 
from slave.config import *
from slave.api import *
import sys
import configparser
import os.path
import urllib3

FAIL = '\033[91m'
BOLD = '\033[1m'
ENDC = '\033[0m'

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    profile = 'Development'
    if len(sys.argv) > 1:
        profile = sys.argv[1]
    #Load config
    conf = configparser.ConfigParser()
    try:
        conf.read('client_config.ini')
    except Exception as e:
        print(e)
        print('No configration was found')


    print(profile, " ", conf.sections())
    if profile in conf.sections():
        config = ClientConfiguration(conf[profile])
    else:
        config = ClientConfiguration({})

    os.makedirs(config.local_path, exist_ok=True)
    os.makedirs(config.api_data_path, exist_ok=True)
    os.makedirs(config.deepspeech_path, exist_ok=True)
    os.makedirs(config.model_path, exist_ok=True)
    os.makedirs(config.scorer_path, exist_ok=True)
    #Init app
    handler = SpeechHandler(os.path.join(config.model_path, config.model), os.path.join(config.scorer_path, config.scorer))
    if handler.invalid_model:
        print(FAIL + BOLD + '----Loaded invalid model file! Voice recognition disabled----' + ENDC)
    if handler.invalid_scorer:
        print(FAIL + BOLD + '----Loaded invalid scorer file! Voice recognition disabled----'+ ENDC)
    recorder = SpeechRecorder(config.input_device, config.noise_gate)
    client = SpeechClient(handler, recorder, config)
    api = SlaveServer(client, config)
    api.run()

if __name__ == "__main__":
    main()