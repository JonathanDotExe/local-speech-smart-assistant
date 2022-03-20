from master.plugin import *
from master.command import *
import pafy
from youtubesearchpython import VideosSearch

class PlaySongCommand(Command):
    
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Play Song Command"
        self.description = "Plays your favorite songs from YouTube!"
        self.aliases = {
            'en': [
                "play {song} on {target}",
                "play {song} in the {target}",
                "play {song}"
            ],
            'de': [
                "spiele {song} im {target}",
                "spiele {song} auf {target}",
                "spiele {song}"
            ]
        }
        self.texts = {
            'en': {
                "ERROR": "Sorry i could not find a video called {song}!"
            },
            'de': {
                "ERROR": "Es tut mir leid, ich konnte kein Video namens {song} finden!"
            }
        }
        self.target_all = {
            'en': [
                "all devices",
                "everywhere"
            ],
            'de': [
                "ueberall",
                "auf allen geraeten"
            ]
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        videosSearch = VideosSearch(params['song'], limit = 1)
        try:
            id = videosSearch.result()["result"][0]['id']
            v = pafy.new('https://www.youtube.com/watch?v=' + id)
            url = v.getbestaudio().url
            broadcast = False
            if 'target' in params:
                if params['target'] in self.target_all.get(args.language):
                    broadcast = True
            return Statement(url, type=Statement.AUDIO, broadcast=broadcast)
        except:
            params = {
                "song": params['song']
            }
            return Statement(self.get_text('ERROR', args.language, params))

class StopMusicCommand(Command):
    
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Stop Music Command"
        self.description = "Stops playing your favorite songs!"
        self.aliases = {
            'en': [
                "stop",
                "stop playing music"
            ],
            'de': [
                "stopp",
                "stop",
                "hoer auf musik zu spielen"
            ]
        }

    def execute(self, params: dict, args: CommandArguments) -> Statement:
        return Statement('stop', type= Statement.AUDIO)

class PauseMusicCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.name = "Pause Music Command"
        self.description = "Pauses the currently playing songs!"
        self.aliases = {
            'en': [
                "pause",
                "pause the music"
            ],
            'de': [
                "pause",
                "pausieren",
                "musik pausieren",
                "pausiere die musik"
            ]
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        return Statement('pause', type= Statement.AUDIO)

class ResumeMusicCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.name = "Resume Music Command"
        self.description = "Resumes the currently playing songs!"
        self.aliases = {
            'en': [
                "resume",
                "resume playing music",
                "continue",
                "continue playing music",
                "play"
            ],
            'de': [
                "weiter",
                "spiele die musik weiter",
                "musik weiterspielen",
                "weiterspielen",
                "spielen",
                "spiele die musik ab"
            ]
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        return Statement('resume', type= Statement.AUDIO)

class MusicPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.name = "Music Plugin"
        self.description = "Plays music!"
        self.commands = [
            PlaySongCommand(self),
            StopMusicCommand(self),
            PauseMusicCommand(self),
            ResumeMusicCommand(self)
        ]