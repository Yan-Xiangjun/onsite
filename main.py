from flask import Flask, send_file, Response
from flask_cors import CORS
from llm import llm
from stt import stt
from kws import kws
from tts import tts, split_sentence
from vad import speech_is_end
import threading
import json
import time
from queue import Queue
import scipy
import re
import toolbox
import yaml
import requests
from prompt import *
from record_sound import *

app = Flask(__name__, static_folder='./static')

audio_queue = Queue()
sentence_queue = Queue()
file_names = '\n'.join([f'{d}.md' for d in os.listdir('./documents')])


def send_msg(msg_type, msg=None):
    if msg is None:
        msg_sse = json.dumps({"type": msg_type})
    else:
        msg_sse = json.dumps({"type": msg_type, "msg": msg})
    return f"data: {msg_sse}\n\n"


def extract_yaml(s):
    pattern = r'```yaml\n(.*?)```'
    match = re.search(pattern, s, re.DOTALL)
    return yaml.safe_load(match[1])


def start_tts():
    while True:
        s = sentence_queue.get()
        if s is None:
            break
        audio_queue.put(tts(s))
    audio_queue.put(None)


def play_tts(audio_queue):
    while True:
        audio_data = audio_queue.get()
        if audio_data is None:
            break
        scipy.io.wavfile.write("tts.wav", rate=16000, data=audio_data)
        play_audio("tts.wav")


@app.route("/")
def hello():
    return send_file('./html-test.html')


# SSE 路由
@app.route('/stream')
def stream():
    return Response(event_stream(), content_type='text/event-stream')


def event_stream():
    while True:
        index = 1
        stream_kws = p.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        LastFrame = []
        while True:
            audio_time = 3 if index == 1 else 2
            current = []
            for i in range(0, int(RATE * audio_time / CHUNK)):
                data = stream_kws.read(CHUNK)
                current.append(data)
            frames = LastFrame + current
            save_audio('kws.wav', b''.join(frames))
            LastFrame = frames[len(frames) * 2 // 3:]

            ret = kws('kws.wav')
            if ret:
                yield send_msg('to_recording')
                play_audio('welcome.wav')
                break
            index += 1

        stream_record = p.open(format=FORMAT,
                               channels=CHANNELS,
                               rate=RATE,
                               input=True,
                               frames_per_buffer=CHUNK)
        LastFrame = []
        total = []
        while True:
            audio_time = 1
            current = []
            for i in range(0, int(RATE * audio_time / CHUNK)):
                data = stream_record.read(CHUNK)
                current.append(data)
            frames = current
            save_audio('vad.wav', b''.join(frames))
            total += current
            ret = speech_is_end('vad.wav')
            if ret:
                yield send_msg('to_stt')
                save_audio('recording.wav', b''.join(total))
                inp = stt('recording.wav')
                inp = inp[0].upper() + inp[1:]
                yield send_msg('human_msg', inp)
                tts_thread = threading.Thread(target=start_tts)
                tts_thread.start()
                player = threading.Thread(target=play_tts, args=(audio_queue,))
                player.start()

                # stage 1
                prompt1 = prompt_template1.format(question=inp)
                print(prompt1)
                sentence = ''
                yield send_msg('prefixing')
                for chunk in llm(prompt1):
                    if sentence == '':
                        yield send_msg('decoding')
                    sentence += chunk
                    yield send_msg('stage1', chunk)

                img_desc = ''
                action_dict = extract_yaml(sentence)
                if action_dict['Problem_analysis'] == 'Ambiguous':
                    img_ret = toolbox.photography()
                    yield send_msg('photo', next(img_ret))
                    yield send_msg('prefixing')
                    for chunk in img_ret:
                        if img_desc == '':
                            yield send_msg('decoding')
                            yield send_msg('img_desc', '📷')
                        yield send_msg('img_desc', chunk)
                        img_desc += chunk
                    img_desc = 'What you are currently seeing:\n' + img_desc

                # stage 2
                prompt2 = prompt_template2.format(file_names=file_names,
                                                  question=inp,
                                                  image_description=img_desc)
                print('*' * 40)
                print(prompt2)
                sentence = ''
                yield send_msg('prefixing')
                for chunk in llm(prompt2):
                    if sentence == '':
                        yield send_msg('decoding')
                    sentence += chunk
                    yield send_msg('stage2', chunk)

                action_dict = extract_yaml(sentence)
                fname = action_dict['FileName']
                if fname != 'Empty':
                    yield send_msg('retrieve', fname)
                    file_content = toolbox.retrieve(fname)
                    ref = prompt_ref
                    response = requests.post(url=f"http://127.0.0.1:8080/slots/0?action=erase")
                    assert response.status_code == 200
                    response = requests.post(url=f"http://127.0.0.1:8080/slots/0?action=restore",
                                             json={'filename': f'{os.path.splitext(fname)[0]}.bin'})
                    assert response.status_code == 200
                else:
                    file_content = ''
                    ref = ''

                # stage 3
                prompt3 = prompt_template3.format(image_description=img_desc,
                                                  file_content=file_content,
                                                  question=inp,
                                                  show_ref=ref)
                print('*' * 40)
                print(prompt3)
                sentence = ''
                yield send_msg('prefixing')
                for chunk in llm(prompt3):
                    if sentence == '':
                        yield send_msg('decoding')
                    sentence += chunk
                    yield send_msg('stage3', chunk)

                yield send_msg('tts')
                s_lst = split_sentence(sentence)
                for i in range(0, len(s_lst) - 1, 2):
                    sentence_queue.put(s_lst[i] + s_lst[i + 1])

                cite = re.findall(r'(?<=\[)Part-\d+-Step-\d+(?=\])', sentence)
                if len(cite) > 0:
                    yield send_msg('ref', toolbox.show_ref(cite, file_content))
                sentence_queue.put(None)
                tts_thread.join()
                player.join()
                break
        yield send_msg('to_waking')


if __name__ == "__main__":
    CORS(app)
    app.run(port=8000)
