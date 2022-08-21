import json
from typing import List, Dict

from utils import DoublyLinkedList, ContentNode, FileDescriptor
from processor import ContentProcessor


def get_content() -> List[Dict]:
    file = open('content.json', 'r')
    data = file.read()
    file.close()
    return json.loads(data)


cnt: DoublyLinkedList[ContentNode] = \
    DoublyLinkedList.from_list(data=get_content())
# [print(node.body) for node in cnt]

processor = ContentProcessor(content=cnt)
result_content = processor.fetch_content()

writer = FileDescriptor(with_clearing=True)
writer.write(" ".join(result_content))