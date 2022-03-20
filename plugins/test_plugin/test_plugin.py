from master.plugin import *
from master.command import *

class HelloCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        
        self.name = "Hello Command"
        self.description = "Says hello to someone!"
        self.aliases = {
            'en': [
                "say hello to {name}",
                "please say hello to {name}",
                "greet {name}"
            ],
            'de': [
                "sag hallo zu {name}",
                "bitte sag hallo zu {name}",
                "grüße {name}"
            ],
        }
        self.texts = {
            'en': {
                "HELLO_HOW_ARE_YOU": "Hello {name}! How are you?",
                "IM_GLAD_YOU_ARE": "I'm glad you are {emotion}!"
            },
            'de': {
                "HELLO_HOW_ARE_YOU": "Hallo {name}! Wie geht's dir?",
                "IM_GLAD_YOU_ARE": "Schön, dass es dir {emotion} geht!"
            },
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        def answer(params: dict, args: CommandArguments):
            return Statement(self.get_text('IM_GLAD_YOU_ARE', args.language, params))
        return Statement(self.get_text('HELLO_HOW_ARE_YOU', args.language, params), callback=answer, finished=not self.plugin.config['ask'], grammars= {
            'en': [
                'i\'m {emotion}',
                'im {emotion}',
                'i feel {emotion}',
                'i am {emotion}'
            ],
            'de': [
                'mir geht es {emotion}',
                'ich fühle mich {emotion}'
            ]
        })

class MusicCommand(Command):

    def __init__(self):
        super().__init__()
        self.name = "Music Command"
        self.description = "Plays the specified song by the specified band!"
        self.aliases = {
            'en': [
                "play {song} by {artist}",
            ],
            'de': [
                "spiele {song} von {artist}",
            ]
        }
        self.texts = {
            'en': {
                "PLAYING": "Playing {song} by {artist}!",
            },
            'de': {
                "PLAYING": "Spiele {song} von {artist}!",
            },
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        return Statement(self.get_text('PLAYING', args.language, params))

class RepeatCommand(Command):

    def __init__(self):
        super().__init__()
        self.name = "Repat Command"
        self.description = "Repeat incomming text"
        self.aliases = {
            'en': [
                'say {text}',
                'repeat {text}'
            ],
            'de': [
                'sage {text}',
                'wiederhole {text}'
            ]
        }

    def execute(self, params: dict, args: CommandArguments) -> Statement:
        return Statement(params['text'])

class TestPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.name = "Test Plugin"
        self.description = "A demo plugin for testing during the development of this app!"
        self.config = {
            'ask': True
        }
        self.commands = [
            HelloCommand(self),
            RepeatCommand(),
            MusicCommand()
        ]