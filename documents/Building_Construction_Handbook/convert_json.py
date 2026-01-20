import json
import os
import re
from pathlib import Path


def join_lines(lines):
    return "".join("".join(span["content"] for span in ln["spans"]) for ln in lines)


def merge_blocks(pages, left_tol=50, gap_tol=20):
    merged_pages = []
    for page in pages:
        merged_content = []
        for block in page["content"]:
            if merged_content:
                prev = merged_content[-1]
                x0, y0, x1, y1 = list(prev["bbox"])
                nx0, ny0, nx1, ny1 = list(block["bbox"])
                left_aligned = abs(nx0 - x0) <= left_tol
                vertical_gap = ny0 - y1
                small_gap = vertical_gap <= gap_tol
                if left_aligned and small_gap:
                    prev["content"] = f"{prev['content']}\n{block['content']}"
                    prev["bbox"] = [min(x0, nx0), min(y0, ny0), max(x1, nx1), max(y1, ny1)]
                    continue
            merged_content.append(block)
        merged_pages.append({"page": page["page"], "content": merged_content, "size": page["size"]})
    return merged_pages


def clean_latex(text):
    if not text:
        return text
    # 处理嵌套的 \mathrm{...} 和 \underline{...}
    while r'\mathrm{' in text:
        text = re.sub(r'\\mathrm\{([^}]*)\}', r'\1', text)
    while r'\underline{' in text:
        text = re.sub(r'\\underline\{([^}]*)\}', r'\1', text)

    # 符号转换
    text = text.replace(r'^{\circ}', '°').replace(r'\circ', '°')
    text = text.replace(r'\sim', '~').replace(r'\%', '%')
    text = text.replace(r'\alpha', 'α').replace(r'\rightarrow', '→')

    # 下标 _{...} -> ... (直接并列)
    while '_{' in text:
        text = re.sub(r'_\{([^}]*)\}', r'\1', text)
    # 上标 ^{...} -> ^...
    while '^{' in text:
        text = re.sub(r'\^\{([^}]*)\}', r'^\1', text)

    # 清除剩余的 \mathrm (如 \mathrm mm)
    text = re.sub(r'\\mathrm\s*', '', text)
    text = text.replace('°C', '℃').replace('~ ', '~').replace(' ~', '~')
    return text


def pages_to_md(blocks, md_path):
    lines = []
    for block in blocks:
        lines.append(f'# Block {block["block_idx"]}')
        lines.append(block["content"])
        # lines.append("")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def simplify(json_path, md_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data = data["pdf_info"]
    pages = []
    for page in data:
        content_items = []
        for block in page["para_blocks"]:
            bbox = block["bbox"]
            text = ""
            if block['type'] in ['text', 'title']:
                text = join_lines(block["lines"])
            elif block['type'] == 'list':
                parts = []
                for sub in block["blocks"]:
                    part = join_lines(sub["lines"])
                    parts.append(part)
                text = "\n".join(parts)
            elif block['type'] == 'table':
                parts = []
                sub_bboxes = []
                for sub in block["blocks"]:
                    sub_bboxes.append(sub["bbox"])
                    if sub['type'] != 'table_body':
                        part = join_lines(sub["lines"])
                        parts.append(part)
                    else:
                        parts.append(sub['lines'][0]['spans'][0]['html'])
                text = "\n".join(parts)
                if sub_bboxes:
                    bbox = [
                        min(b[0] for b in sub_bboxes),
                        min(b[1] for b in sub_bboxes),
                        max(b[2] for b in sub_bboxes),
                        max(b[3] for b in sub_bboxes)
                    ]
            elif block['type'] == 'image':
                parts = []
                sub_bboxes = []
                for sub in block["blocks"]:
                    sub_bboxes.append(sub["bbox"])
                    if sub['type'] != 'image_body':
                        part = join_lines(sub["lines"])
                        parts.append(part)
                    else:
                        parts.append('[图片]')
                text = "\n".join(parts)
                if sub_bboxes:
                    bbox = [
                        min(b[0] for b in sub_bboxes),
                        min(b[1] for b in sub_bboxes),
                        max(b[2] for b in sub_bboxes),
                        max(b[3] for b in sub_bboxes)
                    ]

            content_items.append({
                "bbox": bbox,
                "content": clean_latex(text),
            })
        pages.append({
            "page": page["page_idx"] + 1,
            "content": content_items,
            "size": page["page_size"],
        })

    pages = merge_blocks(pages)

    flat_blocks = []
    bbox_records = []
    block_idx = 1
    for page in pages:
        for block in page["content"]:
            flat_blocks.append({
                "block_idx": block_idx,
                "content": block["content"],
            })
            bbox_records.append({
                "block_idx": block_idx,
                "page": page["page"],
                "page_size": page["size"],
                "bbox": block["bbox"],
            })
            block_idx += 1

    pages_to_md(flat_blocks, md_path)

    bbox_path = Path(md_path).with_name("bbox.json")
    with open(bbox_path, "w", encoding="utf-8") as bf:
        json.dump(bbox_records, bf, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    from pathlib import Path
    json_file = Path(__file__).parent.name + ".json"
    simplify(str(json_file), str(Path(json_file).with_suffix(".md")))
