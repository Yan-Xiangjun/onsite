# Get predictions for individual WAV files (16-bit 16khz PCM)
# use openwakeword==0.4.0
from openwakeword.model import Model
import openwakeword
import os

model_path = os.path.dirname(openwakeword.__file__) + "/resources/models/hey_mycroft_v0.1.onnx"
model = Model([model_path])


def kws(path):
    out = model.predict_clip(path, padding=0)
    ret = [item['hey_mycroft_v0.1'] for item in out]
    for i in range(len(ret) - 2):
        if ret[i] > 0.9 and ret[i + 1] > 0.9 and ret[i + 2] > 0.9:
            return True
    return False


# print(kws('F:/开发/语音工具包/openwakeword/kws.wav'))
