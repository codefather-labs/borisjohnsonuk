import os
from collections.abc import Sequence
from io import TextIOWrapper
from typing import Optional, Union, List

from interfaces import AbstractNode, AbstractTag, AbstractArea, AbstractDoublyLinkedList
from fonts import FONT_MAP


class ContentNode(AbstractNode):
    def __init__(self, content_type: str, body: Union[str, dict]):
        self.content_type = content_type
        self.body: Union[str, dict] = body
        self.__prev: Optional[AbstractNode] = None
        self.__next: Optional[AbstractNode] = None

    def set_next_node(self, node: AbstractNode):
        self.__next = node

    def set_previous_node(self, node: AbstractNode):
        self.__prev = node

    @property
    def get_next_node(self): return self.__next

    @property
    def get_previous_node(self): return self.__prev


class DoublyLinkedList(AbstractDoublyLinkedList):
    def __init__(self, nodes: List[ContentNode]):
        self.nodes: List[ContentNode] = nodes

    @staticmethod
    def from_list(data: list):
        nodes = []
        for obj in data:
            obj_type = obj['type']
            content = obj['content']

            node = ContentNode(content_type=obj_type, body=content)

            if not nodes:
                nodes.append(node)
                continue

            nodes[-1].set_next_node(node)
            node.set_previous_node(nodes[-1])
            nodes.append(node)

        return DoublyLinkedList(nodes=nodes)

    def pop(self, index: int):
        return self.nodes.pop(index)

    def __getitem__(self, index: int) -> ContentNode:
        return self.nodes[index]

    def __len__(self) -> int:
        return len(self.nodes)


class Area(AbstractArea):
    def __init__(self, tag: AbstractTag, chunk: List[ContentNode] = None):
        self.chunk: List[ContentNode] = chunk if chunk else []
        self.tag: AbstractTag = tag

    def append_node(self, node: ContentNode):
        self.chunk.append(node)

    @staticmethod
    def collect_areas(content: DoublyLinkedList) -> List[AbstractArea]:
        last_area = None
        areas = []
        while content:
            node: ContentNode = content.pop(0)
            current_font_tag: AbstractTag = FONT_MAP[node.body.get('flags')]

            if node.content_type == 'image':
                # TODO image collecting
                continue

            if not last_area:
                last_area = Area(tag=current_font_tag)

            if last_area.tag == current_font_tag:
                last_area.append_node(node)

            elif last_area.tag != current_font_tag:
                areas.append(last_area)
                last_area = Area(tag=current_font_tag)

        else:
            areas.append(last_area)

        return areas

    def __len__(self) -> int:
        return len(self.chunk)

    def __getitem__(self, index: int):
        return self.chunk[index]


class FileDescriptor:
    def __init__(self, filepath: str = None, with_clearing: bool = False):
        self.file = filepath if filepath else 'result.md'

        if with_clearing:
            os.system(f'rm -rf {self.file}')

        if not os.path.exists(self.file):
            os.system(f'touch {self.file}')

        self.writer: Optional[TextIOWrapper] = None

    def write(self, data: str):
        self.writer = open(self.file, 'a')
        self.writer.write(data)
        self.writer.close()

    def __enter__(self):  # ???
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # ???
        return self
