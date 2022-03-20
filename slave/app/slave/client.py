from configparser import ConfigParser
from posix import listdir
from time import sleep
from types import resolve_bases
from numpy.core.shape_base import block
from requests.sessions import session
from slave.speech import *
from slave.util import pixel_ring_wrapper
from slave.config import *
import numpy
import requests
import simpleaudio
import wave
import socketio
import rsa
import json
import base64
import sys
import os
import vlc
import alsaaudio
import time

from slave.recorder import *
import os.path
import threading, queue
import pickle

from slave.tts import *

import traceback

class TaskThread(threading.Thread):

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.daemon = True
        self.task_count = 0
        self.lock = threading.Lock()
    
    def run(self):
        while True:
            try:
                task = self.queue.get(block=True, timeout=1)
                task()
                with(self.lock):
                    self.task_count -= 1
                    self.queue.task_done()
            except queue.Empty:
                pass

    def execute(self, task):
        with(self.lock):
            self.queue.put(task)
            self.task_count += 1

    def execute_if_free(self, task):
        free = False
        with (self.lock):
            if self.task_count <= 0:
                self.queue.put(task)
                self.task_count = 1
                free = True
        return free
    
    def is_free(self):
        free = True
        with (self.lock):
            free = self.task_count <= 0
        return free


