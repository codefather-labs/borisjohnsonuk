from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum
from typing import List, Optional, Union


class AbstractNode(ABC):
    content_type: str
    body: Union[str, dict]
    __prev: object
    __next: object

    @abstractmethod
    def set_next_node(self, node: object): raise NotImplementedError

    @abstractmethod
    def set_previous_node(self, node: object): raise NotImplementedError


class AbstractLinkedList(Sequence, ABC):
    nodes: List[AbstractNode]

    @staticmethod
    @abstractmethod
    def from_list(data: list) -> Sequence: raise NotImplementedError


class TagRenderFormat(Enum):
    LEFT_TAG_ONLY = '{self.open_tag}{" ".join(self.buf)}'
    RIGHT_TAG_ONLY = '{" ".join(self.buf)}{self.close_tag}'
    BOTH_TAGS = '{self.open_tag}{" ".join(self.buf)}{self.close_tag}'
    NO_TAGS = '{" ".join(self.buf)}'


class AbstractTag(ABC):
    buf: list
    open_tag: Optional[str]
    close_tag: Optional[str]
    render_format: TagRenderFormat

    def render(self) -> str:
        return f"{self.render_format.value}"

    def __str__(self):
        return self.render()


class AbstractArea(ABC, Sequence):
    chunk: List[AbstractNode]
    tag: AbstractTag

    @abstractmethod
    def append_node(self, node: AbstractNode): ...

    @staticmethod
    @abstractmethod
    def collect_areas(content: AbstractLinkedList): ...
