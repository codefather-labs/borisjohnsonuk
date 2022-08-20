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

    def transform_text(self, text: Union[str, list], size: int = None):
        # Proceed only with spaces and font sizes.
        # Special tag processing going inside
        # FontTag.pre_processing and FontTag.pre_processing
        if isinstance(text, list):
            for index, element in enumerate(text):
                if str(element).isspace():
                    space_count = element.count(' ')
                    if space_count == 1:
                        # FIXME CHANGES
                        del text[index]
                        ...

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
                return f"#{text}"
            elif size < TITLE_SIZE_MIN:
                return text
            return f"{FONT_SIZE_SIGNATURE_MAP[size]}{text}"

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
        if is_code_ready:
            print(self.body)
            # TODO transform this: `j = 0 i = j k = 12.0 j = 2 * k assert i != j`
            #   to this:
            #   ```
            #   j = 0
            #   i = j
            #   k = 12.0
            #   j = 2 * k
            #   assert i != j
            #   ```
            #
            # last out:
            #   [
            #       'j', '', '=', '', '0',
            #       'i', '', '=', '', 'j',
            #       'k', '', '=', '', '12.0',
            #       'j', '', '=', '', '2', '', '*', '', 'k',
            #       'assert', '', 'i', '', '!=', '', 'j'
            #   ]
            # TODO find elements pattern in self.body
            #   where are two neighbours like - '0', 'i'; 'j', 'k'; '12.0', 'j';
            #   both are not a space symbols.
            #   only at this case, can be '\n' between them both!
            ...

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

    @staticmethod
    def from_list(content: DoublyLinkedList) -> DoublyLinkedList[AbstractArena]:
        last_arena = None
        arenas = DoublyLinkedList()

        for node in content:
            node: ContentNode
            current_font_tag: Optional[FontTag] = None

            if isinstance(node.body, dict):
                # text case
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