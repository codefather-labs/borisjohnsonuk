import json
import os
from json import JSONDecodeError

from utils import (
    DoublyLinkedList, ContentNode, Arena
)
import fonts


class ContentProcessor:

    def __init__(self, content: DoublyLinkedList[ContentNode]):
        self.content: DoublyLinkedList[ContentNode] = content
        self.result = []
        self.unknown_fonts = []

    @staticmethod
    def load_unknown_fonts(filepath: str):
        if not os.path.exists(filepath):
            return

        try:
            file = open(filepath, 'r')
            data = list(json.loads(file.read()))
            file.close()
        except JSONDecodeError:
            exit(f'invalid {filepath} file')

        for obj in data:
            obj: dict
            for k, v in obj.items():
                if not v:
                    print(f"Value: {v} on unknown font {k} is invalid. "
                          f"Skipping...")
                    continue

                try:
                    v = getattr(fonts, v)
                except AttributeError as e:
                    exit(f"Invalid font value {v} for {k}")

                if v not in fonts.AVAIlABLE_FONTS_FOR_MAPPING:
                    exit(f"Unknown font value {v} for {k}")

                if v not in fonts.FONT_MAP:
                    fonts.FONT_MAP.update({k: v})

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
            if arena.unknown_fonts:
                self.unknown_fonts.append(*arena.unknown_fonts)
            self.result.append(arena.render())

        return self.result
