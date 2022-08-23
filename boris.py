import os
import json
import shutil
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import List, Optional, Tuple

import fitz  # import the bindings
from fitz import Page
from fitz.utils import get_image_info

from utils import FileDescriptor, DoublyLinkedList, ContentNode
from processor import ContentProcessor
from fonts import flags_decomposer
from interfaces import PDFContentType
import fonts


class AbstractBoris(ABC):
    DEFAULT_PDF_PARSE_FLAGS = (
            fitz.TEXT_PRESERVE_LIGATURES |
            fitz.TEXT_PRESERVE_WHITESPACE |
            fitz.TEXT_PRESERVE_IMAGES |
            fitz.TEXT_MEDIABOX_CLIP |
            fitz.TEXT_DEHYPHENATE |
            fitz.TEXT_PRESERVE_SPANS |
            fitz.TEXT_MEDIABOX_CLIP
    )

    @abstractmethod
    def initial_boris(self): ...

    @abstractmethod
    def fetch_pages(self): ...

    @abstractmethod
    def handle_block(self, doc: fitz.Document, page: Page, block) -> List[str]: ...

    @abstractmethod
    def create_page(self, page: fitz.Page) -> str: ...

    @abstractmethod
    def get_image_from_bytes(self, image: bytes, filename: str, ext: str): ...

    @abstractmethod
    def formatted_image(self, image_path: str, description: str): ...

    @abstractmethod
    def save_page(self, page_number: int, page: str): ...

    @abstractmethod
    def get_image_by_block_number(self, page: Page, block_number: int): ...

    # FIXME Useless now
    # @abstractmethod
    # def save_result(self, result: List[Tuple[int, str]], filepath: str): ...


class MarkdownBoris(AbstractBoris):

    def __init__(self, source_path: str, output_dir_path: str):
        self.source_path = source_path
        self.output_dir_path = output_dir_path
        self.book_font_sizes = set()
        self.unknown_fonts_map_filepath = lambda: os.path.join(
            self.output_dir_path, 'unknown_fonts_map.json'
        )
        self.unknown_fonts_file_descriptor: Optional[FileDescriptor] = None
        self.doc: Optional[fitz.Document] = None
        self.images_path = os.path.join(self.output_dir_path, 'images')
        self.initial_boris()

    def initial_boris(self):
        try:
            self.doc: fitz.Document = fitz.open(self.source_path)  # open document
        except RuntimeError as e:
            exit(f'pdf_path param is invalid. unknown path {self.source_path}')

        if not os.path.isdir(self.output_dir_path):
            os.mkdir(self.output_dir_path)

        if not os.path.isdir(self.images_path):
            os.mkdir(self.images_path)

        self.unknown_fonts_file_descriptor = FileDescriptor(
            filepath=self.unknown_fonts_map_filepath(),
        )
        self.load_unknown_fonts()

    def fetch_pages(self):

        for page in self.doc:
            page_result = self.create_page(page)

            self.save_page(page.number, page_result)

            print(f"Page: {page.number} from {self.doc.page_count} done 👌")

            del page

        # FIXME Useless now
        # save_result(result, filepath=result_path)
        print(f"{self.output_dir_path.split('/')[-1]} converting success 👌")
        print(f"Result is there -> {self.output_dir_path}")

    def get_image_from_bytes(self, image: bytes, filename: str, ext: str):
        # filepath = f"pages/images/{filename}.{ext}"
        filepath = os.path.join(self.output_dir_path, f"images/{filename}.{ext}")
        img = open(filepath, "wb")
        img.write(image)
        img.close()
        return f"images/{filename}.{ext}"

    def formatted_image(self, image_path: str, description: str):
        return f"`\n![{description}]({image_path})\n`"

    def save_page(self, page_number: int, page: str):
        writer = FileDescriptor(
            filepath=f'{self.output_dir_path}/{page_number}.md',
        )
        writer.write(page)

    def save_result(self, r: List[Tuple[int, str]], filepath: str):
        for p, content in r:
            writer = FileDescriptor(filepath=f'{filepath}/{p}.md')
            writer.write(content)

    def get_image_by_block_number(self, page: Page, block_number: int):
        page_images: List[dict] = get_image_info(page, xrefs=True)
        for image in page_images:
            if image.get('number') == block_number:
                return image
        return None

    def load_unknown_fonts(self):
        if not os.path.exists(self.unknown_fonts_map_filepath()):
            return

        try:
            file = open(self.unknown_fonts_map_filepath(), 'r')
            data = list(json.loads(file.read()))
            file.close()
        except JSONDecodeError:
            exit(f'invalid {self.unknown_fonts_map_filepath()} file')

        for obj in data:
            obj: dict
            for k, v in obj.items():
                if not v:
                    print(f"Value: {v} on unknown font {k} is invalid. "
                          f"Skipping...")
                    continue

                try:
                    v = getattr(fonts, v)
                except AttributeError as e:
                    exit(f"Invalid font value {v} for {k}")

                if v not in fonts.AVAIlABLE_FONTS_FOR_MAPPING:
                    exit(f"Unknown font value {v} for {k}")

                if v not in fonts.FONT_MAP:
                    fonts.FONT_MAP.update({k: v})

    def handle_block(self, doc: fitz.Document, page: Page, block) -> List[str]:
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

                    image_path = self.get_image_from_bytes(
                        src_image['image'], image_name, src_image['ext']
                    )
                    image = {
                        "type": "image",
                        "content": self.formatted_image(image_path, image_name)
                    }
                    content.append(image)

            elif block_type == PDFContentType.TEXT:
                for line in block['lines']:
                    for span in line['spans']:
                        font = span['font']
                        font_flags = flags_decomposer(span['flags'])
                        font_size = int(span['size'])
                        text = span['text']

                        self.book_font_sizes.add(font_size)

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

        processor = ContentProcessor(content=cnt)

        result_content = processor.fetch_content()

        if processor.unknown_fonts:
            print('\n-------------')
            print(f"\nFound unknown fonts: {processor.unknown_fonts}")
            print(f"There are will be saved inside of "
                  f"{self.unknown_fonts_map_filepath()} path.\n")
            print(f"You need set all unknown fonts inside 'of {self.unknown_fonts_map_filepath()}'\n"
                  f"and try to restart program. \n"
                  f"They area will be loaded.\n")
            print('-------------\n')

            unknown_fonts = [{font: None} for font in processor.unknown_fonts]
            self.unknown_fonts_file_descriptor.write(json.dumps(unknown_fonts))

        return result_content

    def create_page(self, page: fitz.Page) -> str:
        page: fitz.Page

        blocks: dict = json.loads(
            page.get_displaylist().get_textpage(
                self.DEFAULT_PDF_PARSE_FLAGS).extractJSON()
        )

        markdown_dict: List[str] = self.handle_block(self.doc, page, blocks)
        markdown_string = " ".join(markdown_dict)
        return markdown_string
