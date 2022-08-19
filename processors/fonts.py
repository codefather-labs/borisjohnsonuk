from interfaces import AbstractTag, TagRenderFormat


class Blockquote(AbstractTag):
    open_tag = '>'
    close_tag = None
    render_format = TagRenderFormat.LEFT_TAG_ONLY

    def __init__(self, buf: list):
        self.buf = buf


class SubscriptItalicBold(AbstractTag):
    open_tag = '***~'
    close_tag = '~***'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class SubscriptItalic(AbstractTag):
    open_tag = '*~'
    close_tag = '~*'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class Subscript(AbstractTag):
    open_tag = '~'
    close_tag = '~'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class SuperscriptItalicBold(AbstractTag):
    open_tag = '***^'
    close_tag = '^***'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class SuperscriptItalic(AbstractTag):
    open_tag = '*^'
    close_tag = '^*'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class Superscript(AbstractTag):
    open_tag = '^'
    close_tag = '^'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class ItalicBold(AbstractTag):
    open_tag = '***'
    close_tag = '***'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class Italic(AbstractTag):
    open_tag = '*'
    close_tag = '*'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class Bold(AbstractTag):
    open_tag = '**'
    close_tag = '**'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class Title(AbstractTag):
    open_tag = '#'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class ParagraphTheme(AbstractTag):
    open_tag = '##'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class ParagraphSubtheme(AbstractTag):
    open_tag = '###'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class ChapterNumber(AbstractTag):
    open_tag = '####'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class Code(AbstractTag):
    open_tag = '```'
    close_tag = '```'
    render_format = TagRenderFormat.BOTH_TAGS

    def __init__(self, buf: list):
        self.buf = buf


class Text(AbstractTag):
    open_tag = None
    close_tag = None
    render_format = TagRenderFormat.NO_TAGS

    def __init__(self, buf: list):
        self.buf = buf


FONT_MAP = {
    "sans, proportional": Text,
    "serifed, proportional": Text,
    "serifed, proportional, bold": Bold,
    "serifed, monospaced": Code,
    "serifed, monospaced, bold": Code,
    "italic, serifed, proportional": Italic,
    "italic, serifed, proportional, bold": ItalicBold,
    "italic, serifed, monospaced": Code,
    "superscript, italic, serifed, proportional": SuperscriptItalic
}
