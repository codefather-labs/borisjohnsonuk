from borisjohnsonuk.interfaces import AbstractTag, TagRenderFormat


class FontTag(AbstractTag):
    def render(self, text: str) -> str:
        rendered_string = None

        text = self.pre_processing(text)

        if self.render_format == TagRenderFormat.BOTH_TAGS:
            rendered_string = f"{self.open_tag}{text}{self.close_tag}"

        elif self.render_format == TagRenderFormat.LEFT_TAG_ONLY:
            rendered_string = f"{self.open_tag}{text}"

        elif self.render_format == TagRenderFormat.RIGHT_TAG_ONLY:
            rendered_string = f"{text}{self.close_tag}"

        elif self.render_format == TagRenderFormat.NO_TAGS:
            rendered_string = text

        return self.post_processing(rendered_string)

    def pre_processing(self, text: str):
        return text

    def post_processing(self, rendered_string: str):
        if "#" in rendered_string:
            rendered_string = rendered_string.replace('*', '')
            return f"\n\n{rendered_string}\n\n"
        return rendered_string


class Image(FontTag):
    open_tag = None
    close_tag = None
    render_format = TagRenderFormat.NO_TAGS

    def pre_processing(self, text: str):
        if not str(text[0]).isalnum():
            text = text[1:]

        if not str(text[-1]).isalnum():
            text = text[:-1]

        return f"\n{text}\n"


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

    # FIXME its not everytime is subtitles
    # def post_processing(self, rendered_string: str):
    #     if len(rendered_string.split(" ")) > 1:
    #         rendered_string = f"\n\n{rendered_string}\n\n"
    #     return rendered_string


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

    keyword_open_tag = '`'
    keyword_close_tag = '`'

    code_open_tag = '\n```\n'
    code_close_tag = '\n```\n'

    def pre_processing(self, text: str):
        if '\n' not in text:
            self.open_tag = self.keyword_open_tag
            self.close_tag = self.keyword_close_tag
        else:
            self.open_tag = self.code_open_tag
            self.close_tag = self.code_close_tag
        return text

    def post_processing(self, rendered_string: str):
        rendered_string = rendered_string.replace('  ', ' ')
        return rendered_string


class Text(FontTag):
    open_tag = None
    close_tag = None
    render_format = TagRenderFormat.NO_TAGS


FONT_SIZE_SIGNATURE_MAP = {
    31: "#",
    30: '#',
    29: "#",
    28: "#",
    27: "#",
    26: "#",
    25: "###",
    24: "###",
    23: "###",
    22: "###",
    21: "###",
    20: "###",
    19: "###",
    18: "###",
    17: "###",
    16: "####",
    15: "####",
    14: "######",
    13: "######",
    12: "######",
}

TITLE_SIZE_MIN = min(FONT_SIZE_SIGNATURE_MAP.keys())
TITLE_SIZE_MAX = max(FONT_SIZE_SIGNATURE_MAP.keys())

AVAIlABLE_FONTS_FOR_MAPPING = [
    Text, Italic, Bold,
    ItalicBold, Code, Image,
    Blockquote, ChapterNumber,
    Subscript, SubscriptItalic, SubscriptItalicBold,
    Superscript, SuperscriptItalic, SuperscriptItalicBold,
    Title, ParagraphTheme, ParagraphSubtheme
]

FONT_MAP = {
    "sans, proportional": Text,
    "serifed, proportional": Text,
    "serifed, proportional, bold": Bold,
    "serifed, monospaced": Code,
    "serifed, monospaced, bold": Code,
    "italic, serifed, proportional": Italic,
    "italic, serifed, proportional, bold": ItalicBold,
    "italic, serifed, monospaced": Code,
    "superscript, italic, serifed, proportional": SuperscriptItalic,
    "image": Image,
}


def flags_decomposer(flags):
    """
        Make font flags human readable.
        Useful for PyMuPDF font flags to unwrap them from byte view
    """
    l = []
    if flags & 2 ** 0:
        l.append("superscript")
    if flags & 2 ** 1:
        l.append("italic")
    if flags & 2 ** 2:
        l.append("serifed")
    else:
        l.append("sans")
    if flags & 2 ** 3:
        l.append("monospaced")
    else:
        l.append("proportional")
    if flags & 2 ** 4:
        l.append("bold")
    return ", ".join(l)
