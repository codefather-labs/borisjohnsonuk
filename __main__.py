import os
import argparse
from types import NoneType

from boris import Boris

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_pdf_path", required=True)
    parser.add_argument("--output_dir_path", required=True)
    parser.add_argument("--from_page", type=int, default=0)
    parser.add_argument("--to_page", type=int)

    args = parser.parse_args()
    from_page = args.from_page
    to_page = args.to_page
    if isinstance(to_page, NoneType):
        to_page = 0

    pdf_absolute_path = os.path.abspath(args.source_pdf_path)  # get filename from command line
    output_dir_path = os.path.abspath(args.output_dir_path)

    boris = Boris(
        source_path=pdf_absolute_path,
        output_dir_path=output_dir_path,
        from_page=from_page,
        to_page=to_page
    )
    boris.fetch_pages()