class SpeechClient:

    def __init__(self, handler: SpeechHandler, recorder: SpeechRecorder, config: ClientConfiguration):
        self.handler = handler
        self.recorder = recorder
        self.config = config
        self.session = requests.Session()
        recorder.submit = self.submit
        self.task_thread = TaskThread()
        self.speech_thread = TaskThread()
        self.apply_wakeword_config()
        self.curr_stmt = -1
        self.config = config
        self.models = []
        self.scorers = []
        self.future_model = None
        self.future_scorer = None
        self.vlc = None

        try:
            mixer = alsaaudio.Mixer()
            volume = mixer.getvolume()
            if volume[0] < 10:
                mixer.setvolume(10)
        except alsaaudio.ALSAAudioError:
            print("Couldn't set volume! No mixer was found for the audio device!")

        with wave.open('resources/wake_up.wav') as wav:
            self.wakeup_sound = simpleaudio.WaveObject.from_wave_read(wav)

        pixel_ring_wrapper.off()

        self.tts_engine = None
        if self.config.tts:
            if self.config.tts_engine == 'marytts':
                self.tts_engine = MaryTTSEngine()
            elif self.config.tts_engine == 'espeak':
                self.tts_engine = ESpeakEngine()
            else:
                self.tts_engine = PicoTTSEngine()
            self.tts_engine.set_voice(self.config.language)
        self.session_lock = threading.Lock()
        self.active = False
        #WebSocket
        self.mute_disconnect = False
        self.ws = socketio.Client(reconnection=False, http_session=self.session, ssl_verify=not self.config.ignore_ssl_certificate)
        @self.ws.on('command')
        def on_command(data): #Does not use session hopefully
            self.task_thread.execute(lambda : self.handle_broadcast(data))
        @self.ws.event
        def disconnect(): #Disconnect from server
            self.active = False
            if not self.mute_disconnect:
                def speak():
                    self.tts("Die Verbindung zum Master wurde unterbrochen!" if self.config.language == 'de' else "Lost connection to master!")
                self.task_thread.execute(speak)

        #Load Key Pair
        self.pubkey = None
        self.privkey = None
        path = os.path.join(self.config.local_path, 'private_key.pem')
        if os.path.isfile(path):
            with open(path, mode='rb') as privatefile:
                keydata = privatefile.read()
            self.privkey = rsa.PrivateKey.load_pkcs1(keydata)
            print("Loaded private key")
        path = os.path.join(self.config.local_path, 'public_key.pem')
        if os.path.isfile(path):
            with open(path, mode='rb') as publicfile:
                keydata = publicfile.read()
            self.pubkey = rsa.PublicKey.load_pkcs1(keydata)
            print("Loaded public key")
        #Generate Key Pair
        if self.pubkey == None or self.privkey == None:
            print("No key pair found, generating new one")
            (self.pubkey, self.privkey) = rsa.newkeys(4096, poolsize=8, accurate=False)
            path = os.path.join(self.config.local_path, 'private_key.pem')
            with open(path, "wb") as file:
                keydata = self.privkey.save_pkcs1("PEM")
                file.write(keydata)
            path = os.path.join(self.config.local_path, 'public_key.pem')
            with open(path, "wb") as file:
                keydata = self.pubkey.save_pkcs1("PEM")
                file.write(keydata)
        
        #Load installed models
        self.reload_models()
        self.apply_voice_config(False)

    #Session lock needs to be aquired
    def connect(self, password = None, clear_cookies = False):
        if clear_cookies:
            self.session.cookies.clear()
        try:
            #Login
            if password == None:
                response = self.session.get(self.config.api_url + '/is_logged_in', verify=not self.config.ignore_ssl_certificate)
                data = response.json()['logged_in']
                if not data:
                    raise ValueError("No password entered")
            else:
                if not self.session.post(self.config.api_url + '/login', json={ 'password': password }, verify=not self.config.ignore_ssl_certificate).json()['logged_in']:
                    raise ValueError("Wrong password")


            #Authenticate
            pubkeydata = rsa.PublicKey.save_pkcs1(self.pubkey)
            base64Key = base64.b64encode(pubkeydata).decode('utf-8')
            signature = rsa.sign(self.config.encryption_word.encode(), self.privkey, 'SHA-256')
            base64Signature = base64.b64encode(signature).decode('utf-8')
            
            payload = { "pubkey": base64Key, "signature": base64Signature, "name": self.config.name }
            data_str = json.dumps(payload)
            response = self.session.post(self.config.api_url + '/client_auth', data=data_str, verify=not self.config.ignore_ssl_certificate)

            #Connect WebSocket
            self.mute_disconnect = True
            self.ws.disconnect()
            self.ws.wait()
            self.mute_disconnect = False
            self.ws.connect(self.config.api_url.replace("http", "ws"), wait_timeout=10)

            self.active = True
            print("Sucessfully connected to master!")
        except:
            traceback.print_exc()
            self.ws.disconnect()
            self.ws.wait()
            self.active = False
        return self.active


    def run(self):
        pixel_ring_wrapper.set_volume(8)
        #Load cookies
        with self.session_lock:
            path = os.path.join(self.config.local_path, 'cookies.dat')
            if os.path.isfile(path):
                with open(path, 'rb') as file:
                        self.session.cookies.update(pickle.load(file))

            print('Waiting for connection')

            if self.connect():
                def speak():
                    self.tts("Die Verbindung zum Master wurde erfolgreich hergestellt! Du kannst nun mit mir sprechen! Ich heiße " + self.config.wakeword + "!" if self.config.language == 'de' else "Successfully connected to master! You can now talk to me! My name is " + self.config.wakeword + "!")
                self.task_thread.execute(speak)
            else:
                def speak():
                    self.tts("Die Verbindung zum Master konnte nicht hergestellt werden! Überprüfe ob der Master läuft oder konfiguriere einen gültigen Master!" if self.config.language == 'de' else "Couldn't connect to the master! Make sure the master is running or configure a valid master!")
                self.task_thread.execute(speak)
        
        #Reconnect thread
        def reconnect_task():
            while True:
                if not self.active:
                    with self.session_lock:
                        if not self.active:
                            if self.connect():
                                def speak():
                                    self.tts("Die Verbindung zum Master wurde wiederhergestellt!" if self.config.language == 'de' else "The connection to the master was reestabilished!")
                                self.task_thread.execute(speak)
                time.sleep(10)

        #Start
        self.task_thread.start()
        self.speech_thread.start()
        reconnect_thread = threading.Thread(target=reconnect_task, daemon=True)
        reconnect_thread.start()
        self.recorder.gate.time_out = self.config.active_record_time_out
        self.recorder.run()
        if self.config.allow_text_input:
            inp = ""
            while True:
                print('Enter text:')
                inp = input()
                self.task_thread.execute(lambda : self.process([inp], self.recorder.is_awake()))
    
    def close(self):
        path = os.path.join(self.config.local_path, 'cookies.dat')
        self.recorder.close()
        with self.session_lock:
            #Save cookies
            with open(path, 'wb') as file:
                pickle.dump(self.session.cookies, file)
            #Save config
            self.config.save_user()
            #WebSocket
            self.mute_disconnect = True
            self.ws.disconnect()
            self.ws.wait()
            self.active = True
            self.mute_disconnect = False

    def reload_models(self):
        self.models = self.load_models(self.config.model_path, False)
        self.scorers = self.load_models(self.config.scorer_path, True)

    def load_models(self, path, scorer):
        models = []
        for model in os.listdir(path):
            if (not scorer and (model.endswith('.pbmm') or model.endswith('.tflite'))) or (scorer and model.endswith('.scorer')):
                filestat = os.stat(os.path.join(path, model))
                isActive = (self.config.model == model) or (self.config.scorer == model)
                invalid = False
                if not scorer:
                    invalid = self.handler.invalid_model and self.config.model == model
                else:
                    invalid = self.handler.invalid_scorer and self.config.scorer == model
                models.append({
                    "filename": model,
                    "size": filestat.st_size,
                    "active": isActive,
                    "future_active": False,
                    "invalid": invalid
                })
        return models
    
    def apply_voice_config(self, awake):
        if awake:
            self.apply_command_config()
        else:
            self.apply_wakeword_config() 

    def apply_wakeword_config(self):
        if not self.handler.invalid_model and not self.handler.invalid_scorer:
            self.handler.model.setBeamWidth(self.config.wakeword_beam_width)
        with self.recorder.lock:
            self.recorder.set_state(SpeechRecorderState.WAKEWORD)
    
    def apply_command_config(self):
        if not self.handler.invalid_model and not self.handler.invalid_scorer:
            self.handler.model.setBeamWidth(self.config.active_beam_width)
        with self.recorder.lock:
            self.recorder.set_state(SpeechRecorderState.COMMAND)
    
    def submit(self, data: [float], awake):
        if awake:
            pixel_ring_wrapper.think()
            self.recorder.set_state(SpeechRecorderState.PAUSE)
            texts = self.recognize_audio(data, 7, 'active')
            self.task_thread.execute(lambda : self.process(texts, awake))
        else:
            def recognize():
                pixel_ring_wrapper.think()
                texts = self.recognize_audio(data, 1, 'wakeword')
                self.task_thread.execute(lambda : self.process(texts, awake))
                pixel_ring_wrapper.off()
            if (not self.speech_thread.execute_if_free(recognize)):    #Only process when queue is free to prevent clogging it up
                print("A speech recording was dropped due to full queue")

    def recognize_audio(self, data: [float], amount: int, profile: str):
        res = []
        if self.config.speech_server.startswith('http'):
            try:
                response = requests.post(self.config.speech_server + '/recognize/' + self.config.language + '/' + profile + '/' + str(amount), headers={'Content-Type': 'application/octet-stream'}, data=(numpy.array(data) * 32767).astype(numpy.int16).tostring(), verify=False)
                res = response.json()
            except Exception as e:
                print('Couldn\'t connect to speech server')
                traceback.print_exc()
        else:
            res = self.handler.recognize((numpy.array(data) * 32767).astype(numpy.int16), amount)
        return res

    def handle_broadcast(self, data: dict):
        if self.active:
            self.handle_response(data, True)
            #Apply new config
            self.apply_voice_config(self.curr_stmt >= 0)
    
    def stream_audio(self, url):
        print('Streaming audio')
        if self.vlc != None:
            self.vlc.stop()
        #self.vlc = vlc.MediaPlayer(url)
        instance = vlc.Instance()
        self.vlc = instance.media_player_new()
        media = instance.media_new(url)
        media.get_mrl()
        self.vlc.set_media(media)
        self.vlc.play()

    def handle_response(self, data: dict, play_broadcast: bool = False):
        pixel_ring_wrapper.off()
        if data:
            if not (data['broadcast'] == True) or play_broadcast:
                if data['type'] == 'text':
                    self.curr_stmt = int(data['id'])
                    self.tts(data['response'])
                elif data['type'] == 'audio':
                    try:
                        self.curr_stmt = int(data['id'])
                        self.handle_audio_response(data)
                    except Exception as e:
                        print(e)
                if data['ir_remote'] is not None and data['ir_signal'] is not None:
                    print('Sending \'{}\' to \'{}\''.format(data['ir_signal'], data['ir_remote']))
                    os.system('irsend SEND_ONCE {ir_remote} {ir_signal}'.format(ir_remote=data['ir_remote'], ir_signal=data['ir_signal']))
            else:
                self.curr_stmt = -1
        else:
            text = 'Sorry, I did not understand that.'
            if self.config.language == 'de':
                text = 'Das verstehe ich nicht!'
            self.curr_stmt = -1
            self.tts(text)

    def handle_audio_response (self, data: dict):
        if data['response'] == 'stop':
            if self.vlc != None:
                self.vlc.stop()
        elif data['response'].split(':')[0] == 'decrease' or data['response'].split(':')[0] == 'increase' or data['response'].split(':')[0] == 'set':
            level = int(data['response'].split(':')[1]) * 10
            print(level)
            try:
                if level > 100:
                    level = 100
                if level < 10:
                    level = 10
                m = alsaaudio.Mixer()
                vol = m.getvolume()
                if data['response'].split(':')[0] == 'decrease':
                    vol = vol[0] - level
                    if vol < 10:
                        vol = 10
                    m.setvolume(vol)
                elif data['response'].split(':')[0] == 'increase':
                    print(vol)
                    vol = vol[0] + level
                    print(vol)
                    if vol < 10:
                        vol = 10
                    m.setvolume(vol)
                elif data['response'].split(':')[0] == 'set':
                    m.setvolume(level)
            except alsaaudio.ALSAAudioError:
                print("Couldn't set volume! No mixer was found for the audio device!")
        elif data['response'] == 'pause':
            if self.vlc != None:
                self.vlc.pause()
        elif data['response'] == 'resume':
            if self.vlc != None:
                self.vlc.play()
        else:
            try:
                print(data['response'])
                self.stream_audio(data['response'])
            except Exception as e:
                print(e)
                if self.config.tts:
                    self.tts('Sorry, ich kann dieses Lied nicht spielen!' if self.config.language == 'de' else 'Sorry, i cannot play this song')

    def process(self, texts: [str], awake):
        if self.active:
            #Check wakeword
            if not awake:
                print(texts)
                for text in texts:
                    if self.config.wakeword.lower() in text.lower():
                        print('Woke up')
                        pixel_ring_wrapper.off()
                        self.wakeup_sound.play().wait_done()
                        #Apply new config
                        self.apply_voice_config(True)
                        break
            #Send command
            else:
                print(texts)
                if self.curr_stmt < 0:
                    try:
                        data = None
                        with self.session_lock:
                            response = self.session.post(self.config.api_url + '/command', json={'commands': texts, 'language': self.config.language}, verify=not self.config.ignore_ssl_certificate)
                            data = response.json()
                        self.handle_response(data)
                    except Exception as err:
                        print('Couldn\'t connect to server')
                        print(err)
                        self.curr_stmt = -1
                else:
                    try:
                        data = None
                        with self.session_lock:
                            response = self.session.post(self.config.api_url + '/answer', json={'id': self.curr_stmt, 'answers': texts, 'language': self.config.language}, verify=not self.config.ignore_ssl_certificate)
                            data = response.json()
                        self.handle_response(data)
                    except Exception as err:
                        print('Couldn\'t connect to server')
                        print(err)
                        self.curr_stmt = -1
                self.apply_voice_config(self.curr_stmt >= 0)

    def tts(self, text):
        print(text)
        if self.tts_engine:
            pixel_ring_wrapper.speak()
            self.tts_engine.speak(text)
            pixel_ring_wrapper.off()

