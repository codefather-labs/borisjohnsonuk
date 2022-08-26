import os

from typing import Optional

import fitz  # import the bindings

from borisjohnsonuk.utils import FileDescriptor, DoublyLinkedList, ContentNode
from borisjohnsonuk.processor import ContentProcessor
from borisjohnsonuk.fonts import flags_decomposer
from borisjohnsonuk.interfaces import (
    PDFContentType, AbstractBoris, AbstractPDFBackend, AbstractProcessor
)
from borisjohnsonuk import fonts
from borisjohnsonuk.backends import MuPDFBackend


class Boris(AbstractBoris, MuPDFBackend):

    def __init__(self,
                 source_path: str,
                 output_dir_path: str,
                 from_page: int = 0,
                 to_page: int = 0):
        self.source_path = source_path
        self.output_dir_path = output_dir_path
        self.from_page: int = int(from_page)
        # self.to_page: int = int(to_page)

        self.book_font_sizes = set()
        self.unknown_fonts_map_filepath = lambda: os.path.join(
            self.output_dir_path, 'unknown_fonts_map.json'
        )
        self.unknown_fonts_file_descriptor: Optional[FileDescriptor] = None
        self.doc: Optional[fitz.Document] = None
        self.images_path = os.path.join(self.output_dir_path, 'images')
        self.initial_boris()

        self.processor: Optional[ContentProcessor] = ContentProcessor

    def initial_boris(self):

        try:
            self.doc: fitz.Document = fitz.open(self.source_path)  # open document
        except RuntimeError as e:
            exit(f'pdf_path param is invalid. unknown path {self.source_path}')

        # if not self.to_page:
        #     self.to_page = int(self.doc.page_count)

        if not os.path.isdir(self.output_dir_path):
            os.mkdir(self.output_dir_path)

        if not os.path.isdir(self.images_path):
            os.mkdir(self.images_path)

        self.unknown_fonts_file_descriptor = FileDescriptor(
            filepath=self.unknown_fonts_map_filepath(), write_key='a'
        )
        self.load_unknown_fonts()
