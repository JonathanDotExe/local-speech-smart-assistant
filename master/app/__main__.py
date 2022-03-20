from master.assistant import * 
from master.plugin import * 
from master.api.audioserver import * 
from master.config import *
import sys
import configparser
import os.path
import urllib3

def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    #Load config
    profile = 'Development'
    if len(sys.argv) > 1:
        profile = sys.argv[1]
    #Load config
    conf = configparser.ConfigParser()
    try:
        conf.read('server_config.ini')
    except:
        print('No configration was found')

    if profile in conf.sections():
        config = ServerConfiguration(conf[profile])
    else:
        config = ServerConfiguration({})

    os.makedirs(config.local_path, exist_ok=True)
    os.makedirs(config.plugin_path, exist_ok=True)

    #Create assitant
    assistant = SmartAssistant(config)
    assistant.start()
    server = AssistantServer(assistant, config)
    server.run()

if __name__ == "__main__":
    main()
