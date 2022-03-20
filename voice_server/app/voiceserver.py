import deepspeech
import numpy
from flask import Flask, app, request, flash, redirect
from flask.globals import session
import flask
from werkzeug.utils import secure_filename
import os
import signal
import bcrypt
import pickle
import atexit
import threading
import json


class SpeechHandler:

    def __init__(self, model: str, scorer: str):
        self.invalid_model = False
        self.invalid_scorer = False
        try:
            self.model = deepspeech.Model(model)
        except Exception as e:
            self.invalid_model = True
        try:
            if not self.invalid_model:
                self.model.setBeamWidth(1000)
                self.model.enableExternalScorer(scorer)
        except Exception as e:
            self.invalid_scorer = True

    def recognize(self, audio: numpy.array, amount: int = 20):
        if not self.invalid_model and not self.invalid_scorer:
            texts = []
            for t in self.model.sttWithMetadata(audio, amount).transcripts:
                text = ''
                for token in t.tokens:
                    text += token.text
                texts.append(text)
            return texts
        return []


class SpeechRecognizer:

    def __init__(self, config) -> None:
        self.models = {}
        #Create models for languages and profiles
        for name, lang in config['languages'].items():
            for n, p in config['profiles'].items():
                model = deepspeech.Model('./data/' + lang['model'])
                model.setBeamWidth(p['beam_width'])
                model.enableExternalScorer('./data/' + lang['scorer'])
                self.models[(name, n)] = model


    def recognize(self, lang: str, profile: str, audio: numpy.array, amount: int):
        texts = []
        if (lang, profile) in self.models:
            model = self.models[(lang, profile)]
            for t in model.sttWithMetadata(audio, amount).transcripts:
                text = ''
                for token in t.tokens:
                    text += token.text
                texts.append(text)
        return texts


class SpeechServer:

    def __init__(self, speech: SpeechRecognizer):
        super().__init__()
        self.speech = speech
        #Generate new key
        session_key = os.urandom(24)
        #Init server
        self.app = Flask(__name__, instance_relative_config=True)
        self.app.config['SECRET_KEY'] = session_key
        #Endpoints
        #Recognize
        @self.app.route('/recognize/<language>/<profile>/<amount>', methods=['POST'])
        def login(language, profile, amount):
            audio = numpy.fromstring(request.get_data(), dtype=numpy.int16)
            return json.dumps(self.speech.recognize(language, profile, audio, int(amount)))

    def run(self):
        self.app.run(debug = False, port = 8082, host = '0.0.0.0', ssl_context='adhoc')
