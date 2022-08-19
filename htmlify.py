import os

import argparse
from typing import List

import fitz  # import the bindings


def create_md_page(page: fitz.Page):
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

    return page.get_displaylist().get_textpage(flags).extractHTML()


def save_result(result: List[str], filepath: str):
    for page, content in result:
        with open(f'{filepath}/{page}.html', 'w', encoding='utf-8') as f:
            f.write(content)
            f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("html_path")

    args = parser.parse_args()

    fname = os.path.abspath(args.html_path)  # get filename from command line
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

    result.append((18, create_md_page(doc[18])))

    # for page in doc:
    #     try:
    #         result.append((page.number, create_md_page(doc, page)))
    #         print(f"Page: {page.number} from {pages} done 👌")
    #     except Exception as e:
    #         print(e)
    #
    #     del page

    save_result(result, filepath=result_path)
    print(f"{fname.split('/')[1]} converting success 👌")
    print(f"Result is there -> {result_path}")
