import requests
import toolbox
from llm import llm
import os

file_lst = [d for d in os.listdir('./documents')]
prompt_template = '''
You are an AI civil engineer with profound knowledge of various construction procedures and technologies.
{file_content}
--------------------
Please summarize this document in one sentence.
'''
for f in file_lst:
    print('*' * 20)
    print(f)
    prompt = prompt_template.format(file_content=toolbox.retrieve(f))
    print(prompt)
    ret = llm(prompt)
    for chunk in ret:
        print(chunk, end='', flush=True)
    url = 'http://127.0.0.1:8080'
    response = requests.post(url=f"{url}/slots/0?action=save", json={'filename': f + '.bin'})
    assert response.status_code == 200
    response = requests.post(url=f"{url}/slots/0?action=erase")
    assert response.status_code == 200
