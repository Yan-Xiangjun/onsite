import json
import os
from xml.sax.saxutils import escape
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
                    prev["raw_html"] = prev.get("raw_html", False) or block.get("raw_html", False)
                    continue
            merged_content.append(block)
        merged_pages.append({"page": page["page"], "content": merged_content, "size": page["size"]})
    return merged_pages


def pages_to_xml(blocks, xml_path):
    lines = []
    for block in blocks:
        content_lines = block["content"].splitlines()
        if len(content_lines) == 1:
            text = content_lines[0] if block.get("raw_html") else escape(content_lines[0])
            lines.append(f'<block idx="{block["block_idx"]}">{text}</block>')
        else:
            lines.append(f'<block idx="{block["block_idx"]}">')
            for line in content_lines:
                if block.get("raw_html"):
                    lines.append(f'  {line}')
                else:
                    lines.append(f'  {escape(line)}')
            lines.append("</block>")
        # lines.append("")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def simplify(json_path, xml_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data = data["pdf_info"]
    pages = []
    for page in data:
        content_items = []
        for block in page["para_blocks"]:
            bbox = block["bbox"]
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
                "content": text,
                "raw_html": block.get("type") == "table",
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
                "raw_html": block.get("raw_html", False),
            })
            bbox_records.append({
                "block_idx": block_idx,
                "page": page["page"],
                "page_size": page["size"],
                "bbox": block["bbox"],
            })
            block_idx += 1

    pages_to_xml(flat_blocks, xml_path)

    bbox_path = Path(xml_path).with_name("bbox.json")
    with open(bbox_path, "w", encoding="utf-8") as bf:
        json.dump(bbox_records, bf, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    from pathlib import Path
    json_file = Path(__file__).parent.name + ".json"
    simplify(str(json_file), str(Path(json_file).with_suffix(".xml")))
