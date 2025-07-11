import os
import subprocess
from PIL import Image, ImageOps
import base64
import re

working_dir = ''
vl_path = './model/qwen2-vl/Qwen2-VL-2B-Instruct-Q4_0.gguf'
mmproj = './model/qwen2-vl/qwen2-vl-2b-instruct-vision.gguf'

vlm_process = subprocess.Popen(
    f'~/llama.cpp-b5009/build/bin/llama-qwen2vl-cli -m {vl_path} --mmproj {mmproj} --image ~/on_site/placeholder.jpg -p Hello --threads 6 --temp 0.01 -c 8192',
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    universal_newlines=True,
    shell=True,
    text=True,
    bufsize=1)
while True:
    out = vlm_process.stdout.readline()
    print(out, end='', flush=True)
    if out.endswith('<ED>\n'):
        break


def vlm(user_prompt, img='./placeholder.jpg'):
    user_prompt = user_prompt.replace('\n', '<LF>')
    vlm_process.stdin.write(img + '\n')
    vlm_process.stdin.flush()
    vlm_process.stdin.write(user_prompt + '\n')
    vlm_process.stdin.flush()
    while True:
        out = vlm_process.stdout.readline()
        if out.startswith('encode_image_with_clip: image encoded in'):
            vlm_process.stdout.readline()
            break

    suspected = 0
    while True:
        if suspected == 0:
            out = vlm_process.stdout.read(3)
            yield out
            for i in range(3, 0, -1):
                if out[3 - i:] == '<ED>'[0:i]:
                    suspected = len('<ED>') - i
                    break
        else:  # 可能是EOS
            out = vlm_process.stdout.read(suspected)
            if out == '<ED>'[i:]:  # EOS
                yield out
                break

            else:  # 不是EOS，像往常一样判断
                if suspected < 3:
                    out += vlm_process.stdout.read(3 - suspected)
                yield out

                suspected = 0
                for i in range(3, 0, -1):
                    if out[3 - i:] == '<ED>'[0:i]:
                        suspected = len('<ED>') - i
                        break


def to_b64(fname):
    with open(fname, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image


def photography():
    test_code = os.environ['onsite_test']
    if test_code == '0':
        subprocess.run('termux-media-player play ./shutter.wav', shell=True, check=True)
        subprocess.run('termux-camera-photo -c 0 ./onsite_img.jpg', shell=True, check=True)
        img = Image.open('./onsite_img.jpg')
        img = ImageOps.exif_transpose(img)
        img = img.resize((360, 480))
        img.save('./photo.jpg')
        fname = './photo.jpg'
    elif test_code == '1':
        fname = './zl226.jpg'
    elif test_code == '2':
        fname = './zl330.jpg'
    elif test_code == '3':
        os.system('cp ../pipe.jpg ./onsite_img.jpg')
        fname = './onsite_img.jpg'
    elif test_code == '4':
        os.system('cp ../onsite_img.jpg ./onsite_img.jpg')
        fname = './onsite_img.jpg'

    yield to_b64(fname)
    prompt_img = 'You are an AI civil engineer with profound knowledge of various construction procedures and technologies. Please describe the image in 100 words.'

    for chunk in vlm(prompt_img, fname):
        yield chunk


def retrieve(fname):
    global working_dir
    folder = os.path.splitext(fname)[0]
    fname = fname if fname.endswith('.md') else fname + '.md'
    working_dir = f'./documents/{folder}'
    with open(f'./documents/{folder}/{fname}', 'r', encoding='utf-8') as f:
        content = f.read()
    content = 'Here is a markdown file you can refer to:\n' + content
    return content


def show_ref(cite, doc):
    doc = doc.rsplit('--------------------', 1)[0]
    doc_lst = doc.split('\n')
    dic = {}
    cite = list(dict.fromkeys(cite))
    for idx, item in enumerate(cite):
        dic[item] = []
        dic[item].append(f'[{idx + 1}]')
        img_path = f'{working_dir}/{item}.jpg'
        if os.path.exists(img_path):
            dic[item].append(to_b64(img_path))
        else:
            dic[item].append('')
        part = item.split('-')[1]
        step = item.split('-')[3]
        is_part = False
        is_step = False
        text_lst = []
        for line in doc_lst:
            if line.startswith(f'## Part {part}'):
                is_part = True
                continue
            if is_part and line.startswith(f'{step} '):
                is_step = True
                text_lst.append(line)
                continue
            if is_part and is_step:
                if not re.match(r'^\d+ |## Part \d+ ', line):
                    text_lst.append(line)
                else:
                    break

        dic[item].append(re.sub(r'!\[\]\(.+?\)\n', '', '\n'.join(text_lst)))
    return dic


if __name__ == '__main__':
    # photography()
    # print(retrieve('How to Build Spiral Stairs.md'))
    # print(working_dir)
    doc = retrieve('How to Build Spiral Stairs.md')
    ans = ['Part-3-Step-1']
    a = show_ref(ans, doc)
    pass
