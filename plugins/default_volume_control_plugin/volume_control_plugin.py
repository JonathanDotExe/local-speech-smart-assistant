from master.plugin import *
from master.command import *
from master.number_parser import *

class VolumeSetCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Volume Set Command"
        self.descriptions = "Sets the volume"
        self.aliases = {
            'en': [
                "volume {level_set}",
                "set the volume to {level_set}",
                "volume level {level_set}"
            ],
            'de': [
                "stell lautstärke auf {level_set}",
                "stelle die lautstärke auf {level_set}",
                "lautstärke {level_set}"
            ]
        }

    def execute(self, params: dict, args: CommandArguments) -> Statement:
        try:
            if 'level_set' in params:
                level = int(NUMBER_TEXTS[args.language][params['level_set']])
                if level > 10:
                    level = '10'
                return Statement('set:' + str(level), type=Statement.AUDIO)
        except:
            pass

class VolumeIncreaseCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Volume Increase Command"
        self.descriptions = "Increases the volume"
        self.aliases = {
            'en': [
                "turn the volume up",
                "turn the music up",
                "turn up the volume",
                "turn up the music",
                "increase the volume",
                "incrase the volume by {level}",
                "increase the volume by {level} levels",
                "increase the volume to {level_set}",
                "turn the music up to {level_set}",
                "turn the volume up to {level_set}"
            ],
            'de': [
                "mach die musik lauter",
                "lauter",
                "lauter bitte",
                "mach lauter",
                "mach den ton lauter",
                "mach bitte lauter",
                "ton lauter",
                "mach den ton lauter",
                "musik lauter",
                "mach die musik lauter",
                "stell die lautstärke rauf",
                "stell die lautstaerke rauf",
                "mach um {level} stufen lauter",
                "{level} stufen lauter",
                "mach den ton um {level} stufen lauter",
                "mach um {level} lauter",
                "mach {level} lauter",
                "{level} lauter",
                "erhöhe die lautstärke um {level}",
                "stell die lautstärke auf {level_set} rauf",
                "stelle die lautstärke auf {level_set} rauf",
                "erhöhe die lautstaerke um {level}",
                "stell die lautstaerke auf {level_set} rauf",
                "stelle die lautstaerke auf {level_set} rauf"
            ]
        }

    def execute(self, params: dict, args: CommandArguments) -> Statement:
        try:
            if 'level' in params:
                increase = int(NUMBER_TEXTS[args.language][params['level']])
                if increase > 10:
                    increase = '10'
                return Statement('increase:' + str(increase), type=Statement.AUDIO)
            if 'level_set' in params:
                level = int(NUMBER_TEXTS[args.language][params['level_set']])
                if level > 10:
                    level = '10'
                return Statement('set:' + str(level), type=Statement.AUDIO)
            return Statement('increase:1', type=Statement.AUDIO)
        except:
            pass

class VolumeDecreaseCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Volume Decrease Command"
        self.descriptions = "Decreases the volume"
        self.aliases = {
            'en': [
                "turn the volume down",
                "turn the music down",
                "turn down the volume",
                "turn down the music",
                "decrease the volume",
                "quieter",
                "decrase the volume by {level}",
                "decrease the volume by {level} levels",
                "decrease the volume to {level_set}",
                "volume {level_set}",
                "turn the music down to {level_set}",
                "turn the volume down to {level_set}"
            ],
            'de': [
                "mach die musik leiser",
                "leiser",
                "leiser bitte",
                "mach leiser",
                "mach den ton leiser",
                "mach bitte leiser",
                "ton leiser",
                "mach den ton leiser",
                "musik leiser",
                "mach die musik leiser",
                "stell die lautstärke runter",
                "mach um {level} stufen leiser",
                "{level} stufen leiser",
                "mach den ton um {level} stufen leiser",
                "mach um {level} leiser",
                "mach {level} leiser",
                "{level} leiser",
                "verringere die lautstärke um {level}",
                "stell die lautstärke auf {level_set} runter",
                "stelle die lautsärke auf {level_set} runter"
            ]
        }

    def execute(self, params: dict, args: CommandArguments) -> Statement:
        try:
            if 'level' in params:
                decrease = int(NUMBER_TEXTS[args.language][params['level']])
                if decrease > 10:
                    decrease = '10'
                return Statement('decrease:' + str(decrease), type=Statement.AUDIO)
            if 'level_set' in params:
                level = int(NUMBER_TEXTS[args.language][params['level_set']])
                if level > 10:
                    level = '10'
                return Statement('set:' + str(level), type=Statement.AUDIO)
            return Statement('decrease:1', type=Statement.AUDIO)
        except:
            pass

class VolumeControlPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.name = "Volume-Control Plugin"
        self.description = "A preinstalled default plugin used to control the volume of your device."
        self.config = {}
        self.commands = [
            VolumeSetCommand(self),
            VolumeIncreaseCommand(self),
            VolumeDecreaseCommand(self)
        ]