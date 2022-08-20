from interfaces import AbstractTag, TagRenderFormat


class Blockquote(AbstractTag):
    open_tag = '>'
    close_tag = None
    render_format = TagRenderFormat.LEFT_TAG_ONLY


class SubscriptItalicBold(AbstractTag):
    open_tag = '***~'
    close_tag = '~***'
    render_format = TagRenderFormat.BOTH_TAGS


class SubscriptItalic(AbstractTag):
    open_tag = '*~'
    close_tag = '~*'
    render_format = TagRenderFormat.BOTH_TAGS


class Subscript(AbstractTag):
    open_tag = '~'
    close_tag = '~'
    render_format = TagRenderFormat.BOTH_TAGS


class SuperscriptItalicBold(AbstractTag):
    open_tag = '***^'
    close_tag = '^***'
    render_format = TagRenderFormat.BOTH_TAGS


class SuperscriptItalic(AbstractTag):
    open_tag = '*^'
    close_tag = '^*'
    render_format = TagRenderFormat.BOTH_TAGS


class Superscript(AbstractTag):
    open_tag = '^'
    close_tag = '^'
    render_format = TagRenderFormat.BOTH_TAGS


class ItalicBold(AbstractTag):
    open_tag = '***'
    close_tag = '***'
    render_format = TagRenderFormat.BOTH_TAGS


class Italic(AbstractTag):
    open_tag = '*'
    close_tag = '*'
    render_format = TagRenderFormat.BOTH_TAGS


class Bold(AbstractTag):
    open_tag = '**'
    close_tag = '**'
    render_format = TagRenderFormat.BOTH_TAGS


class Title(AbstractTag):
    open_tag = '#'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class ParagraphTheme(AbstractTag):
    open_tag = '##'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class ParagraphSubtheme(AbstractTag):
    open_tag = '###'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class ChapterNumber(AbstractTag):
    open_tag = '####'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class Code(AbstractTag):
    open_tag = '```'
    close_tag = '```'
    render_format = TagRenderFormat.BOTH_TAGS


class Text(AbstractTag):
    open_tag = None
    close_tag = None
    render_format = TagRenderFormat.NO_TAGS


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
