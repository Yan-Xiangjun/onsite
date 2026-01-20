import toolbox
from llm import *
import os

prompt_template = '''
你是一名经验丰富的AI土木工程师，熟悉各类施工工艺和技术。
这是当前工程项目的施工文档的内容：
---
用户的问题: "外墙喷涂前铺纤维布的时候应当怎样操作？"
---
请分析用户的问题是否清晰明了，包含了工作对象（何种建筑构件）、工作内容（哪一施工过程）等背景信息，使回答者能快速定位问题的关键，而不需进一步猜测其意图。
例如，“我应该怎样安装屋面檩条？”是一个清晰的问题，而“怎么安装这个构件？”是一个不清晰的问题。
你必须使用以下格式回复：
```yaml
Thought: 针对该问题，写出简短的思考过程。
Is_clear: "Yes" 或 "No"。
```
你的回答只能包含以上两个字段，不要包含其他内容。
'''
load_model(0)
# f = 'Harbin_Project_1'
f='Building_Construction_Handbook'
prompt = prompt_template
print(prompt)
ret = llm(prompt)
for chunk in ret:
    print(chunk, end='', flush=True)
