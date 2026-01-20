from flask import Flask, send_file, Response
from flask_cors import CORS
from llm import *
from stt_tts import stt, tts, tts_async
from kws import kws
from vad import is_speech
import threading
import json
import time
from queue import Queue
import re
import toolbox
import requests
from prompt import *
from record_sound import *
from pathlib import Path

app = Flask(__name__, static_folder='./static')

audio_queue = Queue()
sentence_queue = Queue()
connect_count=0

def send_msg(msg_type, msg=None):
    if msg is None:
        msg_sse = json.dumps({"type": msg_type})
    else:
        msg_sse = json.dumps({"type": msg_type, "msg": msg})
    return f"data: {msg_sse}\n\n"


@app.route("/")
def hello():
    load_model(1)
    return send_file('./html-test.html')


# SSE 路由
@app.route('/stream')
def stream():
    return Response(event_stream(), content_type='text/event-stream')

def wait_until_1():
    while connect_count > 1:
        time.sleep(0.2)
            

def event_stream():
    global connect_count
    connect_count += 1
    wait_until_1()
    stream_lst = []

    try:
        while True:
            index = 1
            yield send_msg('debug')
            stream_kws = p.open(**audio_params)
            if stream_kws not in stream_lst:
                stream_lst.append(stream_kws)
            kws_q = Queue()
            kws_running = True
            def kws_worker():
                while kws_running:
                    data = stream_kws.read(CHUNK)
                    kws_q.put(data)

            t_kws = threading.Thread(target=kws_worker)
            t_kws.start()
            LastFrame = []
            while True:
                yield send_msg('debug')
                audio_time = 3 if index == 1 else 2
                current = []
                for i in range(0, int(RATE * audio_time / CHUNK)):
                    data = kws_q.get()
                    current.append(data)
                frames = LastFrame + current
                yield send_msg('debug')
                save_audio('kws.wav', b''.join(frames))
                LastFrame = frames[len(frames) * 2 // 3:]
                ret = kws('kws.wav')
                if ret:
                    kws_running = False
                    t_kws.join()
                    stream_lst.remove(stream_kws)
                    stream_kws.stop_stream()
                    stream_kws.close()
                    yield send_msg('debug')
                    tts('我在！')
                    break
                index += 1
            
            yield send_msg('to_recording')
            stream_record = p.open(**audio_params)
            if stream_record not in stream_lst:
                stream_lst.append(stream_record)
            record_q = Queue()
            is_recording = True

            def record_worker():
                while is_recording:
                    data = stream_record.read(CHUNK)
                    record_q.put(data)
            
            t_rec = threading.Thread(target=record_worker)
            t_rec.start()

            total = []
            while True:
                yield send_msg('debug')
                audio_time = 1.5
                current = []
                for i in range(0, int(RATE * audio_time / CHUNK)):
                    data = record_q.get()
                    current.append(data)
                frames = current
                yield send_msg('debug')
                save_audio('vad.wav', b''.join(frames))
                ret = is_speech('vad.wav')

                if ret:
                    total += current
                    continue
                else:
                    if total == []:  # 第一轮循环就没人说话，则退出
                        is_recording = False
                        t_rec.join()
                        stream_lst.remove(stream_record)
                        stream_record.stop_stream()
                        stream_record.close()
                        break

                is_recording = False
                t_rec.join()
                stream_lst.remove(stream_record)
                stream_record.stop_stream()
                stream_record.close()
                yield send_msg('to_stt')
                save_audio('recording.wav', b''.join(total))
                inp = stt('recording.wav')
                inp = inp[0].upper() + inp[1:]
                yield send_msg('human_msg', inp)
                tts_async('录音结束，模型推理中。')

                # stage 1
                prompt1 = prompt_template1.format(question=inp, )
                # print('*' * 40, '\n', prompt1)
                chat = llm(prompt1)
                yield send_msg('prefixing')
                sentence = next(chat)
                yield send_msg('decoding')
                yield send_msg('stage1', sentence)
                for chunk in chat:
                    sentence += chunk
                    yield send_msg('stage1', chunk)
                action_dict = extract_yaml(sentence)

                if action_dict['Is_clear'] == 'No':
                    img_ret = toolbox.photography()
                    yield send_msg('photo', img_ret)
                    # stage 2
                    prompt2 = prompt_template2.format(question=inp, )
                    # print('*' * 40, '\n', prompt2)
                    chat = llm(prompt2, './onsite_img.jpg')
                    yield send_msg('prefixing')
                    sentence = next(chat)
                    yield send_msg('decoding')
                    yield send_msg('stage2', sentence)
                    for chunk in chat:
                        sentence += chunk
                        yield send_msg('stage2', chunk)
                    action_dict = extract_yaml(sentence)
                    inp = action_dict['Real_question']

                folder = 'Building_Construction_Handbook'
                fname = folder + '.md'
                fpath = f'./documents/{folder}/{fname}'
                yield send_msg('retrieve', fname)
                unload_model(1)
                load_model(0)
                clear_cache()
                load_cache(folder)
                file_content = toolbox.retrieve(fpath)
                

                # stage 3
                prompt3 = prompt_template3.format(
                    file_content=file_content,
                    question=inp,
                )
                # print('*' * 40, '\n', prompt3)
                chat = llm(prompt3)
                yield send_msg('prefixing')
                sentence = next(chat)
                yield send_msg('decoding')
                is_speaking = False
                tts_text = ''
                for chunk in chat:
                    sentence += chunk
                    if len(sentence.split('\n')) < 3:
                        if '\nAnswer: ' in sentence:
                            yield send_msg('stage3', chunk)
                            tts_text += chunk
                    else:
                        if is_speaking == False:
                            yield send_msg('stage3', chunk.split('\n')[0])
                            tts_text += chunk.split('\n')[0]
                            yield send_msg('tts')
                            tts_async(tts_text)
                            is_speaking = True
                
                action_dict = extract_yaml(sentence)
                
                if 'Block_idx' in action_dict:
                    yield send_msg('ref', toolbox.show_ref(folder, action_dict['Block_idx']))
                else:
                    yield send_msg('stage3', '建议咨询其他工程师以获取更准确的答案。')
                    tts_async('建议咨询其他工程师以获取更准确的答案。')
                unload_model(0)
                load_model(1)
                tts('')
                break
            yield send_msg('to_waking')
    except GeneratorExit:
        print("客户端断开连接")
    finally:
        connect_count -= 1
        for item in stream_lst:
            item.stop_stream()
            item.close()
            


if __name__ == "__main__":
    print('http://localhost:8000')
    CORS(app)
    app.run(port=8000, )
