from master.plugin import *
from master.command import *
import socket

class FoodMessageCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Food Message Command"
        self.description = "Notifies all connected clients that food is ready!"
        self.aliases = {
            'en': [
                "food is ready",
                "lunch is ready",
                "food has arrived",
                "lunch has arrived"
            ],
            'de': [
                "essen ist da",
                "essen ist fertig",
                "mittagessen ist da",
                "mittagessen ist fertig"
            ],
        }
        self.texts = {
            'en': {
                "ASK": "Should I notify the people in the office?",
                "FOOD_IS_READY": "Hello everyone! Lunch has arrived!",
                "OK": "Ok!"
            },
            'de': {
                "ASK": "Soll ich eine Benachrichtigung aussenden?",
                "OK": "Ok!"
            },
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        def answer(params: dict, args: CommandArguments):
            if params['answer'] in ['ja', 'yes']:
                muted = self.plugin.config.get('muted', [])
                print(muted)
                targets = [client for client in args.assistant.connected_clients if client not in muted]
                print(targets)
                return Statement(self.plugin.config['audio_url'], type=Statement.AUDIO, broadcast=True, targets=targets)
            else:
                return Statement(self.get_text('OK', args.language, params), broadcast=False)
        return Statement(self.get_text('ASK', args.language, params), callback=answer, finished=False, grammars= {
            'en': [
                '{answer}'
            ],
            'de': [
                '{answer}'
            ]
        })

class MuteFoodMessageCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Mute Food Message Command"
        self.description = "Mutes food messages for the executing client!"
        self.aliases = {
            'en': [
                "mute food messages",
                "mute food messages in this room",
                "mute food messages here",
                "mute food notifications",
                "mute food notifications in this room",
                "mute food notifications here",
                "mute lunch messages",
                "mute lunch messages in this room",
                "mute lunch messages here",
                "mute lunch notifications",
                "mute lunch notifications in this room",
                "mute lunch notifications here"
            ],
            'de': [
                "schalte benachrichtigungen beim essen aus",
                "deaktiviere benachrichtigungen beim essen",
                "schalte essensbenachrichtigungen aus",
                "deaktiviere essensbenachrichtigungen",
                "benachrichtige mich nicht beim essen",
                "benachrichtige mich nicht wenn das essen da is",
                "benachrichtige mich nicht wenn das essen fertig ist",
                "benachrichtige mich nicht beim mittagessen"
            ],
        }
        self.texts = {
            'en': {
                "SUCCESS": "Lunch notifications successfully deactivated!"
            },
            'de': {
                "SUCCESS": "Essensbenachrichtigungen erfolgreich deaktiviert!"
            },
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        if args.executor not in self.plugin.config['muted']:
            self.plugin.config['muted'].append(args.executor)
        return Statement(self.get_text('SUCCESS', args.language, params))

class UnmuteFoodMessageCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Unmute Food Message Command"
        self.description = "Unmutes food messages for the executing client!"
        self.aliases = {
            'en': [
                "unmute food messages",
                "unmute food messages in this room",
                "unmute food messages here",
                "unmute food notifications",
                "unmute food notifications in this room",
                "unmute food notifications here",
                "unmute lunch messages",
                "unmute lunch messages in this room",
                "unmute lunch messages here",
                "unmute lunch notifications",
                "unmute lunch notifications in this room",
                "unmute lunch notifications here"
            ],
            'de': [
                "schalte benachrichtigungen beim essen ein",
                "schalte essensbenachrichtigungen ein",
                "aktiviere essensbenachrichtigungen",
                "aktiviere benachrichtigungen beim essen",
                "benachrichtige mich beim essen",
                "benachrichtige mich wenn das essen da is",
                "benachrichtige mich wenn das essen fertig ist",
                "benachrichtige mich beim mittagessen"
            ],
        }
        self.texts = {
            'en': {
                "SUCCESS": "Lunch notifications successfully activated!"
            },
            'de': {
                "SUCCESS": "Essensbenachrichtigungen erfolgreich aktiviert!"
            },
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        if args.executor in self.plugin.config['muted']:
            self.plugin.config['muted'].remove(args.executor)
        return Statement(self.get_text('SUCCESS', args.language, params))

class FoodMessagePlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.name = "Food Message Plugin"
        self.description = "This plugin allows you to notify all people in the office that lunch is ready!"
        self.config = {
            'muted': [],
            'audio_url': 'https://cdn.discordapp.com/attachments/773599394850275408/914582193710444554/essen.wav'
        }
        self.commands = [
            FoodMessageCommand(self),
            MuteFoodMessageCommand(self),
            UnmuteFoodMessageCommand(self)
        ]