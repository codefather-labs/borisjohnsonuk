from interfaces import AbstractTag, TagRenderFormat


class FontTag(AbstractTag):
    def render(self, text: str) -> str:
        rendered_string = None

        if self.render_format == TagRenderFormat.BOTH_TAGS:
            rendered_string = f"{self.open_tag}{text}{self.close_tag}"

        elif self.render_format == TagRenderFormat.LEFT_TAG_ONLY:
            rendered_string = f"{self.open_tag}{text}"

        elif self.render_format == TagRenderFormat.RIGHT_TAG_ONLY:
            rendered_string = f"{text}{self.close_tag}"

        elif self.render_format == TagRenderFormat.NO_TAGS:
            rendered_string = text

        return rendered_string


class Blockquote(FontTag):
    open_tag = '>'
    close_tag = None
    render_format = TagRenderFormat.LEFT_TAG_ONLY


class SubscriptItalicBold(FontTag):
    open_tag = '***~'
    close_tag = '~***'
    render_format = TagRenderFormat.BOTH_TAGS


class SubscriptItalic(FontTag):
    open_tag = '*~'
    close_tag = '~*'
    render_format = TagRenderFormat.BOTH_TAGS


class Subscript(FontTag):
    open_tag = '~'
    close_tag = '~'
    render_format = TagRenderFormat.BOTH_TAGS


class SuperscriptItalicBold(FontTag):
    open_tag = '***^'
    close_tag = '^***'
    render_format = TagRenderFormat.BOTH_TAGS


class SuperscriptItalic(FontTag):
    open_tag = '*^'
    close_tag = '^*'
    render_format = TagRenderFormat.BOTH_TAGS


class Superscript(FontTag):
    open_tag = '^'
    close_tag = '^'
    render_format = TagRenderFormat.BOTH_TAGS


class ItalicBold(FontTag):
    open_tag = '***'
    close_tag = '***'
    render_format = TagRenderFormat.BOTH_TAGS


class Italic(FontTag):
    open_tag = '*'
    close_tag = '*'
    render_format = TagRenderFormat.BOTH_TAGS


class Bold(FontTag):
    open_tag = '**'
    close_tag = '**'
    render_format = TagRenderFormat.BOTH_TAGS


class Title(FontTag):
    open_tag = '#'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class ParagraphTheme(FontTag):
    open_tag = '##'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class ParagraphSubtheme(FontTag):
    open_tag = '###'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class ChapterNumber(FontTag):
    open_tag = '####'
    close_tag = '\n'
    render_format = TagRenderFormat.BOTH_TAGS


class Code(FontTag):
    open_tag = '```'
    close_tag = '```'
    render_format = TagRenderFormat.BOTH_TAGS


class Text(FontTag):
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
