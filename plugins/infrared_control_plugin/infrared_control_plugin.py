from master.plugin import *
from master.command import *
from master.number_parser import *

class InfraredControlCommand(Command):
	def __init__(self, plugin):
		super().__init__()
		self.plugin = plugin
		self.name = 'Infrared Control Command'
		self.description = 'Control infrared devices!'
		self.aliases = {
			'en': [
				'send {command} to {device}'
			],
			'de': [
				'schicke {command} an {device}',
				'sende {command} an {device}'
			]
		}
		self.texts = {
			'en': {
				'NO_SUCH_DEVICE': 'I could not find the ir device {device}',
				'NO_SUCH_COMMAND': 'This device does not support the command {command}',
				'SLAVE_NOT_CONNECTED': 'The device {device} is not online!'
			},
			'de': {
				'NO_SUCH_DEVICE': 'Ich konnte das Infrarot Gerät {device} nicht finden',
				'NO_SUCH_COMMAND': 'Das Gerät unterstützt den Befehl {command} nicht',
				'SLAVE_NOT_CONNECTED': 'Das Gerät {device} ist nicht online!'
			}
		}

	def execute(self, params: dict, args: CommandArguments) -> Statement:
		remote_device = None
		remote_command = None
		print(params)
		for device in self.plugin.config['devices']:
			if device['name'] == params['device'] or params['device'] in device['aliases']:
				remote_device = device
		if remote_device is None:
			return Statement(self.get_text('NO_SUCH_DEVICE', args.language, params))

		for command in device['commands']:
			if command['name'] == params['command'] or params['command'] in command['aliases']:
				remote_command = command
		if remote_command is None:
			return Statement(self.get_text('NO_SUCH_COMMAND', args.language, params))
		if not device['client'] in args.assistant.connected_clients:
			return Statement(self.get_text('SLAVE_NOT_CONNECTED', args.language, params))
		
		return Statement('', ir_remote=remote_device['remote'], ir_signal=remote_command['signal'], targets=[device['client']], broadcast=True)

class InfraredControlPlugin(Plugin):
	def __init__(self):
		super().__init__()
		self.name = 'Infrared Control Plugin'
		self.description = 'This plugin allows you to use LocalSpeech to control various things in the real world!'
		self.config = {
			'devices': [
				{
					'name': 'DEVICE_NAME',
					'aliases': [],
					'client': 'CLIENT_ID',
					'remote': 'REMOTE_NAME',
					'commands': [
						{
							'name': 'COMMAND_NAME',
							'aliases': [],
							'signal': 'SIGNAL'
						}
					]
				}
			]
		}
		self.commands = [
			InfraredControlCommand(self)
		]
