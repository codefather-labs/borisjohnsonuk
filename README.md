# This is Boris Johnson from UK! 🇬🇧 🇺🇦
## And this is PDF to Markdown converter based on [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/intro.html).
---

### Quick start
```
$ make build
$ make linux_example
$ make macos_example
$ make windows_example # not tested yet
```
### Features
- Boris can convert your PDF file to Markdown.
- It supports images, codeblock, blockquotes, titles, and all other kinds of font flags! (Unknown font flags ease to adding manually)
- Text extracts carefully now!
- Great works inside of Docker image. Outside fitz lib on my M1 Mac was not works. Don't f*ckn know why :(

### Ideas
- I use Boris Johnson converter for convert pdf books and translate them with [deepl](http://deepl.com).
  By the way, [check it](https://github.com/codefather-labs/deepl-translator-pyppeteer)