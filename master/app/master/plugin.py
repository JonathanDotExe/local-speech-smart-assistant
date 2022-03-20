from master.command import * 
import importlib.util
import os
import os.path
import configparser
import zipfile
import zipimport
import json
import copy
import traceback

def load_plugin(folder: str, filename: str) -> None:
    #Load plugin
    plugin: Plugin = None
    try:
        with zipfile.ZipFile(folder, 'r') as zip:
            with zip.open('plugin.ini') as f:
                #Load config
                conf = configparser.ConfigParser()
                conf.read_string(f.read().decode('utf-8'))
                
                main = conf['DEFAULT']['main']
                module = conf['DEFAULT']['module']

                print(module)

                #Load file
                imp = zipimport.zipimporter(folder)
                mod = imp.load_module(module)

                main_class = getattr(mod, main)
                plugin = main_class()
    except:
        text = traceback.format_exc()
        print(text)
        plugin = InvalidPlugin()
        plugin.description = text
    plugin.filename = filename    
    #Config
    try:
        with open(os.path.splitext(folder)[0] + '.json', 'r') as f:
            js = json.loads(f.read())
            plugin.active = bool(js.get('active', True))
            plugin.config.update(js.get('config', plugin.config))
    except:
        pass
    return plugin

def load_plugins(folder: str):
    #List files
    plugins = []
    for plugin in os.listdir(folder):
        if plugin.endswith('.zip'):
            plugins.append(load_plugin(os.path.join(folder, plugin), plugin))
    return plugins

class Plugin:

    def __init__(self):
        self.name = ""
        self.description = ""
        self.filename = ""
        self.commands: [Command] = []
        self.active = True
        self.config = {}
        self.html = ""
    
    def to_json(self):
        return {
            'name': self.name,
            'description': self.description,
            'filename': self.filename,
            'active': self.active,
            'config': copy.deepcopy(self.config),
            'html': self.html,
            'commands': [*map(lambda c : {
                'name': c.name,
                'description': c.description,
                'aliases': c.aliases
            }, self.commands)]
        }
    
    def endpoint(self, path: str):
        return "Endpoint not found", 404

class InvalidPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.name = "Invalid"
        self.description = "An invalid plugin that couldn't be loaded properly!"
    