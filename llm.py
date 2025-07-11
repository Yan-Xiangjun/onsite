from prompt import *
from openai import OpenAI
import requests
import json
import toolbox


def llm(query):
    url = 'http://127.0.0.1:8080'
    messages = {'messages': [{'role': 'user', 'content': query}]}
    response = requests.post(url=f"{url}/apply-template", json=messages)
    prompt = json.loads(response.text)['prompt']
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
    # client = OpenAI(api_key='key', base_url=url)
    # ret = client.chat.completions.create(model='model',
    #                                      messages=[{'role': 'user', 'content': query}],
    #                                      stream=True,
    #                                      temperature=0.01)
    # for chunk in ret:
    #     yield chunk.choices[0].delta.content


if __name__ == "__main__":
    from test import testprompt
    # sysp = prompt_template1
    # userp = 'Generally speaking what is the floor height of a residential building'
    # userp = 'What are they made of'
    userp = 'What is the first step to building a spiral staircase'
    # userp = 'To install them on the ground how much space should I leave between them and the wall'
    # userp = 'When I use them what points about time should I notice'
    # userp = 'How to prevent their displacement as much as possible'
    # userp = 'How to prevent rebar displacement as much as possible when casting concrete'
    userp = prompt_template1.format(question=userp)
    print('Prompt:', userp)
    ret = llm(userp)
    for chunk in ret:
        print(chunk, end='', flush=True)
