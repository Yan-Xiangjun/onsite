import numpy as np
import pyaudio
import wave
import os

path = os.path.split(os.path.realpath(__file__))[0]
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()  # 初始化


def save_audio(file, frames):
    wf = wave.open(file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(frames)
    wf.close()


def play_audio(file):
    with wave.open(file, 'rb') as wf:
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        stream.write(wf.readframes(wf.getnframes()))
        stream.stop_stream()
        stream.close()
