import toolbox
import yaml
import json
from prompt import *
from llm import *
import requests
from pathlib import Path
import os
from time import time
from PIL import Image

with open('./benchmark/test_data1.yaml', 'r', encoding='utf-8') as f:
    data = yaml.full_load(f)

results_data = []
detail = []
load_model(1)

for k in data:
    start_time = time()
    inp = data[k]['text']
    out_result = [inp, '']
    print('Question:', inp)
    # stage 1
    prompt1 = prompt_template1.format(question=inp, )
    chat = llm(prompt1)
    sentence = next(chat)
    for chunk in chat:
        sentence += chunk
    action_dict = extract_yaml(sentence)
    out_result[1] += sentence + '\n'

    if action_dict['Is_clear'] == 'No':
        if not data[k]['img']:
            out_result.append('Failed')
            out_result.append(f'{time() - start_time:.2f}')
            results_data.append({
                'question': out_result[0],
                'process': out_result[1],
                'final_answer': out_result[2],
                'time': out_result[3]
            })
            continue

        toolbox.photography('./benchmark/img/' + data[k]['img'])
        # stage 2
        prompt2 = prompt_template2.format(question=inp, )
        chat = llm(prompt2, './benchmark/img/' + data[k]['img'])
        sentence = next(chat)
        for chunk in chat:
            sentence += chunk
        action_dict = extract_yaml(sentence)
        inp = action_dict['Real_question']
        out_result[1] += sentence + '\n'

    folder = 'Harbin_Project_1'
    fname = folder + '.md'
    fpath = f'./documents/{folder}/{fname}'
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
    chat = llm(prompt3)
    final_answer = next(chat)
    for chunk in chat:
        final_answer += chunk

    end_time = time()
    out_result.append(final_answer)
    out_result.append(f'{end_time - start_time:.2f}')

    results_data.append({
        'question': out_result[0],
        'process': out_result[1],
        'final_answer': out_result[2],
        'time': out_result[3]
    })
    unload_model(0)
    load_model(1)

# 保存为json文件
json_path = './benchmark/test_result.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results_data, f, ensure_ascii=False, indent=4)
import pandas as pd


def convert_json_to_excel(json_file, excel_file):
    # 读取json文件，转化为python字典
    with open(json_file, 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    # 构建二维list作为表格
    table = [['question', 'process', 'final_answer', 'time']]
    for item in data_list:
        table.append([item['question'], item['process'], item['final_answer'], item['time']])

    # 把表格保存为Excel文件
    df = pd.DataFrame(table)
    df.to_excel(excel_file, index=False, header=False)


# 执行转换
convert_json_to_excel(json_path, './benchmark/test_result.xlsx')
