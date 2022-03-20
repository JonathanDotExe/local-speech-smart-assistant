from master.plugin import * 
from master.command import * 
from master.config import *
import time
import json
import threading

class ConnectedClient:

    def __init__(self, sid, ip):
        self.sid = sid
        self.ip = ip

class SmartAssistant:

    def __init__(self, config: ServerConfiguration):
        self.config = config
        self.connected_clients = {}
        self.plugins = []
        self.reload_plugins()
        self.statements: {int: RunningStatement} = {}
        self.next_stmt_id = 0
        self.lock = threading.Lock()
        def cb(stmt: dict, targets: []):
            print('Broadcasts are not supported!')
        self.broadcast_callback = cb
    
    def start(self):
        def task():
            while True:
                t = time.time()
                remove = []
                with self.lock:
                    for id, stmt in self.statements.items():
                        if stmt.time < t - 60:
                            remove.append(id)
                    for id in remove:
                        del self.statements[id]
                time.sleep(1)
        thread = threading.Thread(target=task, daemon=True)
        thread.start()
 
    def new_statement(self, stmt: Statement) -> StatementInfo:
        info: StatementInfo = None
        if not stmt.finished:
            self.statements[self.next_stmt_id] = RunningStatement(stmt, time.time())
            self.next_stmt_id += 1
            info = StatementInfo(stmt, self.next_stmt_id - 1)
        else:
            info = StatementInfo(stmt, -1)
        if stmt.broadcast:
            print("Broadcast statement")
            self.broadcast_callback(info.to_json(), stmt.targets)
        return info

    def on_command(self, args: CommandArguments) -> dict:
        args.assistant = self
        for cmd in args.texts:
            for plugin in self.plugins:
                if plugin.active:
                    for command in plugin.commands:
                        ret = command.try_execute(cmd, args)
                        if ret != None:
                            with self.lock:
                                return self.new_statement(ret).to_json()
        return None
    
    def on_answer(self, id: int, args: CommandArguments) -> dict:
        args.assistant = self
        with self.lock:
            if id in self.statements:
                stmt: RunningStatement = self.statements[id]
                if not stmt.stmt.broadcast:
                    del self.statements[id]
                for answer in args.texts:
                    ret = stmt.stmt.try_execute(answer, args)
                    if ret != None:
                        return self.new_statement(ret).to_json()
        return None

    def save_configs(self):
        for plugin in self.plugins:
            with open(os.path.join(self.config.plugin_path, os.path.splitext(plugin.filename)[0] + '.json'), 'w') as f:
                f.write(json.dumps({ 'active': plugin.active, 'config': plugin.config }))

    def reload_plugins(self):
        #Load plugins
        self.save_configs()
        self.plugins = load_plugins(self.config.plugin_path)

    def get_plugin(self, filename):
        for plugin in self.plugins:
            if plugin.filename == filename:
                return plugin
        return None
