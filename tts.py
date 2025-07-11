from time import time
from transformers import AutoTokenizer
from onnxruntime import InferenceSession
import numpy as np
from num2words import num2words
import re

tokenizer = AutoTokenizer.from_pretrained("model/mms-tts-eng/onnx")
session = InferenceSession("model/mms-tts-eng/onnx/model.onnx")


# text = 'some fascinating careers are paving the way for artificial intelligence to help us all out in our daily lives and at work.'
def tts(s):
    inputs = tokenizer(s, return_tensors="np")
    inputs = {k: v.astype(np.int64) for k, v in inputs.items()}
    outputs = session.run(output_names=["waveform"], input_feed=inputs)
    return np.int16(outputs[0].T * 32767)


def split_sentence(text):
    # 去掉引用
    text = re.sub(r'\[Part-\d+-Step-\d+\]', '', text)
    # 处理长度单位
    text = re.sub(r'(?<=\d\s)km(?=\W)', 'kilometers', text)
    text = re.sub(r'(?<=\d\s)m(?=\W)', 'meters', text)
    text = re.sub(r'(?<=\d\s)cm(?=\W)', 'centimeters', text)
    text = re.sub(r'(?<=\d\s)mm(?=\W)', 'millimeters', text)
    text = re.sub(r'(?<=\d\s)mi(?=\W)', 'miles', text)
    text = re.sub(r'(?<=\d\s)yd(?=\W)', 'yards', text)
    text = re.sub(r'(?<=\d\s)ft(?=\W)', 'feet', text)
    text = re.sub(r'(?<=\d\s)in(?=\W)', 'inches', text)
    text = text.replace('one kilometers', 'one kilometer')
    text = text.replace('one meters', 'one meter')
    text = text.replace('one centimeters', 'one centimeter')
    text = text.replace('one millimeters', 'one millimeter')
    text = text.replace('one miles', 'one mile')
    text = text.replace('one yards', 'one yard')
    text = text.replace('one feet', 'one foot')
    text = text.replace('one inches', 'one inch')

    #序数词1. abc-> first abc
    text = re.sub(r'(\d+)(\.\s)', lambda x: num2words(x[1], True) + ' ', text)
    #处理分数
    text = re.sub(
        r'(\d+)/(\d+)', lambda x: num2words(x[1]) + ' ' + num2words(x[2], True) +
        ('s' if int(x[1]) > 1 else ''), text)

    text = re.sub(r'\d(?=[a-zA-Z])', lambda x: x[0] + ' ', text)
    text = re.sub(r'\d+(\.\d+)?', lambda x: num2words(x[0]), text)
    text_lst = re.split(r'([.!?:])\s+', text)
    return text_lst


if __name__ == "__main__":
    text = '1. There are 3 in fascinating 12 cm careers are 1/4 paving the way.\n2. for artificial intelligence to help us.\n3. all out in our daily lives and at work.'
    text = 'There are 3 in fascinating 12 cm careers are 1/4 paving the way.'
    print(split_sentence(text))
    # text = 'Hello world!'
    # text = 'Hello world! 1234.56'
    # text = 'Hello world! 1234.56abc'
    # text = 'Hello world!
# #将浮点 PCM 数据转换为整数 PCM，否则with wave.open("techno.wav", 'rb') as wf:报错
# import wave
# import pyaudio

# p = pyaudio.PyAudio()
# with wave.open("techno.wav", 'rb') as wf:
#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                     channels=wf.getnchannels(),
#                     rate=wf.getframerate(),
#                     output=True)
#     stream.write(wf.readframes(wf.getnframes()))
#     stream.stop_stream()
#     stream.close()
