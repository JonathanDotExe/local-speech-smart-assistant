import deepspeech
import numpy
import pyaudio

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

