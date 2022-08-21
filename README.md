# This is Boris Johnson from UK! 🇬🇧 🇺🇦
## And this is PDF to Markdown converter based on [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/intro.html).
---

### Quick start
```
make build
make example
```
### Features
- Boris can convert your PDF file to Markdown and he supports images! But Text extracts not carefule yet, sorry.
- Python3 support
- Great works inside of Docker image. Outside fitz lib on my M1 Mac was not works. Don't f*ckn know why :(

### Ideas
- parsing code blocks via markdown any lib
- create another way parse backend which transform pdf to html natively 
- and then html to md via client script