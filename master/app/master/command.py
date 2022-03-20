from master.conversation import *

class Command:

    def __init__(self):
        self.aliases = {} # Dict of language codes to list of alias names in that language
        self.name = ""
        self.description = ""
        self.texts = {} # Dict of language codes to dict of texts in that language

    def get_text(self, name: str, language: str, params: dict):
        text = name
        if self.texts.get(language) and self.texts.get(language).get(name):
            text = self.texts.get(language).get(name)
        return text.format(**params)
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        print("Executing command " + self.name + ": " + params)
        return Statement("Executing command " + self.name + ": " + params)
    
    def try_execute(self, inp: str, args: CommandArguments) -> Statement:
        if self.aliases.get(args.language):
            for alias in self.aliases[args.language]:
                values = parse_params(inp, alias)
                if values != None:
                    return self.execute(values, args)
        return None