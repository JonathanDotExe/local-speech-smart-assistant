import simpleaudio
import wave
import numpy
import pyttsx3
import picotts
import marytts
import io


class ESpeakEngine:

    def __init__(self):
        self.engine = pyttsx3.init()
    
    def set_voice(self, language):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            for lang in voice.languages:
                if language in str(lang):
                    print('set voice to', voice)
                    self.engine.setProperty('voice', voice.id)
                    break

    def speak(self, text):
        if text and text.strip():
            self.engine.say(text)
            self.engine.runAndWait()

class MaryTTSEngine:

    def __init__(self):
        self.engine = marytts.MaryTTS()
    
    def set_voice(self, language):
        for voice in self.engine.voices:
            if language in voice[1]:
                self.engine.locale = language
                self.engine.voice = voice[0]
                break

    def speak(self, text):
        wavs = self.engine.synth_wav(text)
        with wave.open(io.BytesIO(wavs)) as wav:
            wav_obj = simpleaudio.WaveObject.from_wave_read(wav)
            wav_obj.play().wait_done()

class PicoTTSEngine:

    def __init__(self):
        self.engine = picotts.PicoTTS()
    
    def set_voice(self, language):
        voices = self.engine.voices
        for voice in voices:
            if language in str(voice):
                self.engine.voice = voice
                break

    def speak(self, text):
        wavs = self.engine.synth_wav(text)
        with wave.open(io.BytesIO(wavs)) as wav:
            wav_obj = simpleaudio.WaveObject.from_wave_read(wav)
            wav_obj.play().wait_done()
