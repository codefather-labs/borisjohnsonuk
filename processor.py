from typing import Generator, List

from borisjohnsonuk.interfaces import AbstractProcessor
from borisjohnsonuk.utils import (
    DoublyLinkedList, ContentNode, Arena
)


class ContentProcessor(AbstractProcessor):

    def __init__(self, content: DoublyLinkedList[ContentNode]):
        self.content: DoublyLinkedList[ContentNode] = content
        self.result = []
        self.unknown_fonts = []

    @staticmethod
    def pre_processor(text: str):
        return text

    @staticmethod
    def post_processor(text: List[str]):
        return text

    def fetch_content(self):
        """
            I want to get a behavior
            that will declare the automatic addition
            the desired tag to text using the data about the previous font.

            What I need is a mechanism that won't add a different tag to each word
            tag individually, but instead recognize text chunks
            related to the current tag.
        """

        arenas = Arena.from_list(content=self.content)

        for arena in arenas:
            arena: Arena
            if arena.unknown_fonts:
                self.unknown_fonts.append(*arena.unknown_fonts)

            render_generator: Generator = arena.render()
            is_code, prepared = next(render_generator)

            pre_proceed = self.pre_processor(prepared)
            proceed = render_generator.send(pre_proceed)

            self.result.append(proceed)

        return self.post_processor(self.result)
