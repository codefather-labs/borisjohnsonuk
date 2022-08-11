import os
import json
import argparse

import sys, fitz  # import the bindings
from copy import deepcopy

from fitz import Page
from fitz.utils import get_image_info
from typing import List, Optional, Tuple

from libtypes import PDFContentType

font_sizes = set()


def get_image_from_bytes(image: bytes, filename: str, ext: str):
    filepath = f"pages/images/{filename}.{ext}"
    img = open(filepath, "wb")
    img.write(image)
    img.close()
    return f"images/{filename}.{ext}"


def formatted_image(imagepath: str, description: str):
    return f"\n![{description}]({imagepath})\n"


# https://pymupdf.readthedocs.io/en/latest/faq.html
# https://pymupdf.readthedocs.io/en/latest/vars.html#textpreserve

def save_block_file(data: dict):
    with open('data.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(data['blocks'][:-5]))


def save_result(result: List[Tuple[int, str]], filepath: str):
    for page, content in result:
        with open(f'{filepath}/{page}.md', 'w', encoding='utf-8') as f:
            f.write(content)
            f.close()


def save_html_file(string: str, filepath: str):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(string)


def flags_decomposer(flags):
    """Make font flags human readable."""
    l = []
    if flags & 2 ** 0:
        l.append("superscript")
    if flags & 2 ** 1:
        l.append("italic")
    if flags & 2 ** 2:
        l.append("serifed")
    else:
        l.append("sans")
    if flags & 2 ** 3:
        l.append("monospaced")
    else:
        l.append("proportional")
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)


def get_image_by_block_number(page: Page, block_number: int):
    page_images: List[dict] = get_image_info(page, xrefs=True)
    for image in page_images:
        if image.get('number') == block_number:
            return image
    return None


def prepare_buf_for_return(buf: List = None):
    buf = deepcopy(buf)
    return buf


def fetch_result_content(content: list):
    result = []
    last_font_flags = None
    text_buf = []
    text_buf_is_ready_for_return = False

    def text_process(text: str, font_flags: str, font_size: int):
        nonlocal last_font_flags
        nonlocal text_buf
        nonlocal text_buf_is_ready_for_return

        title_signature_map = {
            31: "#",
            28: "#",
            25: "###",
            18: "###",
            17: "###",
            16: "####",
            15: "####",
            14: "######",
            12: "######",
        }
        title = title_signature_map.get(font_size)
        is_title_text = bool(title)
        if is_title_text:
            return f"{title} {text}\n"

        # степень "^" X^2^
        # основание "~" H~2~O
        tags_signature_map = {
            "serifed": "",
            "italic": "*",
            "bold": "**",
            "monospaced": "`",
            "code": "```",  # CUSTOM
            "blockquote": ">",
            "strikethrough": "~~",
            "highlight": "==",
            "superscript": "^"
        }
        is_tag = lambda x: True if x in tags_signature_map.values() else False

        font_tags_map = {
            "serifed, proportional": tags_signature_map["serifed"],
            "serifed, proportional, bold": tags_signature_map["bold"],
            "italic, serifed, proportional": tags_signature_map["italic"],
            "italic, serifed, proportional, bold": tags_signature_map["bold"],
            "serifed, monospaced": tags_signature_map["monospaced"],
            "italic, serifed, monospaced": tags_signature_map["monospaced"],
            "serifed, monospaced, bold": tags_signature_map["monospaced"],
            "italic, serifed, monospaced, bold": tags_signature_map["monospaced"],
            "superscript, serifed, proportional": tags_signature_map["superscript"]
        }

        last_tag = lambda: font_tags_map[last_font_flags] if last_font_flags else None
        input_tag = lambda: font_tags_map[font_flags]

        # FIXME MONOSPACED
        # if 'monospaced' in font_flags:
        #     if not text_buf:
        #         text_buf.append(input_tag())
        #
        #     text_buf.append(text)
        #
        #     return None
        #
        # if not 'monospaced' in font_flags and text_buf:
        #     text_buf.append(last_tag())
        #     result_buf = text_buf
        #
        #     text_buf.clear()
        #     assert text_buf != result_buf
        #
        #     text = f'{" ".join(result_buf)}\n {text}'

        closed_text_buf = text

        return f"{input_tag()}{closed_text_buf}{input_tag()}"

    for c in content:
        t = c['type']
        cnt = c['content']

        if t == 'image':
            result.append(cnt)

        elif t == 'text':
            text_result = text_process(
                text=cnt['text'],
                font_flags=cnt['flags'],
                font_size=cnt['size']
            )

            if text_result:
                result.append(
                    text_result
                )

    return result


