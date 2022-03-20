import requests
import base64
from master.plugin import *
from master.command import *

class PipelineStatusCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Pipeline Status Command"
        self.description = "Tells you the build status of the latest run of a pipeline!"
        self.aliases = {
            'en': [
                "tell me the build status of {pipeline} in {project}",
                "tell me the build status of {project}"
            ],
            'de': [
                "sag mir den status von {pipeline} in {project}",
                "Sag mir den status von {project}"
            ],
        }
        self.texts = {
            'en': {
                "SUCCESS": "The last build of the {pipeline} was successful!",
                "FAILED": "The last build of the {pipeline} has failed!",
                "INVALID": "No pipeline called {pipeline} was found!",
                "NOT_FOUND": "The requested organization {organization} was not found!",
                "ERROR": "Couldn't connect to Azure DevOps!"
            },
            'de': {
                "SUCCESS": "Der letzte Build von {pipeline} war erfolgreich!",
                "FAILED": "Der letzte Build von {pipeline} ist fehlgeschlagen!",
                "INVALID": "Es gibt keine Pipeline mit dem Namen {pipeline}!",
                "NOT_FOUND": "Es gibt keine Organisation mit dem Namen {organization}!",
                "ERROR": "Azure DevOps konnte nicht erreicht werden!"
            },
        }
        self.session = requests.Session()
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        project_name = params['project']
        pipeline_name = params.get('pipeline', project_name)
        #Find project object
        project = None
        for p in self.plugin.config['projects']:
            pr = {
                    'name': '',
                    'aliases': [],
                    'pipelines': []
                }
            pr.update(p)
            
            if pr['name'] == project_name.lower() or project_name.lower() in pr['aliases']:
                project = pr
                break
        if project:
            project_name = project['name']
            pipeline = None
            for p in project['pipelines']:
                pi = {
                    'definition_name': '',
                    'definition_id': -1,
                    'aliases': []
                }
                pi.update(p)
                if pi['definition_name'] == pipeline_name.lower() or str(pi['definition_id']) == pipeline_name.lower() or pipeline_name.lower() in pi['aliases']:
                    pipeline = pi
                    break
            if pipeline:
                pipeline_name = str(pipeline['definition_name'])
        #Request API
        self.session.auth = (self.plugin.config['username'], self.plugin.config['basic_auth_token'])
        try:
            url = 'https://dev.azure.com/' + self.plugin.config['organization'] + '/' + project_name + '/_apis/build/status/' + pipeline_name + '?api-version=6.0-preview.1'
            response = self.session.get(url)
            print(url)
            if response.status_code != 200:
                try:
                    response.json()
                    return Statement(self.get_text('INVALID', args.language, {'pipeline': pipeline_name}))
                except:
                    return Statement(self.get_text('NOT_FOUND', args.language, {'organization': self.plugin.config['organization']}))
            else:
                if 'failed' in response.text:
                    return Statement(self.get_text('FAILED', args.language, {'pipeline': pipeline_name}))
                else:
                    return Statement(self.get_text('SUCCESS', args.language, {'pipeline': pipeline_name}))
        except requests.exceptions.RequestException:
            return Statement(self.get_text('ERROR', args.language, {}))

class AzureDevOpsPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.name = "Azure DevOps Plugin"
        self.description = "Contains commands to get information about your azure devops platform!"
        self.config = {
            'username': 'INSERT_USERNAME_HERE',
            'basic_auth_token': 'INSERT_KEY_HERE',
            'organization': 'example_company',
            'projects': [
                {
                    'name': 'Internal - Example Project',
                    'aliases': ['example'],
                    'pipelines': [
                        {
                            'definition_name': 'Internal - Example Pipeline',
                            'definition_id': 1,
                            'aliases': ['example_pipeline', 'example']
                        }
                    ]
                }
            ]
        }
        self.commands = [
            PipelineStatusCommand(self)
        ]