import requests
import base64
from master.plugin import *
from master.command import *
from master.number_parser import *
from master.timeutils import *
import flask
import difflib
import socket
import datetime

class OnlineStatusCommand(Command):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Online Status Command"
        self.description = "Tells you if an organization member is online!"
        self.aliases = {
            'en': [
                "is {name} online",
                "tell me the online status of {name}"
            ],
            'de': [
                "sag mir den online status von {name}",
                "ist {name} verfügbar",
                "ist {name} online"
            ],
        }
        self.texts = {
            'en': {
                "SUCCESS": "The status of {name} is {status}!",
                "SUCCESS_ACTIVITY": "{name} is {activity} and their current status is {status}!",
                "ERROR": "An error with code {status} occured!",
                "NO_USER": "Couldn't find a user with the name {name}!",
                "NO_PRIVILEGES": "Ich habe keine Berechtigung um diese Information abzurufen!!",
                "NO_CONNECTION": "Couldn't connect to the Microsoft Graph API!",
                "Available": "Available",
                "Busy": "Busy",
                "DoNotDisturb": "Do Not Disturb",
                "Be Right Back": "Be Right Back",
                "Away": "Away",
                "Offline": "Offline",
                "OffWork": "Off Work",
                "InACall": "In A Call",
                "PresenceUnknown": "Unknown"
            },
            'de': {
                "SUCCESS": "Der Status von {name} ist {status}!",
                "SUCCESS_ACTIVITY": "{name} ist {activity} und {name}'s Status ist {status}!",
                "ERROR": "Ein Fehler mit dem Code {status} ist aufgetreten",
                "NO_USER": "Es konnte kein User mit dem Namen {name} gefunden werden!",
                "NO_PRIVILEGES": "Ich habe keine Berechtigung um diese Information abzurufen!",
                "NO_CONNECTION": "Die Microsoft Graph API konnte nicht erreicht werden!",
                "Available": "Verfügbar",
                "Busy": "Beschäftigt",
                "DoNotDisturb": "Bitte nicht stören",
                "Be Right Back": "Bin gleich zurück",
                "Away": "Abwesend",
                "Offline": "Offline",
                "OffWork": "nicht in der Arbeit",
                "InACall": "in einem Telefonat",
                "PresenceUnknown": "Unbekannt"
            },
        }
        self.session = requests.Session()

    def load_users(self, url, headers, users):
        response = self.session.get(url, headers = headers)
        if response.status_code == 200:
            json = response.json()
            for user in json['value']:
                users.append(user)
            if '@odata.nextLink' in json:
                return self.load_users(json['@odata.nextLink'], headers, users)
        return response.status_code

    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        name = params['name'].lower()
        #Request API
        try:
            headers = self.plugin.refresh_access_token(self.session)

            #Find users
            url = 'https://graph.microsoft.com/v1.0/users?$search="displayName:' + name[0] + '"&$select=displayName,id'
            users = []
            status_code = self.load_users(url, headers, users)
            if status_code == 200:
                names = []
                for user in users:
                    names.append(user["displayName"].lower())
                try:
                    closest = difflib.get_close_matches(name, names, n=1, cutoff=0.3)[0]
                    user = None
                    for u in users:
                        if u['displayName'].lower() == closest:
                            user = u
                            break
                    #Presence
                    response = self.session.get('https://graph.microsoft.com/v1.0/users/' + user['id'] + '/presence/', headers = headers)
                    if response.status_code == 200:
                        json = response.json()
                        availability = json['availability']
                        activity = json['activity']
                        if availability == activity:
                            return Statement(self.get_text('SUCCESS', args.language, {'name': user['displayName'], 'status': self.get_text(availability, args.language, {})}))
                        else:
                            return Statement(self.get_text('SUCCESS_ACTIVITY', args.language, {'name': user['displayName'], 'status': self.get_text(availability, args.language, {}), 'activity': self.get_text(activity, args.language, {})}))
                    elif response.status_code == 401:
                        return Statement(self.get_text('NO_PRIVILEGES', args.language, {}))
                    else:
                        return Statement(self.get_text('ERROR', args.language, {'status': response.status_code}))
                except IndexError:
                    pass

                return Statement(self.get_text('NO_USER', args.language, {'name': params['name']})) #TODO
            elif status_code == 401:
                return Statement(self.get_text('NO_PRIVILEGES', args.language, {}))
            else:
                return Statement(self.get_text('ERROR', args.language, {'status': status_code}))
        except requests.exceptions.RequestException:
            return Statement(self.get_text('NO_CONNECTION', args.language, {}))

