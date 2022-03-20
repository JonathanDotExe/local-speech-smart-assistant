import configparser
import os.path

class ClientConfiguration:

    def __init__(self, parser) -> None:
        self.local_path = parser.get('local_path', 'data')

        self.user = configparser.ConfigParser()
        self.user.read(os.path.join(self.local_path, 'config.ini'))

        userconfig = self.user['DEFAULT']
        #Speech/Slave
        self.deepspeech_path =                self.get_config_value(userconfig, parser, 'deepspeech_path', 'data/deepspeech')
        self.model_path =                     self.get_config_value(userconfig, parser, 'model_folder', 'data/deepspeech/models')
        self.scorer_path =                    self.get_config_value(userconfig, parser, 'scorer_folder', 'data/deepspeech/scorers')
        self.model =                          self.get_config_value(userconfig, parser, 'model', 'de_aashishag_model.pbmm')
        self.scorer =                         self.get_config_value(userconfig, parser, 'scorer', 'de_pocolm_large.scorer')
        self.input_device =                   self.get_config_value(userconfig, parser, 'input_device', 'None')
        self.input_device =                   self.get_config_value(userconfig, parser, 'input_device', None)
        try:
            self.input_device = int(self.input_device)
        except:
            self.input_device = None
        self.wakeword =                       self.get_config_value(userconfig, parser, 'wakeword', 'computer')
        self.language =                       self.get_config_value(userconfig, parser, 'language', 'de')
        self.api_url =                        self.get_config_value(userconfig, parser, 'api_url', 'http://localhost:8080')
        self.allow_text_input =               self.get_config_value(userconfig, parser, 'allow_text_input', 'True') == 'True'
        self.tts =                            self.get_config_value(userconfig, parser, 'tts', 'True') == 'True'
        self.tts_engine =                     self.get_config_value(userconfig, parser, 'tts_engine', 'picotts')
        self.encryption_word =                self.get_config_value(userconfig, parser, 'encryption_word', 'AUTH_WORD')
        self.noise_gate =               float(self.get_config_value(userconfig, parser, 'noise_gate', '0.03'))
        self.name =                           self.get_config_value(userconfig, parser, 'name', 'Local Speech Slave')
        self.active_beam_width =          int(self.get_config_value(userconfig, parser, 'active_beam_width', '1000'))
        self.active_record_time_out =   float(self.get_config_value(userconfig, parser, 'active_record_time_out', '2.0'))
        self.wakeword_beam_width =        int(self.get_config_value(userconfig, parser, 'wakeword_beam_width', '200'))
        self.wakeword_record_time_out = float(self.get_config_value(userconfig, parser, 'wakeword_record_time_out', '0.5'))
        #API
        self.api_data_path =                  self.get_config_value(userconfig, parser, 'api_data_path', 'data/api')
        self.default_password =               self.get_config_value(userconfig, parser, 'default_password', 'password')
        self.port =                       int(self.get_config_value(userconfig, parser, 'port', '8070'))
        self.reboot_cmd =                     self.get_config_value(userconfig, parser, 'reboot_cmd', 'reboot')
        self.allow_reboot =                   self.get_config_value(userconfig, parser, 'allow_reboot', 'True') == 'True'

        self.ignore_ssl_certificate =         self.get_config_value(userconfig, parser, 'ignore_ssl_certificate', 'True') == 'True'
        self.speech_server =                  self.get_config_value(userconfig, parser, 'speech_server', '')

    def get_config_value(self, parser1, parser2, name: str, default_value: str) -> str:
        value =  parser1.get(name, None)
        if value is None:
            value = parser2.get(name, default_value)
        return value

    def set_model(self, model: str):
        self.user['DEFAULT']['model'] = model
    
    def set_scorer(self, scorer: str):
        self.user['DEFAULT']['scorer'] = scorer

    def set_wakeword(self, wakeword: str):
        self.wakeword = wakeword
        self.user['DEFAULT']['wakeword'] = wakeword

    def set_noise_gate(self, gate: str):
        self.noise_gate = float(gate)
        self.user['DEFAULT']['noise_gate'] = gate
    
    def set_language(self, language: str):
        #self.language = language
        self.user['DEFAULT']['language'] = language

    def set_api_url(self, api_url: str):
        self.api_url = api_url
        self.user['DEFAULT']['api_url'] = api_url
    
    def set_speech_server(self, speech_server: str):
        self.speech_server = speech_server
        self.user['DEFAULT']['speech_server'] = speech_server
    
    def set_name(self, name: str):
        self.name = name
        self.user['DEFAULT']['name'] = name
    
    def set_wakeword_beam_width(self, arg: str):
        self.wakeword_beam_width = int(arg)
        self.user['DEFAULT']['wakeword_beam_width'] = arg
    
    def set_wakeword_record_time_out(self, arg: str):
        self.wakeword_record_time_out = float(arg)
        self.user['DEFAULT']['wakeword_record_time_out'] = arg
    
    def set_active_beam_width(self, arg: str):
        self.active_beam_width = int(arg)
        self.user['DEFAULT']['active_beam_width'] = arg
    
    def set_active_record_time_out(self, arg: str):
        self.active_record_time_out = float(arg)
        self.user['DEFAULT']['active_record_time_out'] = arg
    
    def save_user(self):
        try:
            with open(os.path.join(self.local_path, 'config.ini'), 'w') as f:
                self.user.write(f)
        except:
            print("Couldn't save user config")
    
        
