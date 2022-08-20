import os
import json

import sys, fitz  # import the bindings

from fitz import Page
from fitz.utils import get_image_info
from typing import List, Optional, Tuple

from processors.libtypes import PDFContentType

fname = sys.argv[1]  # get filename from command line
step = int(sys.argv[2])  # get filename from command line
dir_name = "".join(fname.split(".")[:-1]).replace("\\", "")
dir_name = dir_name.replace("'", "")
dir_name = dir_name.replace("(", "")
dir_name = dir_name.replace(")", "")
dir_name = dir_name.replace(' ', '_')
dir_name = f"separated/{''.join(dir_name.split('/')[1:])}"
doc: fitz.Document = fitz.open(fname)  # open document
width, height = fitz.paper_size("a4")

if not os.path.isdir('separated'):
    os.mkdir('separated')

start = 0
stop = doc.page_count
step = step


def create_doc(src: fitz.Document, from_page: int, to_page: int):
    result_doc: fitz.Document = fitz.open()
    result_doc.insert_pdf(doc, from_page=from_page, to_page=to_page)
    result_doc.save(filename=f"separated/{from_page}_{to_page}.pdf")


while start <= stop:
    if start + step > stop:
        break

    create_doc(doc, start, start + step)

    start += step

last_dif = stop - start
create_doc(doc, stop - last_dif, stop)
