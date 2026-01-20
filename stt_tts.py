# pip3 install -U funasr-onnx
from funasr_onnx import Paraformer
import time
import subprocess
import re

model_dir = "./paraformer"
model = Paraformer(model_dir, batch_size=1, quantize=True)

stt = lambda x: model([x])[0]['preds'][0]

tts_proc = None
def tts(s):
    while True:
        if tts_proc is None or tts_proc.poll() is not None:
            subprocess.run(f"termux-tts-speak '{s}'", shell=True, check=True)
            break
        time.sleep(0.2)


def tts_async(s):
    global tts_proc
    while True:
        if tts_proc is None or tts_proc.poll() is not None:
            tts_proc = subprocess.Popen(f"termux-tts-speak '{s}'", shell=True)
            break
        time.sleep(0.2)
    



if __name__ == '__main__':
    wav_path = './kws.wav'
    result = stt(wav_path)
    print(result)

    t1 = time.time()
    result = stt(wav_path)
    print(result)
    print(time.time() - t1)
