from sqlite3.dbapi2 import Cursor
from flask import Flask, app, request, flash, redirect, g
from flask.globals import session
import socketio
import flask
import flask_cors
import flask_login
import flask_socketio
import flask_session
from werkzeug.wsgi import FileWrapper
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response
from master.config import *
from master.assistant import *
import os
import signal
import bcrypt
import pickle
import atexit
import threading
import functools
import rsa
import base64
import json
import sqlite3

#Based on https://blog.miguelgrinberg.com/post/flask-socketio-and-the-user-session
def socketio_auth_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs): #TODO Check if client is set
        if flask_login.current_user.is_authenticated and 'client_id' in session:
            return f(*args, **kwargs)
        else:
            flask_socketio.disconnect()
    return wrapper

class AssistantUser:

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

class AssistantServer:

    def __init__(self, assistant: SmartAssistant, config: ServerConfiguration):
        super().__init__()
        self.config = config
        self.assistant = assistant

        #Load Key
        session_key = None
        path = os.path.join(self.config.local_path, 'session_key.dat')
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                session_key = file.read()
        #Generate new key
        if session_key == None:
            print("No session key found, generating new one")
            session_key = os.urandom(24)
            with open(path, 'wb') as file:
                file.write(session_key)
            
        #Init server
        self.app = Flask(__name__, instance_relative_config=True)
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SECRET_KEY'] = session_key
        #Session
        self.server_session = flask_session.Session(self.app)
        #SocketIO
        self.socketio = flask_socketio.SocketIO(self.app, managed_session=False)
        def broadcast_callback(info: dict, targets: []):
            if targets == None:
                print("Broadcasting to all")
                self.socketio.emit('command', info)
            else:
                print("Broadcasting to targets ", targets)
                for target in targets:
                    self.socketio.emit('command', info, room=self.assistant.connected_clients[target].sid)
        self.assistant.broadcast_callback = broadcast_callback
        #CORS
        flask_cors.CORS(self.app)
        #Load password
        password = None
        path = os.path.join(self.config.local_path, 'login.dat')
        if os.path.isfile(path):
            with open(path, 'rb') as file:
                password = file.read()
        
        #Login
        self.login_manager = flask_login.LoginManager()
        self.login_manager.init_app(self.app)
        self.user = AssistantUser(password, config.default_password) #TODO
        
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
                flask_login.login_user(self.user, remember=request.json.get('remember', True))
                return { 'logged_in': True }
            return { 'logged_in': False }

        @self.app.route('/is_logged_in', methods=['GET'])
        def is_logged_in():
            return { 'logged_in': flask_login.current_user.is_authenticated }

        @self.app.route('/client_auth', methods=['POST'])
        @flask_login.login_required
        def client_auth():
            clength = request.headers.get('content-length')
            if clength is None:
                return "Content length required", 411
            print("Receiving", clength, "bytes")
            if int(clength) <= self.config.max_content_size:
                content = request.get_data(cache=False, as_text=False, parse_form_data=False)
                jsonData = json.loads(content)
                try:
                    base64Decode = base64.b64decode(jsonData["pubkey"])
                    clientpub = rsa.PublicKey.load_pkcs1(base64Decode)
                except:
                    return "Invalid data", 400
                encryption_word = self.config.encryption_word
                signatureDecode = base64.b64decode(jsonData["signature"])

                try:
                    rsa.verify(encryption_word.encode(), signatureDecode, clientpub)
                except:
                    return "Invalid signature hash", 403

                # Checks passed:
                clientpub_bytes = rsa.PublicKey.save_pkcs1(clientpub)
                clientpub_b64 = base64.b64encode(clientpub_bytes)
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT * FROM clients WHERE pkey=?", (clientpub_b64,))
                row = cursor.fetchone()

                if(row is None):
                    insert_sql = "INSERT INTO clients (pkey, client_name) VALUES (?, ?)"
                    cursor.execute(insert_sql, (clientpub_b64, jsonData['name'], ))
                    db.commit()
                    session["client_id"] = cursor.lastrowid
                else:
                    session["client_id"] = row[0]
                    update_sql = "UPDATE clients SET client_name=? where id=?"
                    cursor.execute(update_sql, (jsonData['name'], row[0]))
                    db.commit()
                                                
            else:
                return "Content size too big", 413
            return {}

        @self.app.route('/change_password', methods=['POST'])
        @flask_login.login_required
        def change_password():
            if self.user.check_password(request.json.get('password', None)):
                self.user.update_password(request.json.get('new_password', None))
                return { 'success': True }
            return { 'success': False }
        #Commands
        @self.app.route('/command', methods=['POST'])
        @flask_login.login_required
        def command():
            if not 'client_id' in session:
                return "Client authorization required", 401
            print(session["client_id"])
            try:
                commands = request.json['commands']
                language = request.json['language']
            except KeyError:
                return 'Invalid JSON'

            args = CommandArguments(commands, language, session["client_id"], None)
            ret = self.assistant.on_command(args)

            if ret:
                return ret
            else:
                return {}

        @self.app.route('/answer', methods=['POST'])
        @flask_login.login_required
        def answer():
            if not 'client_id' in session:
                return "Client authorization required", 401
            try:
                answers = request.json['answers']
                language = request.json['language']
                id = int(request.json['id'])
            except KeyError:
                return 'Invalid JSON'
            
            args = CommandArguments(answers, language, session['client_id'], None)
            ret = self.assistant.on_answer(id, args)

            if ret:
                return ret
            else:
                return {}
        
        #Plugins
        @self.app.route('/plugins', methods=['GET', 'POST'])
        @flask_login.login_required
        def plugins():
            if request.method == 'GET':
                #Get all
                return flask.jsonify([*map(lambda p : p.to_json(), self.assistant.plugins)])
            else:
                #Update config
                plugin = self.assistant.get_plugin(request.json['filename'])
                plugin.active = bool(request.json.get('active', plugin.active))
                plugin.config.update(request.json.get('config', plugin.config))
                return plugin.to_json()
        
        @self.app.route('/plugins/<filename>/<path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
        @flask_login.login_required
        def plugins_endpoint(filename, path):
            #Update config
            plugin = self.assistant.get_plugin(filename)
            if plugin != None:
                return plugin.endpoint(path)
            else: 
                return "Plugin not found", 404

        @self.app.route('/plugins/upload', methods=['POST'])
        @flask_login.login_required
        def upload_plugin():
            file = request.files['file']
            if file and file.filename.endswith('.zip'):
                file.save(os.path.join(self.config.plugin_path, secure_filename(file.filename)))
                self.assistant.reload_plugins()
                return flask.jsonify(True)
            return flask.jsonify(False)
        
        @self.app.route('/plugins/<filename>', methods=['POST', 'DELETE'])
        @flask_login.login_required
        def delete_plugin(filename):
            success = False

            try:
                path = os.path.join(self.config.plugin_path, secure_filename(filename))
                os.remove(path)
                success = True
            except:
                pass
            self.assistant.reload_plugins()
            try:
                jsonpath = os.path.splitext(path)[0] + '.json'
                os.remove(jsonpath)
            except:
                pass

            return flask.jsonify(success)

        #Settings
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

        #Clients 
        @self.app.route('/clients', methods=['GET'])
        @flask_login.login_required
        def clients():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM clients;")
            clients = cursor.fetchall()
            client_list = []
            for c in clients:
                row = list(c)
                cid = row[0]
                is_online = cid in self.assistant.connected_clients
                ip = ""
                if is_online:
                    ip = self.assistant.connected_clients.get(cid).ip
                
                client = {
                    "id": cid,
                    "room_id": row[1],
                    "name": row[3],
                    "is_online": is_online,
                    "ip": ip
                }
                client_list.append(client)
            return flask.jsonify(client_list)
        
        @self.app.route('/client/<client_id>', methods=['DELETE'])
        @flask_login.login_required
        def client_delete(client_id):
            db = get_db()
            cursor = db.cursor()
            if int(client_id) in self.assistant.connected_clients:
                return flask.jsonify(message="Cannot remove a connected client!"), 403
            else:
                cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
                db.commit()
                return {}, 200
        
        @self.app.route('/clients/room/<clientid>/<roomid>')
        @flask_login.login_required
        def client_room(clientid, roomid):
            db = get_db()
            cursor = db.cursor()
            if (roomid == "-1"):
                roomid = None
            cursor.execute("UPDATE clients SET room_id=? WHERE id=?", (roomid, clientid,))
            db.commit()
            return {}, 200

        #Rooms
        @self.app.route('/rooms', methods=['GET'])
        @flask_login.login_required
        def rooms():
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM rooms")
            rooms = cursor.fetchall()
            room_list = []
            for r in rooms:
                room = {
                    "id": r[0],
                    "name": r[1]
                }
                room_list.append(room)
            return flask.jsonify(room_list)
        
        @self.app.route("/rooms/<name>", methods=['POST'])
        @flask_login.login_required
        def room_insert(name):
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO rooms (name) VALUES (?)", (name,))
            db.commit()
            return {}, 200

        @self.app.route("/rooms/edit/<id>/<name>", methods=["POST"])
        @flask_login.login_required
        def room_edit(id, name):
            db = get_db()
            cursor = db.cursor()
            cursor.execute("UPDATE rooms SET name=? WHERE id=?", (name, id,))
            db.commit()
            return {}, 200

        @self.app.route("/rooms/<id>", methods=['DELETE'])
        @flask_login.login_required
        def room_delete(id):
            db = get_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM rooms WHERE id=?", (int(id),))
            db.commit()
            return {}, 200

        @self.app.route("/stream_audio/<filename>", methods=['GET'])
        def streamwav(filename):
            CHUNK = 1024
            def generate():
                with open("resources/" + filename, "rb") as wav:
                    data = wav.read(CHUNK)
                    while data:
                        yield data
                        data = wav.read(CHUNK)
            return Response(generate(), mimetype="audio/mp3")

        #Websockets
        @self.socketio.on('connect')
        @socketio_auth_required
        def connect():
            self.assistant.connected_clients[session["client_id"]] = ConnectedClient(request.sid, request.remote_addr)

        @self.socketio.on('disconnect')
        def disconnect():
            client_id = session.get('client_id')
            if client_id in self.assistant.connected_clients:
                del self.assistant.connected_clients[client_id]

        def get_db():
            db = getattr(g, '_database', None)
            if db is None:
                db = g._database = sqlite3.connect(self.config.db_path)
                sql_file = open(self.config.sql_path)
                sql_text = sql_file.read()
                db.cursor().executescript(sql_text)
            return db

        # Close db on teardown
        @self.app.teardown_appcontext
        def close_connection(exception):
            db = getattr(g, '_database', None)
            if db is not None:
                db.close()
    
    def save(self):
        print('Saving')
        #Save password
        path = os.path.join(self.config.local_path, 'login.dat')
        with open(path, 'wb') as file:
            file.write(self.user.password_hash)
        #Save plugin config
        self.assistant.save_configs()

    def run(self):
        self.app.run(debug = False, port = self.config.port, host = '0.0.0.0', ssl_context='adhoc')
        atexit.register(self.save)
