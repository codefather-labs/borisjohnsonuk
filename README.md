|  ![logo](media/picture1.jpeg)   |
|-----|
|  ![logo](media/full.jpeg)   |
> Instagram: [@borisjohnsonuk](https://www.instagram.com/borisjohnsonuk/)
> 
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


### More
- The first thing Boris Johnson does is to open your PDF file via [Document](https://pymupdf.readthedocs.io/en/latest/document.html?highlight=Document) reference. Then bypasses each [Page](https://pymupdf.readthedocs.io/en/latest/page.html?highlight=Page) reference, which is a representation of the pages of the PDF file.
- Then, ideating over each page, Boris calls [.extractJSON](https://pymupdf.readthedocs.io/en/latest/textpage.html?highlight=extractJSON#TextPage.extractJSON) for each page. This expands the byte representation of the page into JSON dictionaries that hold all the data in each page.
- [This code can be tracked here](https://github.com/codefather-labs/borisjohnsonuk/blob/main/__main__.py#L142-L144)
- Then boris processes each Block in the order of the original queue.
- [Here boris does the initial parsing](https://github.com/codefather-labs/borisjohnsonuk/blob/main/__main__.py#L52) and arranges each block by its type - Picture or text - to further comfortably convert the source blocks into markdown
- Then Boris binds a result [into a doubly linked list](https://github.com/codefather-labs/borisjohnsonuk/blob/main/__main__.py#L99). 
- In what follows, we will think of a sequence of PDF content as nodes, two-linked lists that are represented by Pages. That is, Pages are double-linked lists, and the sequence of content in them are nodes. It's simple.
> This is convenient for us, because in the future, when transforming the content, we will need to understand the state of the current node and its neighbors. That's how we will know when it's time to open markdown tag and when we should close it.  We convert the PDF content into a markdown by having a sequence of content with its own font type (which we parse) and font size (which we also parse) and based on that data we know which block of text belongs to which tag. Then we gradually open the necessary tags, concatenate the lines and close the tags when the font type of each current node in the iteration differs from the font type of the previous node. Obviously, if the fonts are different, it means they belong to different tags. This is why I introduced the Bi-linked list - so that by going through each node, we can check the font type of the previous and next node and understand whether or not we should close/open this or that tag now.
- Then we introduce an entity like [MarkdownProcessor](https://github.com/codefather-labs/borisjohnsonuk/blob/main/processor.py#L11) which takes a Bi-linked list of content as input and encapsulates all further processing and conversion of PDF content into a markdown representation.

### Ideas
- I use Boris Johnson converter for convert pdf books and translate them with [deepl](http://deepl.com).
  By the way, [check it](https://github.com/codefather-labs/deepl-translator-pyppeteer)