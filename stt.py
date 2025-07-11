# pip3 install -U funasr-onnx
from funasr_onnx import Paraformer
import time

model_dir = "./model/paraformer"
model = Paraformer(model_dir, batch_size=1, quantize=True)

stt = lambda x: model([x])[0]['preds'][0]

if __name__ == '__main__':
    wav_path = './kws.wav'
    result = stt(wav_path)
    print(result)

    t1 = time.time()
    result = stt(wav_path)
    print(result)
    print(time.time() - t1)
