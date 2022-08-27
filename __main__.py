import os
import argparse
from types import NoneType

from boris import Boris
from processor import ContentProcessor

import json
import os
import shutil
import time
from types import NoneType
from typing import List

from utils import FileDescriptor

config_map = {
    "source_pdf_path": 'source.pdf',
    "output_dir_path": 'result',
    "debug": False,
    "from_page": 0,
    "to_page": -1,
}


def get_config() -> dict:
    if not os.path.exists('config.json'):
        desc = FileDescriptor(filepath='config.json', write_key='w')
        desc.write(json.dumps(config_map, indent=4))
        exit('File "config.json" was created. It need yours check for continue')
    else:
        file = open('config.json', 'r')
        config = json.loads(file.read())
        file.close()
        return config


if __name__ == '__main__':
    config: dict = get_config()

    from_page = config['from_page']
    to_page = config['to_page']
    if isinstance(to_page, NoneType):
        to_page = 0

    pdf_absolute_path = os.path.abspath(config['source_pdf_path'])  # get filename from command line
    output_dir_path = os.path.abspath(config['output_dir_path'])

    if not os.path.exists(pdf_absolute_path):
        exit(f'File {pdf_absolute_path} was not found')

    from_page = config['from_page']
    to_page = config['to_page']

    boris = Boris(
        source_path=pdf_absolute_path,
        output_dir_path=output_dir_path,
        from_page=from_page,
        to_page=to_page
    )
    boris.fetch_pages()
