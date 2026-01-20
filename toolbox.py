import subprocess
from PIL import Image, ImageOps, ImageDraw
import re
import base64
import json
import sys
import requests
import io
import threading


def parse_page_size(xml_path, idx):
    with open(xml_path, "r", encoding="utf-8") as f:
        content = f.read()
    lst = content.splitlines()
    for line in lst:
        if line.strip().startswith('<page '):
            page_idx_match = re.search(r'page_idx="(\d+)"', line)
            if page_idx_match and int(page_idx_match[1]) == idx:
                size_attr = re.search(r'page_size="(.+)"', line).group(1)
                break

    width, height = eval(size_attr)
    return width, height


def to_b64(input_data):
    if isinstance(input_data, str):
        with open(input_data, 'rb') as image_file:
            content = image_file.read()
    else:
        buffered = io.BytesIO()
        input_data.save(buffered, format="JPEG")
        content = buffered.getvalue()
    return base64.b64encode(content).decode('utf-8')


def photography(fname='./onsite_img.jpg'):
    if sys.platform != 'win32':
        threading.Thread(
            target=subprocess.run,
            args=('termux-media-player play ./shutter.wav', ),
            kwargs={
                'shell': True,
                'check': True
            },
        ).start()
        subprocess.run('termux-camera-photo -c 0 ./onsite_img.jpg', shell=True, check=True)

    with Image.open(fname) as img:
        img = ImageOps.exif_transpose(img)
        w, h = img.size
        if max(w, h) != 480:
            scale = 480 / max(w, h)
            img.resize(
                (int(w * scale), int(h * scale)),
                Image.Resampling.LANCZOS,
            ).save(fname)

    return to_b64(fname)


def retrieve(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        file_content = f.read()
    return file_content


def show_ref(folder, idx):
    with open(f'./documents/{folder}/bbox.json', 'r', encoding='utf-8') as f:
        bbox_records = json.load(f)
    out = []
    for item in bbox_records:
        if item['block_idx'] == idx:
            break
    page = item['page']
    bbox = item['bbox']
    w, h = item['page_size']
    img_path = f'./documents/{folder}/{page}.jpg'
    img = Image.open(img_path)
    left, top, right, bottom = bbox
    # 先把原图resize成w和h，再在原图上画出bbox（画矩形）
    img = img.resize((w, h))
    draw = ImageDraw.Draw(img)
    draw.rectangle([left, top, right, bottom], outline='red', width=5)
    img = img.resize((int(0.7 * w), int(0.7 * h)))
    # 转成base64返回
    out.append(to_b64(img))
    return out


if __name__ == '__main__':
    show_ref('Harbin_Project_1', 39)
    pass
