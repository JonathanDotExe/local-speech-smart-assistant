import wave
import picotts
import io
import simpleaudio

tts = picotts.PicoTTS()
print(tts.voices)
tts.voice = 'de-DE'
wavs = tts.synth_wav('Hallo Welt! Ich bin Hans! Dein persönlicher Assistent! 1 2 3 4 5')
wav = wave.open(io.BytesIO(wavs))

wav_obj = simpleaudio.WaveObject.from_wave_read(wav)
wav_obj.play().wait_done()
