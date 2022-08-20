import os
import json
import argparse
from typing import List, Optional, Tuple

import fitz  # import the bindings
from fitz import Page
from fitz.utils import get_image_info

from libtypes import PDFContentType

from utils import FileDescriptor

font_sizes = set()


def get_image_from_bytes(image: bytes, filename: str, ext: str):
    filepath = f"pages/images/{filename}.{ext}"
    img = open(filepath, "wb")
    img.write(image)
    img.close()
    return f"images/{filename}.{ext}"


def formatted_image(imagepath: str, description: str):
    return f"`\n![{description}]({imagepath})\n`"


def save_result(result: List[Tuple[int, str]], filepath: str):
    for page, content in result:
        with open(f'{filepath}/{page}.md', 'w', encoding='utf-8') as f:
            f.write(content)
            f.close()


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
                image = {
                    "type": "image",
                    "content": formatted_image(imagepath, image_name)
                }
                content.append(image)

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

    writer = FileDescriptor(filepath='processors/content.json', with_clearing=True)
    writer.write(json.dumps(content, indent=4))

    # tag_processor = ContentProcessor(content=content)
    # content = tag_processor.fetch_content()

    # return content


def create_md_page(doc: fitz.Document,
                   page: fitz.Page):
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
    # if translator:
    #     markdown_string = translator.translate(markdown_string)
    return markdown_string


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")

    args = parser.parse_args()

    fname = os.path.abspath(args.pdf_path)  # get filename from command line
    result_path = 'pages'
    try:
        doc: fitz.Document = fitz.open(os.path.abspath(fname))  # open document
    except RuntimeError as e:
        exit()

    if not os.path.isdir(result_path):
        os.mkdir(result_path)

    images_path = os.path.join(result_path, 'images')
    if not os.path.isdir(images_path):
        os.mkdir(images_path)

    result = []
    pages = doc.page_count

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
