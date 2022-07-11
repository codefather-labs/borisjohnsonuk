import os
import json

import sys, fitz  # import the bindings

from fitz import Page
from fitz.utils import get_image_info
from typing import List, Optional, Tuple

from libtypes import PDFContentType

fname = sys.argv[1]  # get filename from command line
dir_name = "".join(fname.split(".")[:-1]).replace("\\", "")
dir_name = dir_name.replace("'", "")
dir_name = dir_name.replace("(", "")
dir_name = dir_name.replace(")", "")
dir_name = dir_name.replace(' ', '_')
dir_name = f"pages/{''.join(dir_name.split('/')[1:])}"
doc: fitz.Document = fitz.open(fname)  # open document

if not os.path.isdir('pages'):
    os.mkdir('pages')

if not os.path.isdir('pages/images'):
    os.mkdir('pages/images')


def get_image_from_bytes(image: bytes, filename: str, ext: str):
    filepath = f"pages/images/{filename}.{ext}"
    img = open(filepath, "wb")
    img.write(image)
    img.close()
    return f"images/{filename}.{ext}"


def formatted_text(text: str, size: int, flags: str, font: str):
    if 'monospaced' in flags:
        return f"""
        %s \n""" % text

    if flags == 'serifed, proportional, bold':
        if size == 15:
            return "\n%s \n\n" % f"#{text}"

        if size == 12:
            return "\n%s \n\n" % f"##{text}"

    return text


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


def handle_block(page: Page, block) -> List[str]:
    result = []

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
                result.append(formatted_image(imagepath, image_name))

        elif block_type == PDFContentType.TEXT:
            for line in block['lines']:
                for span in line['spans']:
                    font = span['font']
                    font_flags = flags_decomposer(span['flags'])
                    font_size = int(span['size'])

                    result.append(
                        formatted_text(
                            span['text'],
                            font_size,
                            font_flags,
                            font
                        )
                    )
        else:
            exit(f"-----------UNKNOWN BLOCK TYPE------------\n\n"
                 f"{block}"
                 f"-----------------------------------------")
    return result


def create_md_page(page: fitz.Page, with_translating: bool = False):
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

    markdown_dict: List[str] = handle_block(page, blocks)
    markdown_string = " ".join(markdown_dict)
    if with_translating:
        markdown_string = translator.translate(markdown_string)
    return markdown_string


result = []
pages = doc.page_count

result_path = f'pages/'
if not os.path.isdir(result_path):
    os.mkdir(result_path)

for page in doc:
    try:
        result.append((page.number, create_md_page(page)))
        print(f"Page: {page.number} from {pages} done 👌")
    except Exception as e:
        print(e)

    del page

save_result(result, filepath=result_path)
print(f"{fname.split('/')[1]} converting success 👌")
print(f"Result is there -> {result_path}")