def handle_block(doc: fitz.Document, page: Page, block) -> List[str]:
    content = []

    for block in block['blocks']:
        block_number = block['number']
        block_type = block['type']

        if block_type == PDFContentType.IMAGE:
            image_name = f"page_{page.number}_{block_number}"
            image: Optional[dict] = \
                get_image_by_block_number(page, block_number)

            if image:
                src_image: dict = doc.extract_image(image['xref'])

                imagepath = get_image_from_bytes(
                    src_image['image'], image_name, src_image['ext']
                )
                content.append({
                    "type": "image",
                    "content": formatted_image(imagepath, image_name)
                })

        elif block_type == PDFContentType.TEXT:
            for line in block['lines']:
                for span in line['spans']:
                    font = span['font']
                    font_flags = flags_decomposer(span['flags'])
                    font_size = int(span['size'])
                    text = span['text']

                    font_sizes.add(font_size)

                    content.append({
                        "type": "text",
                        "content": {
                            "text": text,
                            "size": font_size,
                            "flags": font_flags,
                            "font": font,
                        }
                    })
        else:
            exit(f"-----------UNKNOWN BLOCK TYPE------------\n\n"
                 f"{block}"
                 f"-----------------------------------------")

    return fetch_result_content(content)


def create_md_page(doc: fitz.Document, page: fitz.Page, with_translating: bool = False):
    page: fitz.Page

    flags = (
            fitz.TEXT_PRESERVE_LIGATURES |
            fitz.TEXT_PRESERVE_WHITESPACE |
            fitz.TEXT_PRESERVE_IMAGES |
            fitz.TEXT_MEDIABOX_CLIP |
            fitz.TEXT_DEHYPHENATE |
            fitz.TEXT_PRESERVE_SPANS |
            fitz.TEXT_MEDIABOX_CLIP
    )

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!
    # https://github.com/pymupdf/PyMuPDF/blob/master/fitz/utils.py#L472 !!!!!!!!!!!!!!!!!
    blocks: dict = json.loads(page.get_displaylist().get_textpage(flags).extractJSON())

    markdown_dict: List[str] = handle_block(doc, page, blocks)
    markdown_string = " ".join(markdown_dict)
    # if with_translating:
    #     markdown_string = translator.translate(markdown_string)
    return markdown_string


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")

    args = parser.parse_args()

    fname = os.path.abspath(args.pdf_path)  # get filename from command line
    dir_name = "".join(fname.split(".")[:-1]).replace("\\", "")
    dir_name = dir_name.replace("'", "")
    dir_name = dir_name.replace("(", "")
    dir_name = dir_name.replace(")", "")
    dir_name = dir_name.replace(' ', '_')
    dir_name = f"pages/{''.join(dir_name.split('/')[1:])}"
    try:
        doc: fitz.Document = fitz.open(os.path.abspath(fname))  # open document
    except RuntimeError as e:
        exit()

    if not os.path.isdir('pages'):
        os.mkdir('pages')

    if not os.path.isdir('pages/images'):
        os.mkdir('pages/images')

    result = []
    pages = doc.page_count

    result_path = f'pages/'
    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    for page in doc:
        try:
            result.append((page.number, create_md_page(doc, page)))
            print(f"Page: {page.number} from {pages} done 👌")
        except Exception as e:
            print(e)

        del page

    save_result(result, filepath=result_path)
    print(f"{fname.split('/')[1]} converting success 👌")
    print(f"Result is there -> {result_path}")
