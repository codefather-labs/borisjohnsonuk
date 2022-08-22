import os
from collections.abc import Sequence
from io import TextIOWrapper
from typing import Optional, Union, List

from interfaces import AbstractTag, AbstractArena, AbstractDoublyLinkedList, BaseContentNode, AbstractNode
from fonts import FONT_MAP, FontTag, Image, FONT_SIZE_SIGNATURE_MAP, TITLE_SIZE_MIN, TITLE_SIZE_MAX, Code


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

    Arena is Data Structure
    Arena is DoublyLinkedList and DoublyLinkedList-Node at the same time (see internals of AbstractArena)
    Arena is a DoublyLinkedList which contains links on next and prev Arenas (encapsulated in AbstractArena)
    Arena is a DoublyLinkedList which contains link on DoublyLinkedList[ContentNode] (self.nodes)
    Arena contains Markdown Tag for DoublyLinkedList[ContentNode] (self.tag)

    """

    def __init__(self, tag: FontTag, nodes: AbstractDoublyLinkedList[AbstractNode] = None):
        self.nodes: AbstractDoublyLinkedList[AbstractNode] = nodes if nodes else DoublyLinkedList()
        self.tag: FontTag = tag
        self.body = []
        self.unknown_fonts = []

    def transform_text(self, text: Union[str, list], size: int = None):
        # Proceed only with spaces and font sizes.
        # Special tag processing going inside
        # FontTag.pre_processing and FontTag.pre_processing
        if isinstance(text, list):
            for index, element in enumerate(text):
                if str(element).isspace():
                    space_count = element.count(' ')
                    if space_count == 1:
                        del text[index]

                    elif space_count > 1:
                        text[index] = f"\n{' ' * space_count}"

        else:
            if str(text).isspace():
                space_count = text.count(' ')
                if space_count == 1:
                    text = text.replace(' ', '')
                elif space_count > 1:
                    text = text.replace(' ' * space_count, f"\n{' ' * space_count}")

        if size:

            if size > TITLE_SIZE_MAX:
                return f"#{text}\n"
            elif size < TITLE_SIZE_MIN:
                return text
            return f"{FONT_SIZE_SIGNATURE_MAP[size]}{text}\n"

        return text

    def prepare_body(self) -> list:
        if isinstance(self.tag, Image):
            self.body = [
                node.body for node in self.nodes[0:len(self.nodes):2]
            ]
            return self.transform_text(self.body)
        else:
            self.body = [
                self.transform_text(text=node.body['text'], size=node.body['size'])
                for node in self.nodes[0:len(self.nodes):2]
            ]
            return self.body

    def prepare_code(self):
        is_code_ready = all([bool('\n' not in code) for code in self.body])
        if is_code_ready and len(self.body) > 1:
            new_body = []

            max_index = len(self.body) - 1 if len(self.body) > 1 else 1

            current_index = 0
            left_neighbour_index = lambda: current_index - 1 if current_index > 1 else 0
            right_neighbour_index = lambda: current_index + 1 if current_index + 1 <= max_index else max_index

            while current_index < max_index:
                left_neighbour: str = self.body[left_neighbour_index()]
                current_element: str = self.body[current_index]
                right_neighbour: str = self.body[right_neighbour_index()]

                new_body.append(current_element)

                if left_neighbour != current_element:
                    rules = [
                        current_element != '',
                        right_neighbour != '',
                        right_neighbour.isalnum() or right_neighbour in ['{', ';'],
                    ]
                    if all(rules):
                        new_body.append('\n')

                current_index += 1
            else:
                new_body.append(self.body[-1])

            new_body_string = ' '.join(new_body)
            new_body_string = new_body_string.replace('  ', ' ')
            new_body_string = new_body_string.replace(' \n ', '\n')
            self.body = new_body_string.split(' ')

        return self.body

    def render(self) -> str:
        prepared = self.prepare_body()
        if type(self.tag) == Code:
            prepared = self.prepare_code()

        return self.tag.render(text=" ".join(prepared))

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

    def add_unknown_font(self, font: str):
        if font not in self.unknown_fonts:
            self.unknown_fonts.append(font)

    @staticmethod
    def from_list(content: DoublyLinkedList) -> DoublyLinkedList[AbstractArena]:
        last_arena = None
        arenas = DoublyLinkedList()

        for node in content:
            node: ContentNode
            current_font_tag: Optional[FontTag] = None

            if isinstance(node.body, dict):
                # text case
                if not node.body.get('flags') in FONT_MAP:
                    last_arena.add_unknown_font(node.body.get('flags'))

                    current_font_tag: FontTag = FONT_MAP['sans, proportional']()
                else:
                    current_font_tag: FontTag = FONT_MAP[node.body.get('flags')]()

            if isinstance(node.body, str):
                # image case
                current_font_tag: FontTag = FONT_MAP['image']()

            if not last_arena:
                last_arena = Arena(tag=current_font_tag)

            elif type(last_arena.tag) != type(current_font_tag):
                arenas.append(last_arena)
                last_arena = Arena(tag=current_font_tag)

            last_arena.append(node)

        else:
            if last_arena:
                arenas.append(last_arena)

        return arenas

    def pop(self, index: int) -> AbstractNode:
        pass

    def __len__(self) -> int:
        return len(self.nodes)


class FileDescriptor:
    def __init__(self,
                 filepath: str = None,
                 with_clearing: bool = False,
                 create_empty: bool = False):
        self.file = filepath if filepath else 'result.md'
        self.is_empty_file_created = False

        if with_clearing:
            os.system(f'rm -rf {self.file}')

        if create_empty:
            if not os.path.exists(self.file):
                os.system(f'touch {self.file}')

            self.is_empty_file_created = True

        self.writer: Optional[TextIOWrapper] = None

    def write(self, data: str):
        if not self.is_empty_file_created:
            os.system(f'touch {self.file}')
            self.is_empty_file_created = True

        self.writer = open(self.file, 'a')
        self.writer.write(data)
        self.writer.close()

    def __enter__(self):  # ???
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):  # ???
        return self
