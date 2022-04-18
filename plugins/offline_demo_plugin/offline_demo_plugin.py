import random
from master.plugin import *
from master.command import *
from master.number_parser import *
import socket

class MarryMeCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Marry Me Command"
        self.description = "Does the computer want to marry you?"
        self.aliases = {
            'en': [
                "marry me",
                "will you marry me",
                "please marry me",
                "can you marry me",
                "do you want to marry me",
                "would you like to marry me"
            ],
            'de': [
                "heirate mich",
                "bitte heirate mich",
                "willst du mich heiraten",
                "kannst du mich heiraten",
                "möchtest du mich heiraten"
            ],
        }
        self.texts = {
            'en': {
                "ANSWER1": "I don't think a relatinship between a computer and a human would work!",
                "ANSWER2": "Sorry I'm already taken.",
                "ANSWER3": "I'm afraid I can't fall in love with you on command!",
                "ANSWER4": "Maybe if you ask more kindly.",
                "ANSWER5": "Do you really want that?"
            },
            'de': {
                "ANSWER1": "Ich glaube nicht, dass eine Beziehung zwischen Mensch und Maschine funktionieren würde!",
                "ANSWER2": "Tut mir leid, ich bin bereits vergeben.",
                "ANSWER3": "Ich kann mich leider nicht auf Befehl in dich verlieben.",
                "ANSWER4": "Vielleicht wenn du noch lieber fragst.",
                "ANSWER5": "Willst du das wirklich?"
            },
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        return Statement(self.get_text(random.choice(['ANSWER1', 'ANSWER2', 'ANSWER3', 'ANSWER4', 'ANSWER5']), args.language, params), finished=True)


class CalculatorCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Calculator Command"
        self.description = "Calculates simple calculations for you (only supports 0 - 10)"
        self.aliases = {
            'en': [
                "calculate {number1} plus {number2}",
                "calculate {number1} minus {number2}",
                "calculate {number1} times {number2}",
                "calculate {number1} divided by {number2}",
            ],
            'de': [
                "rechne {number1} plus {number2}",
                "rechne {number1} minus {number2}",
                "rechne {number1} mal {number2}",
                "rechne {number1} dividiert durch {number2}",
            ],
        }
        self.texts = {
            'en': {
                "RESULT": "The result is {result}!",
                "NOT_A_NUMBER": "I'm sorry, {number} is not a number!"
            },
            'de': {
                "RESULT": "Das Ergebnis ist {result}!",
                "NOT_A_NUMBER": "Tut mir leid, {number} ist keine Zahl!"
            },
        }
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        #Parse numbers
        number1 = 0
        try:
            number1 = int(NUMBER_TEXTS[args.language][params["number1"]])
            print(number1)
        except:
            return Statement(self.get_text("NOT_A_NUMBER", args.language, { "number": params["number1"]}), finished=True)
        number2 = 0
        try:
            number2 = int(NUMBER_TEXTS[args.language][params["number2"]])
            print(number2)
        except:
            return Statement(self.get_text("NOT_A_NUMBER", args.language, { "number": params["number2"]}), finished=True)
        #Calculate
        result = number1 + number2
        return Statement(self.get_text("RESULT", args.language, { "result": result}), finished=True)


class OfflineDemoPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.name = "Offline Demo Plugin"
        self.description = "This plugin implements some fun commands that work without internet!"
        self.config = {
            'muted': [],
            'audio_url': 'https://cdn.discordapp.com/attachments/773599394850275408/914582193710444554/essen.wav'
        }
        self.commands = [
            MarryMeCommand(self),
            CalculatorCommand(self),
        ]