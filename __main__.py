import os
import argparse

from boris import MarkdownBoris

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source_pdf_path", required=True)
    parser.add_argument("--output_dir_path", required=True)

    args = parser.parse_args()

    pdf_absolute_path = os.path.abspath(args.source_pdf_path)  # get filename from command line
    output_dir_path = os.path.abspath(args.output_dir_path)

    boris = MarkdownBoris(
        source_path=pdf_absolute_path,
        output_dir_path=output_dir_path
    )
    boris.fetch_pages()
