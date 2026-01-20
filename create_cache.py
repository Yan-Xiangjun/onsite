import toolbox
from llm import *
import os

prompt_template = '''
你是一名经验丰富的AI土木工程师，熟悉各类施工工艺和技术。
这是当前工程项目的施工文档的内容：
{file_content}
---
用户的问题: "请用一句话总结该文档的内容。"
'''
load_model(0)
# f = 'Harbin_Project_1'
f='Building_Construction_Handbook'
prompt = prompt_template.format(file_content=toolbox.retrieve(f'./documents/{f}/{f}.md'))
print(prompt)
ret = llm(prompt)
for chunk in ret:
    print(chunk, end='', flush=True)
save_cache(f)
clear_cache()
