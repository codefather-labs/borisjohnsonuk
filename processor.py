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
            self.result.append(arena.render())

        return self.result