class CalendarEventCommand(Command):
    
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.name = "Calendar event command"
        self.description = "Plans your meetings!"
        self.aliases = {
            'en': [
                "schedule a meeting for {day}",
                "plan a meeting for {day}",
                "schedule a meeting on the {date}",
                "schedule a meeting on {date}",
                "plan a meeting on the {date}",
                "plan a meeting on {date}",
                "schedule a meeting",
                "plan a meeting"
            ],
            'de': [
                "plane eine besprechung für {day}",
                "plane eine besprechung fuer {day}",
                "plane eine besprechung am {date}",
                "plane eine besprechung",
                "erstelle eine besprechung",
                "trage eine besprechung ein",
            ],
        }
        self.texts = {
            'en': {
                "CREATED": "Ok, i have planned the meeting {use} on {date} from {time1} to {time2} o'clock",
                "ASK_USE": "Ok, what's the meeting's subject?",
                "ASK_TIME": "Ok, when does the meeting start?",
                "RE_ASK_TIME": "Please repeat when the meeting starts!",
                "ASK_TIME_2": "Ok, when does the meeting end?",
                "RE_ASK_TIME_2": "Please repeat when the meeting ends!",
                "ERROR": "Sorry, i couldn't create the meeting! Please check if you configured the plugin correctly!",
                "UNDERSTAND_ERROR": "Sorry, i did not understand that."
            },
            'de': {
                "CREATED": "Ok, ich habe die Besprechung {use} am {date} für {time1} Uhr bis {time2} Uhr geplant",
                "ASK_USE": "Ok, was ist der Betreff der Besprechung?",
                "ASK_TIME": "Ok, wann beginnt die Besprechung?",
                "RE_ASK_TIME": "Bitte wiederholen Sie wann die Besprechung beginnt!",
                "ASK_TIME_2": "Ok, wann endet die Besprechung?",
                "RE_ASK_TIME_2": "Bitte wiederholen Sie wann die Besprechung endet!",
                "ERROR": "Es tut mir leid, ich konnte die Besprechung nicht eintragen! Bitte überprüfen Sie ob Sie das Plugin korrekt konfiguriert haben!",
                "UNDERSTAND_ERROR": "Es tut mir leid, das habe ich nicht verstanden."
            },
        }
        self.futures = {
            'en': {
                'tomorrow': 1,
                'the day after tomorrow': 2,
                'next week': 7
            },
            'de': {
                'morgen': 1,
                'uebermorgen': 2,
                'übermorgen': 2,
                'naechste woche': 7,
                'nächste woche': 7
            }
        }
        self.session = requests.Session()
    
    def execute(self, params: dict, args: CommandArguments) -> Statement:
        try:
            self.plugin.refresh_access_token(self.session)
            def ask_time1(params: dict, args: CommandArguments, text: str):
                if 'time1_1' in params:
                    params.pop('time1_1')
                if 'time2_1' in params:
                    params.pop('time1_2')
                return Statement(self.get_text(text, args.language, params), callback=self.execute, finished=False, old_params=params, grammars= {
                    'en': [
                        '{time1}',
                        '{time1} o clock',
                        'it starts at {time1}',
                        'the meeting starts at {time1}'
                    ],
                    'de': [
                        'um {time1} uhr',
                        'es beginnt um {time1} uhr',
                        'sie beginnt um {time1} uhr',
                        'die besprechung beginnt um {time1} uhr',
                        '{time1} uhr',
                        'um {time1_1} uhr {time1_2}',
                        'es beginnt um {time1_1} uhr {time1_2}',
                        'sie beginnt um {time1_1} uhr {time1_2}',
                        'die besprechung beginnt um {time1_1} uhr {time1_2}',
                        '{time1_1} uhr {time1_2}'
                    ]
                })
            def ask_time2(params: dict, args: CommandArguments, text: str):
                if 'time2_1' in params:
                    params.pop('time2_1')
                if 'time2_2' in params:
                    params.pop('time2_2')
                print(params)
                return Statement(self.get_text(text, args.language, params), callback=self.execute, finished=False, old_params=params, grammars= {
                    'en': [
                        '{time2}',
                        '{time2} o clock',
                        'it ends at {time2}',
                        'the meeting ends at {time2}'
                    ],
                    'de': [
                        'um {time2} uhr',
                        'es endet um {time2} uhr',
                        'sie endet um {time2} uhr',
                        'die besprechung endet um {time2} uhr',
                        '{time2} uhr',
                        'um {time2_1} uhr {time2_2}',
                        'es endet um {time2_1} uhr {time2_2}',
                        'sie endet um {time2_1} uhr {time2_2}',
                        'die besprechung endet um {time2_1} uhr {time2_2}',
                        '{time2_1} uhr {time2_2}'
                    ]
                })
            def confirm(params: dict, args: CommandArguments):
                print(params)
                #try:

                if not 'time1_correct' in params:
                    time1 = parse_time1(params=params, args=args)
                    if time1 is ASK:
                        return ask_time1(params, args, 'ASK_TIME')
                    if time1 is RE_ASK:
                        return ask_time1(params, args, 'RE_ASK_TIME')
                    params = time1

                params['time1_correct'] = True

                if not 'time2_correct' in params:
                    time2 = parse_time2(params=params, args=args)
                    if time2 is ASK:
                        return ask_time2(params, args, 'ASK_TIME_2')
                    if time2 is RE_ASK:
                        return ask_time2(params, args, 'RE_ASK_TIME_2')
                    params = time2

                params['time2_correct'] = True

                if 'use' in params and 'time1' in params and 'time2' in params:
                    date = datetime.datetime.today()
                    if 'day' in params:
                        futures = self.futures[args.language]
                        day = futures[params['day']]
                        if day:
                            date += datetime.timedelta(days=day)
                    elif 'date' in params:
                        parsed_date = parse_date(params['date'], args.language)
                        if not parsed_date is None:
                            date = parsed_date
                    date = date.strftime('%Y-%m-%d')
                    params['date'] = date

                    headers = {
                        "Authorization": "Bearer " + self.plugin.config['bearer_token']
                    }
                    body = {
                        "subject": "{subject}".format(subject=params['use']),
                        "body": {
                            "contentType": "HTML",
                            "content": "Planned by smart assistant"
                        },
                        "start": {
                            "dateTime": "{date}T{time1}".format(date=date, time1=params['time1']),
                            "timeZone": self.plugin.config['time_zone']
                        },
                        "end": {
                            "dateTime": "{date}T{time2}".format(date=date, time2=params['time2']),
                            "timeZone": self.plugin.config['time_zone']
                        }
                    }
                    #response = requests.post('https://graph.microsoft.com/v1.0/groups/{group_id}/calendar/events'.format(group_id=self.plugin.config['group_id']), headers=headers, json=body)
                    response = requests.post('https://graph.microsoft.com/v1.0/me/calendar/events'.format(group_id=self.plugin.config['group_id']), headers=headers, json=body)
                    if response.status_code == 201:
                        return Statement(self.get_text('CREATED', args.language, params))
                    else:
                        return Statement(self.get_text('ERROR', args.language, params))
                else:
                    return Statement(self.get_text('UNDERSTAND_ERROR', args.language, params))

            def ask_use(params: dict, args: CommandArguments):
                print(params)
                return Statement(self.get_text('ASK_USE', args.language, params), callback=confirm, finished=False, old_params=params, grammars= {
                    'en': [
                        'the subject is {use}',
                        'it is {use}',
                        '{use}'
                    ],
                    'de': [
                        'der betreff ist {use}',
                        '{use}'
                    ]
                })

            if not 'use' in params:
                return ask_use(params=params, args=args)
            return confirm(params, args)

        except Exception as e:
            print(str(e))
            return Statement(self.get_text('ERROR', args.language, params))

    

