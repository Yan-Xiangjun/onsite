import os
from prompt import *
import requests
import base64
import json
import re
import yaml
from time import sleep

url = ''
url0 = 'http://127.0.0.1:8080'


def to_b64(fname):
    with open(fname, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image


def extract_yaml(s):
    pattern = r'```yaml\n(.*?)```'
    match = re.search(pattern, s, re.DOTALL)
    return yaml.safe_load(match[1])


def llm(query, img=None):
    query = query + '\n<__media__>' if img is not None else query
    messages = {'messages': [{'role': 'user', 'content': query}]}
    response = requests.post(url=f"{url}/apply-template", json=messages)
    prompt = json.loads(response.text)['prompt']
    if img is not None:
        prompt = {"prompt_string": prompt, "multimodal_data": [to_b64(img)]}
    data_send = {'prompt': prompt, 'stream': True, 'temperature': 0.01, 'id_slot': 0}

    with requests.post(url=f"{url}/completion", json=data_send, stream=True) as ret:
        buffer = ''
        for chunk in ret.iter_content(chunk_size=None):
            if chunk:
                # 将字节转换为字符串并添加到缓冲区
                buffer += chunk.decode('utf-8')
                if "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)
                    json_str = event[5:].strip()  # 去掉"data:"
                    data = json.loads(json_str)
                    yield data["content"]
    yield ' '


def clear_cache():
    response = requests.post(url=f"{url}/slots/0?action=erase")
    assert response.status_code == 200


def load_cache(fname):
    response = requests.post(
        url=f"{url}/slots/0?action=restore",
        json={'filename': f'{fname}.bin'},
    )
    assert response.status_code == 200


def save_cache(fname):
    response = requests.post(
        url=f"{url}/slots/0?action=save",
        json={'filename': f'{fname}.bin'},
    )
    assert response.status_code == 200


def load_model(num):
    model_name = 'qwen3-vl-text' if num == 0 else 'qwen3-vl'
    is_loaded = False
    while True:
        status = requests.get(url=f"{url0}/models").json()
        for m in status['data']:
            if m['id'] == model_name:
                if m['status']['value'] == 'unloaded':
                    response = requests.post(
                        url=f"{url0}/models/load",
                        json={'model': model_name},
                    )
                    assert response.status_code == 200
                elif m['status']['value'] == 'loading':
                    sleep(0.2)
                else:
                    is_loaded = True
                break
        if is_loaded:
            break

    global url
    status = requests.get(url=f"{url0}/models").json()
    for m in status['data']:
        if m['id'] == model_name:
            lst = m['status']['args']
            port = lst[lst.index('--port') + 1]
            url = f"http://127.0.0.1:{port}"
            # print(url)
            break


def unload_model(num):
    model_name = 'qwen3-vl-text' if num == 0 else 'qwen3-vl'
    response = requests.post(
        url=f"{url0}/models/unload",
        json={'model': model_name},
    )
    assert response.status_code == 200


if __name__ == "__main__":
    load_model(1)
    # userp = 'What is the first step to building a spiral staircase'
    userp = '描述这张图: '
    print('Prompt:', userp)
    ret = llm(userp, img='F:/zl226.jpg')
    for chunk in ret:
        print(chunk, end='', flush=True)
