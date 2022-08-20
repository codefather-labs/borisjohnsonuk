import os
import json
import argparse
from typing import List, Optional, Tuple

import fitz  # import the bindings
from fitz import Page
from fitz.utils import get_image_info

from utils import FileDescriptor, DoublyLinkedList, ContentNode
from processor import ContentProcessor
from fonts import flags_decomposer, FONT_MAP
from interfaces import PDFContentType

book_font_sizes = set()
unknown_font_flags = set()


def get_image_from_bytes(image: bytes, filename: str, ext: str):
    filepath = f"pages/images/{filename}.{ext}"
    img = open(filepath, "wb")
    img.write(image)
    img.close()
    return f"images/{filename}.{ext}"


def formatted_image(imagepath: str, description: str):
    return f"`\n![{description}]({imagepath})\n`"


def save_result(r: List[Tuple[int, str]], filepath: str):
    for p, content in r:
        writer = FileDescriptor(filepath=f'{filepath}/{p}.md', with_clearing=True)
        writer.write(content)


def get_image_by_block_number(page: Page, block_number: int):
    page_images: List[dict] = get_image_info(page, xrefs=True)
    for image in page_images:
        if image.get('number') == block_number:
            return image
    return None


def handle_block(doc: fitz.Document, page: Page, block) -> List[str]:
    content = []

    page_images: List[dict] = list(get_image_info(page, xrefs=True))

    for block in block['blocks']:
        block_number = block['number']
        block_type = block['type']

        if block_type == PDFContentType.IMAGE:
            image_name = f"page_{page.number}_{block_number}"
            image = page_images.pop(0)

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

                    book_font_sizes.add(font_size)
                    if font_flags not in FONT_MAP:
                        unknown_font_flags.add(font_flags)

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

    # writer = FileDescriptor(filepath='content.json', with_clearing=True)
    # writer.write(json.dumps(content, indent=4))

    cnt: DoublyLinkedList[ContentNode] = \
        DoublyLinkedList.from_list(data=content)
    # [print(node.body) for node in cnt]

    processor = ContentProcessor(content=cnt)
    result_content = processor.fetch_content()

    return result_content


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

    blocks: dict = json.loads(
        page.get_displaylist().get_textpage(flags).extractJSON()
    )

    markdown_dict: List[str] = handle_block(doc, page, blocks)
    markdown_string = " ".join(markdown_dict)
    return markdown_string


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")

    args = parser.parse_args()

    pdf_absolute_path = os.path.abspath(args.pdf_path)  # get filename from command line
    result_path = os.path.abspath('pages')
    try:
        doc: fitz.Document = fitz.open(pdf_absolute_path)  # open document
    except RuntimeError as e:
        exit(f'pdf_path param is invalid. unknown path {pdf_absolute_path}')

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
        result.append((page.number, create_md_page(doc, page)))
        print(f"Page: {page.number} from {pages} done 👌")

        del page

    save_result(result, filepath=result_path)
    print(f"Unknown Fonts found: {unknown_font_flags}") if unknown_font_flags else None
    print(f"{pdf_absolute_path.split('/')[-1]} converting success 👌")
    print(f"Result is there -> {result_path}")