class MicrosoftOrganizationsPlugin(Plugin):

    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()
        self.name = "Microsoft Organizations Plugin"
        self.description = "Contains commands to get information about your microsoft organization. Needed permissions: Presence.Read.All, User.ReadBasic.All, Calendars.ReadWrite, Calendars.ReadWrite.Shared"
        self.redirect_uri = 'https://{hostname}:4000/api/plugins/microsoft_organizations_plugin.zip/request_token'.format(hostname=self.hostname)
        self.html = '''
                <p>
                    <b>Note:</b> When creating the application identity in the Azure Portal use {uri} as redirect URI!
                </p>
                <a href="{href}"><button class="w3-button">Authenticate</button></a>
            '''.format(uri = self.redirect_uri, href='api/plugins/microsoft_organizations_plugin.zip/authenticate')
        self.config = {
            'tenant_id': 'INSERT_TENANT_ID_HERE',
            'client_id': 'INSERT_CLIENT_ID_HERE',
            'client_secret': 'INSERT_CLIENT_SECRET_HERE',
            'bearer_token': 'AUTO_GENERATED',
            'refresh_token': 'AUTO_GENERATED',
            'group_id': 'INSERT_GROUP_ID_HERE',
            'time_zone': 'Europe/Berlin'
        }
        self.commands = [
            OnlineStatusCommand(self),
            CalendarEventCommand(self)
        ]
        self.permissions = 'user.read user.readbasic.all presence.read presence.read.all calendars.readwrite calendars.read calendars.read.shared calendars.readwrite.shared'
    
    def endpoint(self, path):
        if path == 'authenticate':
            return flask.redirect('https://login.microsoftonline.com/' + self.config['tenant_id'] + '/oauth2/v2.0/authorize?client_id=' + self.config['client_id'] + '&response_type=code&response_mode=query&redirect_uri=' + self.redirect_uri + '&scope=offline_access ' + self.permissions)
        elif path == 'request_token':
            code = flask.request.args.get('code')
            response = requests.post('https://login.microsoftonline.com/' + self.config['tenant_id'] + '/oauth2/v2.0/token', data= {
                'client_id': self.config['client_id'],
                'scope': self.permissions,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_secret': self.config['client_secret']
            })
            data = response.json()
            print(data)
            self.config['bearer_token'] = data['access_token']
            self.config['refresh_token'] = data['refresh_token']
            return flask.redirect('https://{hostname}:4000/plugins.html'.format(hostname=self.hostname))
        return "Endpoint not found", 404
    
    def refresh_access_token(self, session):
        headers = {
            'Authorization': 'Bearer ' + self.config['bearer_token'],
            'ConsistencyLevel': 'eventual'
        }
        #API Test
        status_code = session.get('https://graph.microsoft.com/v1.0/me', headers = headers).status_code
        if status_code == 401:
            response = requests.post('https://login.microsoftonline.com/' + self.config['tenant_id'] + '/oauth2/v2.0/token', data= {
                'client_id': self.config['client_id'],
                'scope': self.permissions,
                'grant_type': 'refresh_token',
                'refresh_token': self.config['refresh_token'],
                'redirect_uri': self.redirect_uri,
                'client_secret': self.config['client_secret']
            })

            data = response.json()

            try:
                self.config['bearer_token'] = data['access_token']
                self.config['refresh_token'] = data['refresh_token']
            except KeyError:
                print("The MS-Organizations Token could not be refreshed: ", data.get("error_description", ""))

            return {
                'Authorization': 'Bearer ' + self.config['bearer_token'],
                'ConsistencyLevel': 'eventual'
            }
        return headers