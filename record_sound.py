import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()  # 初始化
audio_params = {
    "format": FORMAT,
    "channels": CHANNELS,
    "rate": RATE,
    "input": True,
    "frames_per_buffer": CHUNK
}


def save_audio(file, frames):
    wf = wave.open(file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(frames)
    wf.close()
