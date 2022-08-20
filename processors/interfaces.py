from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum
from typing import List, Optional, Union


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
    def fetch_body(self) -> None: raise NotImplementedError
