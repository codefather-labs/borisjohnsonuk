import json
from copy import deepcopy, copy
from typing import Optional

from interfaces import AbstractTag
from utils import (
    FileDescriptor, DoublyLinkedList, ContentNode, Arena
)


class ContentProcessor:

    def __init__(self, content: DoublyLinkedList[ContentNode]):
        self.content: DoublyLinkedList[ContentNode] = content
        self.result = []

    @staticmethod
    def get_open_tag(current: AbstractTag, last: Optional[AbstractTag]):
        """
            Если последний шрифт пуст, в таком кейсе ничего дополнительно делать не нужно.
            Просто добавить новый текст с его тегом в префиксе
        """

        if not last:
            return current.open_tag

        if last != current:
            # кейс, при котором новый текст не является частью предыдущего тега
            # предыдущий тег нужно закрыть, а затем добавлять новый текст с его тегом
            return current.open_tag

        if last == current:
            # кейс, при котором новый текст является частью предыдущего тега
            # нужно добавить текст
            return ''

    @staticmethod
    def get_close_tag(current: AbstractTag, last: AbstractTag):
        """
            Если последний шрифт не пуст, это значит, что в result лежит текст ожидающий закрытия тега.
        """
        if current == last:
            return ''

        return last.close_tag if last else ''

    def process_image(self, node: ContentNode):
        return

    def fetch_content(self):
        """
            Я хочу получить такое поведение
            которое будет декларировать автоматическое добавление
            нужного тега к text используя данные о предыдущем шрифте.

            Нужен механизм, который позволит не добавлять к каждому слову свой тег
            по отдельности, а вместо этого будет распознавать чанки текста
            относящиеся к текущему тегу.
        """

        # TODO пример группировки по Arena ниже
        #   эта идея не тестировалась. воспринимать как псевдокод

        arenas = Arena.from_list(content=copy(self.content))
        # self.content = arenas ??? может так ?

        for arena in arenas:
            arena: Arena
            self.result.append(arena.render())

            # на этом этапе не понятно нужен ли код ниже в текущей реализации
            # поскольку у нас теперь есть Arena -
            # последовательность из DoublyLinkedList[ContentNode]...
            # по идее нам достаточно здесь просто
            # написать обработчик для arena (arena.render()), который бы рендерил текст
            # в зависимости от arena.tag
            # результат arena.render() кладем в self.result и возвращаем его...

            # Код ниже может помочь в форматировании чанков, но это не точно

            # arena.render()

            # for node in arena.nodes:
            #     node: ContentNode
            #
            #     print(arena, node)
            #
            #     if node.content_type == 'image':
            #         # TODO
            #         # self.process_image(node=node)
            #         continue
            #
            #     last_font_tag: Optional[AbstractTag] = \
            #         FONT_MAP[
            #             node.get_previous_node.body.get('flags')
            #         ] if node.get_previous_node else None
            #
            #     # я последовательно перебираю весь текст и
            #     # при несоответствии текущего шрифта с последним,
            #
            #     current_font_tag: AbstractTag = FONT_MAP[node.body.get('flags')]
            #     text: str = node.body.get('text')
            #
            #     if text.isspace():
            #         space_count = text.count(' ')
            #         if space_count == 1:
            #             self.result.append(' ')
            #
            #         elif space_count > 1:
            #             self.result.append(f"\n{' ' * space_count}")
            #
            #         continue
            #
            #     open_tag: Optional[str] = self.get_open_tag(
            #         current=current_font_tag,
            #         last=last_font_tag,
            #     )
            #
            #     close_tag: Optional[str] = self.get_close_tag(
            #         current=current_font_tag,
            #         last=last_font_tag,
            #     )
            #     result_string = text
            #
            #     if not isinstance(open_tag, NoneType):
            #         result_string = f"{open_tag}{result_string}"
            #
            #     if not isinstance(close_tag, NoneType):
            #         result_string = f"{result_string}{close_tag}"
            #
            #     # добавляю в result текущий текст c
            #     # его открытым и закрытым тегом
            #     # (их может не быть если текущий текст
            #     # не является открывающим или закрывающим свой тег)
            #
            #     self.result.append(result_string)

        return self.result


def load_content() -> list:
    file = open('content.json', 'r')
    data = file.read()
    file.close()
    return list(json.loads(data))


cnt: DoublyLinkedList[ContentNode] = \
    DoublyLinkedList.from_list(data=load_content())

processor = ContentProcessor(content=cnt)
result_content = processor.fetch_content()

writer = FileDescriptor(with_clearing=True)
writer.write(" ".join(result_content))
