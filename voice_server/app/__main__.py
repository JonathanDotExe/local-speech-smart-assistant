from voiceserver import *
import sys
import configparser
import os
import urllib3
import json

def main():
    print(os.getcwd())
    config = {}
    with open('data/config.json') as f:
        config = json.load(f)

    #Init app
    speech = SpeechRecognizer(config)
    api = SpeechServer(speech)
    api.run()

if __name__ == "__main__":
    main()
    