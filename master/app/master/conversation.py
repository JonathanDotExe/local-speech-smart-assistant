def parse_params(inp: str, template: str):
    values = {}
    in_parts_case = inp.split(' ')
    in_parts = inp.lower().split(' ')
    template_parts = template.lower().split(' ')
    in_i = 0
    i = 0

    # Iterate over template parts
    while i < len(template_parts):
        # Break if no input word is there
        if in_i >= len(in_parts):
            return None
        t = template_parts[i]

        if t.startswith("{") and t.endswith("}"):
            param = t[1:-1]
            values[param] = ""
            i += 1
            space = False
            while in_i < len(in_parts) and (i >= len(template_parts) or in_parts[in_i] != template_parts[i]):
                if space:
                    values[param] += " "
                values[param] += in_parts_case[in_i]
                space = True
                in_i += 1
        elif in_parts[in_i] != template_parts[i]:
            return None
        in_i += 1
        i += 1
    if in_i < len(in_parts):
        return None
    return values

class CommandArguments:

    def __init__(self, texts: [str], language: [str], executor: int, assistant):
        self.texts = texts
        self.language = language
        self.executor = executor
        self.assistant = assistant

class Statement:

    TEXT = 'text'
    AUDIO = 'audio'

    def __init__(self, text: str, callback=lambda a, args : Statement(""), finished: bool = True, grammars: {str: [str]} = {}, broadcast = False, targets = None, old_params: dict = None, ir_remote: str = None, ir_signal: str = None, type: str = TEXT):
        self.text = text
        self.callback = callback
        self.finished = finished
        self.grammars = grammars # Dict of language codes to list of alias names in that language
        self.broadcast = broadcast
        self.targets = targets
        self.ir_remote = ir_remote
        self.ir_signal = ir_signal
        self.type = type
        self.old_params = old_params

    def try_execute(self, inp: str, args: CommandArguments):
        if self.grammars.get(args.language):
            for grammar in self.grammars[args.language]:
                if self.old_params:
                    values = self.old_params
                    parsed = parse_params(inp, grammar)
                    if parsed:
                        values.update(parsed)
                        return self.callback(values, args)
                else:
                    values = parse_params(inp, grammar)
                    if values:
                        return self.callback(values, args)
        return None

class RunningStatement:

    def __init__(self, stmt: Statement, time: float):
        self.stmt = stmt
        self.time = time

class StatementInfo:

    def __init__(self, stmt: Statement, id: int):
        self.stmt = stmt
        self.id = id
    
    def to_json(self):
        return { 'id': self.id, 'response': self.stmt.text, 'broadcast': self.stmt.broadcast, 'ir_remote': self.stmt.ir_remote, 'ir_signal': self.stmt.ir_signal, 'type': self.stmt.type }
