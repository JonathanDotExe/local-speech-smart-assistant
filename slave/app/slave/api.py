from flask import Flask, app, request, flash, redirect
from flask.globals import session
import flask
import flask_cors
import flask_login
from werkzeug.utils import secure_filename
import os
import signal
import bcrypt
import pickle
import atexit
import threading
from slave.client import * 
from slave.config import *


class SlaveUser:

    def __init__(self, password_hash, default_password='password') -> None:
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
        if password_hash == None:
            self.update_password(default_password)
        else:
            self.password_hash = password_hash

    def get_id(self):
        return 'user'

    def update_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf8'), self.password_hash)

class SlaveServer:

    def __init__(self, client: SpeechClient, config: ClientConfiguration):
        super().__init__()
        self.config = config
        self.client = client
        #Generate new key
        session_key = os.urandom(24)
        #Init server
        self.app = Flask(__name__, instance_relative_config=True)
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SECRET_KEY'] = session_key
        #CORS
        flask_cors.CORS(self.app)
        #Load password
        password = None
        path = os.path.join(self.config.api_data_path, 'login.dat')
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                password = file.read()
        
        #Login
        self.login_manager = flask_login.LoginManager()
        self.login_manager.init_app(self.app)
        self.user = SlaveUser(password, self.config.default_password)
        
        @self.login_manager.user_loader
        def load_user(user_id):
            if self.user.get_id() == user_id:
                return self.user
            return None
        
        #Endpoints
        #Login
        @self.app.route('/login', methods=['POST'])
        def login():
            if self.user.check_password(request.json.get('password', None)):
                flask_login.login_user(self.user)
                return { 'logged_in': True }
            return { 'logged_in': False }

        @self.app.route('/is_logged_in', methods=['GET'])
        def is_logged_in():
            return { 'logged_in': flask_login.current_user.is_authenticated }

        @self.app.route('/change_password', methods=['POST'])
        @flask_login.login_required
        def change_password():
            if self.user.check_password(request.json.get('password', None)):
                self.user.update_password(request.json.get('new_password', None))
                return { 'success': True }
            return { 'success': False }

        @self.app.route('/config/<name>', methods=['GET', 'POST'])
        @flask_login.login_required
        def get_config_value(name):
            if request.method == 'GET':
                try:
                    value = self.config.user['DEFAULT'].get(name, getattr(self.config, name))
                except:
                    return {}, 406
                return flask.jsonify({name: value}), 200
            else:
                try:
                    value = request.json['value']
                except:
                    return flask.jsonify(message='No value was supplied'), 406
                try:
                    func = getattr(self.config, 'set_' + name)
                    func(value)
                except:
                    return flask.jsonify(message='Attribute not found'), 406
                if name == 'model' or name == 'scorer':
                    list = self.client.models
                    if name == 'scorer':
                        list = self.client.scorers
                    found = False
                    for m in list:
                        m['future_active'] = False
                        if m.get('filename') == value:
                            found = True
                            if name == 'model' and self.config.model == value:
                                self.client.future_model = None
                            elif name == 'scorer' and self.config.scorer == value:
                                self.client.future_scorer = None
                            else:
                                m['future_active'] = True
                                if name == 'model':
                                    self.client.future_model = value
                                else:
                                    self.client.future_scorer = value
                    if not found:
                        return flask.jsonify(message='Model not found'), 400
                elif name == 'noise_gate':
                    self.client.recorder.gate.gate = float(value)
                elif name == 'wakeword_beam_width' or name == 'wakeword_record_time_out' or name == 'active_beam_width' or name =='active_record_time_out':
                    self.client.task_thread.execute(lambda : self.client.apply_voice_config(self.client.recorder.is_awake()))
                return {}, 200

        #Models
        @self.app.route('/models', methods=['GET'])
        @flask_login.login_required
        def get_models():
            return flask.jsonify(models=self.client.models, invalid_model=self.client.handler.invalid_model)

        @self.app.route('/model/upload', methods=['POST'])
        @flask_login.login_required
        def upload_model():
            file = request.files['file']
            for m in self.client.models:
                if m['filename'] == file.filename:
                    return flask.jsonify(message='Model already exists.'), 400
            if file and (file.filename.endswith('.pbmm') or file.filename.endswith('.tflite')):
                try:
                    file.save(os.path.join(self.config.model_path, secure_filename(file.filename)))
                    self.client.reload_models()
                    return {}, 200
                except Exception as e:
                    return flask.jsonify(message=str(e))
            return flask.jsonify(message='No file or wrong filetype appended'), 406

        @self.app.route('/model/<filename>', methods=["DELETE"])
        def delete_model(filename):
            if self.config.model == filename:
                return flask.jsonify(message='Cannot delete active model'), 406
            if filename == self.client.future_model:
                return flask.jsonify(message='This model has been set active after reboot'), 406
            file = os.path.join(self.config.model_path, secure_filename(filename))
            try:
                open(file)
            except:
                return flask.jsonify(message='File does not exist'), 400
            try:
                os.remove(os.path.join(self.config.model_path, secure_filename(filename)))
            except:
                return flask.jsonify(message='File could not be deleted'), 400
            self.client.reload_models()
            return {}, 200

        @self.app.route('/scorers', methods=['GET'])
        @flask_login.login_required
        def get_scorers():
            return flask.jsonify(scorers=self.client.scorers, invalid_scorer=self.client.handler.invalid_scorer)

        @self.app.route('/scorer/upload', methods=['POST'])
        @flask_login.login_required
        def upload_scorer():
            file = request.files['file']
            for m in self.client.scorers:
                if m['filename'] == file.filename:
                    return flask.jsonify(message='Scorer already exists.'), 400
            if file and file.filename.endswith('.scorer'):
                try:
                    file.save(os.path.join(self.config.scorer_path, secure_filename(file.filename)))
                    self.client.reload_models()
                    return {}, 200
                except Exception as e:
                    return flask.jsonify(message=str(e))
            return {}, 406

        @self.app.route('/scorer/<filename>', methods=["DELETE"])
        def delete_scorer(filename):
            if self.config.scorer == filename:
                return flask.jsonify(message='Cannot delete active scorer'), 406
            if filename == self.client.future_scorer:
                return flask.jsonify(message='This scorer has been set active after reboot'), 406
            file = os.path.join(self.config.scorer_path, secure_filename(filename))
            try:
                open(file)
            except:
                return flask.jsonify(message='File does not exist'), 400
            try:
                os.remove(os.path.join(self.config.scorer_path, secure_filename(filename)))
            except:
                return flask.jsonify(message='File could not be deleted'), 400
            self.client.reload_models()
            return {}, 200
        
        #Settings
        @self.app.route('/connect', methods=['POST'])
        @flask_login.login_required
        def connect():
            self.config.set_api_url(request.json['api_url'])
            with self.client.session_lock:
                success = self.client.connect(password=request.json['password'], clear_cookies=True)
            return flask.jsonify(success)

        @self.app.route('/reboot', methods=['POST'])
        @flask_login.login_required
        def reboot():
            def do_reboot():
                if self.config.allow_reboot:
                    self.save()
                    os.system(self.config.reboot_cmd)
                else:
                    print('Rebooting is not allowed')
            threading.Thread(target=do_reboot).start()
            return flask.jsonify(True)
        
        @self.app.route('/shutdown', methods=['POST'])
        @flask_login.login_required
        def shutdown():
            def do_shutdown():
                os.kill(os.getpid(), signal.SIGINT)
            threading.Thread(target=do_shutdown).start()
            return flask.jsonify(True)
        
        @self.app.route('/is_connected', methods=['GET'])
        @flask_login.login_required
        def is_connected():
            return flask.jsonify(self.client.active)

    def save(self):
        print('Saving password')
        self.client.close()
        #Save password
        path = os.path.join(self.config.api_data_path, 'login.dat')
        with open(path, 'wb') as file:
            file.write(self.user.password_hash)

    def run(self):
        threading.Thread(target = self.client.run, daemon=True).start()
        self.app.run(debug = False, port = self.config.port, host = '0.0.0.0', ssl_context='adhoc')
        def exit_callback():
            self.save()
        atexit.register(exit_callback)