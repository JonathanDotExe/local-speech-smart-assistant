import pyaudio
import numpy
import math
import enum
import threading
from slave.util import pixel_ring_wrapper

class VolumeGate:

    def __init__(self, gate = 0.03, time_out = 2.0):
        self.gate = gate
        self.time_out = time_out
        self.attack = 0.005
        self.release = 0.1
        self.reset()
    
    def reset(self):
        self.last_time = -self.time_out - 1
    
    def process(self, sample: float, time: float):
        #Update timeout
        if (abs(sample) >= self.gate):
            self.last_time = time
        #Eventually clear
        if time > self.last_time + self.time_out:
            sample = 0
        return sample
    
    def mute(self, time: float):
        return time > self.last_time + self.time_out

class SpeechRecorderState(enum.Enum):
    WAKEWORD = 0
    PAUSE = 1
    COMMAND = 2

class SpeechRecorder:

    def __init__(self, device = 0, noise_gate = 0.03):
        super().__init__()
        self.lock = threading.Lock()
        self.audio = pyaudio.PyAudio()
        #Audio stream
        self.sample_rate = 16000
        self.channels = 1
        #List devices
        for i in range(0, self.audio.get_host_api_info_by_index(0).get('deviceCount')):
            dev = self.audio.get_device_info_by_host_api_device_index(0, i)
            print(i, ": ", dev['name'], " with ", dev['maxInputChannels'], " channels, Sample Rate", dev['defaultSampleRate'])

        try:
            dev = self.audio.get_default_input_device_info()
            print("Default: ", dev['name'], " with ", dev['maxInputChannels'], " channels, Sample Rate", dev['defaultSampleRate'])
            self.stream = self.audio.open(format=pyaudio.paFloat32, channels=self.channels, rate=self.sample_rate, input=True, frames_per_buffer=1024, stream_callback=self.callback, input_device_index=device)
        except OSError as e:
            self.stream = None
            print("Couldn't open audio device: ", e)
        #Recording
        self.data = []
        self.time = 0
        self.time_step = 1.0/self.sample_rate
        self.submit = lambda d, a : 0
        self.state = SpeechRecorderState.WAKEWORD
        #Command
        self.gate = VolumeGate(noise_gate)
        self.recording = False
        self.time_out = 15
        #Wakeword
        self.wakeword_duration = 5
        self.wakeword_interval = 4
        self.last_recognize = 0
        
    
    def convert(self, data: [float], sample_rate: float, goal_sample_rate: float):
        if sample_rate == goal_sample_rate:
            return [*data]
        converted = []
        step = sample_rate / goal_sample_rate
        for i in range(0, int(len(data)/step)):
            index = i * step
            first_i = int(math.floor(index))
            second_i = int(math.ceil(index))
            first = data[first_i]
            second = data[second_i]
            prog = index - first_i
            converted.append(first * (1 - prog) + second * prog)
        return converted

    def callback(self, inp, frames, time, status):
        for i in numpy.fromstring(inp, dtype=numpy.float32):
            with self.lock:
                self.gate.process(i, self.time)
                if self.state == SpeechRecorderState.COMMAND:
                    #Stop recording
                    if (self.gate.mute(self.time) or len(self.data) > ((self.time_out + 2) * self.sample_rate)) and self.recording:
                        print("Stop recording")
                        pixel_ring_wrapper.off()
                        self.recording = False
                        self.submit(self.data.copy(), self.is_awake())
                        self.data = []
                    #Start recording
                    elif not self.gate.mute(self.time) and not self.recording:
                        print("Start recording")
                        pixel_ring_wrapper.wakeup()
                        self.recording = True
                    
                    #Record
                    self.data.append(i)
                    if not self.recording and len(self.data) > (self.sample_rate * 2):
                        self.data = self.data[-(self.sample_rate * 2):]
                elif self.state == SpeechRecorderState.WAKEWORD:
                    #Record
                    self.data.append(i)
                    if len(self.data) > (self.sample_rate * (self.wakeword_duration + 1)):
                        self.data = self.data[-(self.sample_rate * self.wakeword_duration):]
                    #Recognize
                    if self.last_recognize < self.time - self.wakeword_interval:
                        self.last_recognize = self.time
                        if self.gate.last_time >= self.time - self.wakeword_interval:
                            print("Submitting recording")
                            self.submit(self.data.copy(), self.is_awake())
                        else:
                            print("Too quiet! Not recognizing voice!")
                elif self.state == SpeechRecorderState.PAUSE:
                    pass
                self.time += self.time_step
        return (inp, pyaudio.paContinue)

    # Lock has to be aquired
    def set_state(self, state):
        if self.state != state:
            self.last_recognize = self.time
            self.recording = False
            self.data = []
            self.gate.reset()
        self.state = state
    
    def is_awake(self):
        return self.state != SpeechRecorderState.WAKEWORD

    def run(self):
        if self.stream:
            self.stream.start_stream()
    
    def close(self):
        if self.stream:
            self.stream.close()
        self.audio.terminate()