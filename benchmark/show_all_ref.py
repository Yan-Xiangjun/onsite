import json
from pathlib import Path
from PIL import Image, ImageDraw
import shutil

shutil.rmtree('./all_ref', ignore_errors=True)
Path('./all_ref').mkdir(parents=True, exist_ok=True)

# folder = 'Harbin_Project_1'
folder = 'Building_Construction_Handbook'
with open(f'../documents/{folder}/bbox.json', 'r', encoding='utf-8') as f:
    bbox_records = json.load(f)
idx_lst = list(range(1, len(bbox_records) + 1))
for idx in idx_lst:
    for item in bbox_records:
        if item['block_idx'] == idx:
            break
    page = item['page']
    bbox = item['bbox']
    w, h = item['page_size']
    img_path = f'../documents/{folder}/{page}.jpg'
    img = Image.open(img_path)
    left, top, right, bottom = bbox
    # 先把原图resize成w和h，再在原图上画出bbox（画矩形）
    img = img.resize((w, h))
    draw = ImageDraw.Draw(img)
    draw.rectangle([left, top, right, bottom], outline='red', width=5)
    img = img.resize((int(0.7 * w), int(0.7 * h)))
    img.save(f'./all_ref/{idx}.jpg')
