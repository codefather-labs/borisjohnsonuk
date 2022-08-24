from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum, IntEnum
from typing import List, Optional, Union

import fitz
from fitz import Page


class PDFContentType(IntEnum):
    TEXT = 0
    IMAGE = 1


class AbstractNode(ABC):
    body: Union[str, dict]
    __prev: object
    __next: object

    @abstractmethod
    def set_next_node(self, node: object): raise NotImplementedError

    @abstractmethod
    def set_previous_node(self, node: object): raise NotImplementedError


class BaseContentNode(AbstractNode):
    content_type: str
    body: Union[str, dict]
    __prev: object
    __next: object

    @abstractmethod
    def set_next_node(self, node: object): raise NotImplementedError

    @abstractmethod
    def set_previous_node(self, node: object): raise NotImplementedError


class AbstractDoublyLinkedList(Sequence, ABC):
    nodes: List[AbstractNode]

    @staticmethod
    @abstractmethod
    def from_list(data: list): raise NotImplementedError

    @abstractmethod
    def append(self, data: AbstractNode): raise NotImplementedError

    @abstractmethod
    def pop(self, index: int) -> AbstractNode: raise NotImplementedError

    def __getitem__(self, index: int) -> AbstractNode:
        return self.nodes[index]


class AbstractProcessor(ABC):
    content: AbstractDoublyLinkedList[AbstractNode]
    result: List
    unknown_fonts: List

    @staticmethod
    @abstractmethod
    def pre_processor(text: str) -> str: ...

    @staticmethod
    @abstractmethod
    def post_processor(text: str) -> str: ...

    @abstractmethod
    def fetch_content(self): ...


class TagRenderFormat(Enum):
    LEFT_TAG_ONLY = 1
    RIGHT_TAG_ONLY = 2
    BOTH_TAGS = 3
    NO_TAGS = 4


class AbstractTag(ABC):
    buf: list
    open_tag: Optional[str]
    close_tag: Optional[str]
    render_format: TagRenderFormat

    @abstractmethod
    def render(self, text: str) -> str: ...

    @abstractmethod
    def pre_processing(self, text: str) -> str: ...

    @abstractmethod
    def post_processing(self, rendered_string: str) -> str: ...


class AbstractArena(AbstractDoublyLinkedList, AbstractNode):
    nodes: AbstractDoublyLinkedList[AbstractNode]
    tag: AbstractTag
    body: list

    @abstractmethod
    def append(self, node: AbstractNode): ...

    @staticmethod
    @abstractmethod
    def from_list(content: AbstractDoublyLinkedList): raise NotImplementedError

    @abstractmethod
    def render(self) -> str: raise NotImplementedError

    @abstractmethod
    def prepare_body(self) -> None: raise NotImplementedError


class AbstractPDFBackend(ABC):
    from_page: int
    to_page: int
    source_path: str
    output_dir_path: str
    processor: AbstractProcessor

    @abstractmethod
    def fetch_pages(self): ...

    @abstractmethod
    def handle_block(self, doc, page, block) -> List[str]: ...

    @abstractmethod
    def get_image(self, image: bytes, filename: str, ext: str): ...

    @abstractmethod
    def formatted_image(self, image_path: str, description: str): ...

    @abstractmethod
    def load_unknown_fonts(self): ...

    @abstractmethod
    def create_page(self, page) -> str: ...

    @abstractmethod
    def save_page(self, page_number: int, page: str): ...


class AbstractBoris(ABC):

    @abstractmethod
    def initial_boris(self): ...
