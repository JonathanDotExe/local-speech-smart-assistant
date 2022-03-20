import os
import torch
import time
import sounddevice
import numpy

from TTS.tts.utils.generic_utils import setup_model
from TTS.tts.utils.synthesis import synthesis
from TTS.tts.utils.text.symbols import symbols, phonemes
from TTS.utils.io import load_config
from TTS.utils.audio import AudioProcessor
from TTS.tts.utils.io import load_checkpoint
from TTS.vocoder.utils.generic_utils import setup_generator
from TTS.vocoder.utils.io import load_checkpoint as load_vocoder_checkpoint

def tts(model, text, CONFIG, use_cuda, ap, use_gl, figures=True):
    t_1 = time.time()
    waveform, alignment, mel_spec, mel_postnet_spec, stop_tokens, inputs = synthesis(model, text, CONFIG, use_cuda, ap, speaker_id, style_wav=None,
                                                                             truncated=False, enable_eos_bos_chars=CONFIG.enable_eos_bos_chars)
    # mel_postnet_spec = ap._denormalize(mel_postnet_spec.T)
    if not use_gl:
        waveform = vocoder_model.inference(torch.FloatTensor(mel_postnet_spec.T).unsqueeze(0))
        waveform = waveform.flatten()
    if use_cuda:
        waveform = waveform.cpu()
    waveform = waveform.numpy()
    rtf = (time.time() - t_1) / (len(waveform) / ap.sample_rate)
    tps = (time.time() - t_1) / len(waveform)
    print(waveform.shape)
    print(" > Run-time: {}".format(time.time() - t_1))
    print(" > Real-time factor: {}".format(rtf))
    print(" > Time per step: {}".format(tps))
    return alignment, mel_postnet_spec, stop_tokens, waveform

use_cuda = False
TTS_MODEL = "data/tts_model.pth.tar"
TTS_CONFIG = "data/tts_config.json"
VOCODER_MODEL = "data/vocoder_model.pth.tar"
VOCODER_CONFIG = "data/vocoder_config.json"

TTS_CONFIG = load_config(TTS_CONFIG)
VOCODER_CONFIG = load_config(VOCODER_CONFIG)

ap = AudioProcessor(**TTS_CONFIG.audio) 

speaker_id = None
speakers = []

num_chars = len(phonemes) if TTS_CONFIG.use_phonemes else len(symbols)
model = setup_model(num_chars, len(speakers), TTS_CONFIG)

model, _ = load_checkpoint(model, TTS_MODEL, use_cuda=use_cuda)
model.eval()

vocoder_model = setup_generator(VOCODER_CONFIG)
vocoder_model, _ = load_vocoder_checkpoint(vocoder_model, checkpoint_path=VOCODER_MODEL)
vocoder_model.remove_weight_norm()
vocoder_model.inference_padding = 0

ap_vocoder = AudioProcessor(**VOCODER_CONFIG['audio'])    
if use_cuda:
    vocoder_model.cuda()
vocoder_model.eval()

sentence = input('Scentence: ')
align, spec, stop_tokens, wav = tts(model, sentence, TTS_CONFIG, use_cuda, ap, use_gl=False, figures=True)

sounddevice.play(numpy.array(wav), TTS_CONFIG.audio['sample_rate'])
sounddevice.wait()
