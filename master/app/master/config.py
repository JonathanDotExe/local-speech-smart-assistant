import configparser
import os

class ServerConfiguration:

    def __init__(self, parser) -> None:
        self.local_path = parser.get('local_path', 'data')

        self.user = configparser.ConfigParser()
        self.user.read(os.path.join(self.local_path, 'config.ini'))

        userconfig = self.user['DEFAULT']

        self.default_password = self.get_config_value(userconfig, parser, 'default_password', 'password')
        self.port =             self.get_config_value(userconfig, parser, 'port', 8080)
        try:
            self.port = int(self.port)
        except:
            self.port = 8080
        self.debug =            self.get_config_value(userconfig, parser, 'debug', 'True') == 'True'
        self.allow_reboot =     self.get_config_value(userconfig, parser, 'allow_reboot', 'True') == 'True'
        self.reboot_cmd =       self.get_config_value(userconfig, parser, 'reboot_cmd', 'reboot')
        self.max_content_size = self.get_config_value(userconfig, parser, 'max_content_size', 512000)
        try:
            self.max_content_size = int(self.max_content_size)
        except:
            self.max_content_size = 512000
        self.encryption_word =  self.get_config_value(userconfig, parser, 'encryption_word', 'AUTH_WORD')
        self.plugin_path =      self.get_config_value(userconfig, parser, 'plugin_path', 'data/plugins')
        self.db_path =          self.get_config_value(userconfig, parser, 'db_path', 'data/database.db')
        self.sql_path =         self.get_config_value(userconfig, parser, 'sql_path', 'resources/import.sql')

    def get_config_value(self, parser1, parser2, name: str, default_value: str) -> str:
        value =  parser1.get(name, None)
        if value is None:
            value = parser2.get(name, default_value)
        return value
