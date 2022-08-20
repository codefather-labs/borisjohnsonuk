import os
from collections.abc import Sequence
from io import TextIOWrapper
from typing import Optional, Union, List

from interfaces import AbstractTag, AbstractArena, AbstractDoublyLinkedList, BaseContentNode, AbstractNode
from fonts import FONT_MAP, FontTag


class ContentNode(BaseContentNode):
    def __init__(self, content_type: str, body: Union[str, dict]):
        self.content_type = content_type
        self.body: Union[str, dict] = body
        self.__prev: Optional[BaseContentNode] = None
        self.__next: Optional[BaseContentNode] = None

    def set_next_node(self, node: BaseContentNode):
        self.__next = node

    def set_previous_node(self, node: BaseContentNode):
        self.__prev = node

    @property
    def get_next_node(self): return self.__next

    @property
    def get_previous_node(self): return self.__prev


class DoublyLinkedList(AbstractDoublyLinkedList):
    def __init__(self, nodes: List[Union[ContentNode, AbstractNode]] = None):
        self.nodes: List[Union[ContentNode, AbstractNode]] = nodes if nodes else []

    def append(self, node: Union[ContentNode, AbstractNode]):
        if not self.nodes:
            self.nodes.append(node)
            return

        self.nodes[-1].set_next_node(node)
        node.set_previous_node(self.nodes[-1])
        self.nodes.append(node)

    @staticmethod
    def from_list(data: list):
        dll = DoublyLinkedList()
        for obj in data:
            obj_type = obj['type']
            content = obj['content']

            node = ContentNode(content_type=obj_type, body=content)

            dll.append(node)

        return dll

    def pop(self, index: int) -> Union[ContentNode, AbstractNode]:
        return self.nodes.pop(index)

    def __len__(self) -> int:
        return len(self.nodes)


class Arena(AbstractArena):
    """
    Inspired by PyArena lol xD (why not)

    Arena is DataStructure
    Arena is DoublyLinkedList and DoublyLinkedList-Node at the same time (see internals of AbstractArena)
    Arena is a DoublyLinkedList which contains next and prev Arenas (encapsulated in AbstractArena)
    Arena is a DoublyLinkedList which contains DoublyLinkedList[ContentNode] (self.nodes)
    Arena contains Markdown Tag for DoublyLinkedList[ContentNode] (self.tag)

    """

    def __init__(self, tag: FontTag, nodes: AbstractDoublyLinkedList[AbstractNode] = None):
        self.nodes: AbstractDoublyLinkedList[AbstractNode] = nodes if nodes else DoublyLinkedList()
        self.tag: FontTag = tag
        self.body = []

    @staticmethod
    def transform_text(text: list):
        for index, element in enumerate(text):

            if str(element).isspace():
                space_count = element.count(' ')
                if space_count == 1:
                    del text[index]
                    ...

                elif space_count > 1:
                    text[index] = f"\n{' ' * space_count}"

        return text

    def fetch_body(self) -> list:
        self.body = [node.body['text'] for node in self.nodes[0:len(self.nodes):2]]
        return self.transform_text(self.body)

    def render(self) -> str:
        return self.tag.render(text=" ".join(self.fetch_body()))

    def append(self, node: AbstractNode):
        self.nodes.append(node)

        if not self.nodes:
            self.nodes.append(node)
            return

        self.nodes[-1].set_next_node(node)
        node.set_previous_node(self.nodes[-1])
        self.nodes.append(node)

    def set_next_node(self, node: AbstractArena):
        self.__next = node

    def set_previous_node(self, node: AbstractArena):
        self.__prev = node

    @property
    def get_next_node(self):
        return self.__next

    @property
    def get_previous_node(self):
        return self.__prev

    @staticmethod
    def from_list(content: DoublyLinkedList) -> DoublyLinkedList[AbstractArena]:
        last_arena = None
        arenas = DoublyLinkedList()

        for node in content:
            node: ContentNode

            text: str = node.body.get('text')
            current_font_tag: FontTag = FONT_MAP[node.body.get('flags')]()

            if node.content_type == 'image':
                # TODO image collecting
                continue

            if not last_arena:
                last_arena = Arena(tag=current_font_tag)

            elif type(last_arena.tag) != type(current_font_tag):
                arenas.append(last_arena)
                last_arena = Arena(tag=current_font_tag)

            last_arena.append(node)

        else:
            if last_arena:
                arenas.append(last_arena)

        # for arena in arenas:
        #     arena: Arena
        #     print(f"{arena} Arena:")
        #     print(f"-------- {arena.render()}")

        # body = [node.body['text'] for node in arena.nodes]
        #
        # print(f"------ {arena.tag} {body} ")

        return arenas

    def pop(self, index: int) -> AbstractNode:
        pass

    def __len__(self) -> int:
        return len(self.nodes)


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
