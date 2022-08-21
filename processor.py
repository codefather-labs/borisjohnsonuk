from utils import (
    DoublyLinkedList, ContentNode, Arena
)


class ContentProcessor:
    
    def __init__(self, content: DoublyLinkedList[ContentNode]):
        self.content: DoublyLinkedList[ContentNode] = content
        self.result = []

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

        arenas = Arena.from_list(content=self.content)

        for arena in arenas:
            arena: Arena
            self.result.append(arena.render())

        return self.result
