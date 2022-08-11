from copy import deepcopy
from typing import Optional, List


# TODO DEPRECATED
# TODO NEED FIX
class TextProcessor:
    def __init__(self):
        self.is_wait_for_code_tag_close = False
        self.code = []
        self.buf = []
        self.tag = None

    @property
    def tag_is_opened(self):
        return bool(self.tag) if self.tag else False

    def add_tag_to_buf(self, tag: str):
        self.buf.append(tag)

    def append_tag(self, tag: str):
        self.tag = tag
        self.add_tag_to_buf(self.tag)

    def prepare_buf_for_return(self, buf: List = None):
        buf = deepcopy(buf[1:-1] if buf else self.buf[1:-1])
        return buf

    def tag_processor(self, tag_signature_map: dict, flags: str, font_flag: str, text: str, buf: list = None):

        current_text_tag = tag_signature_map.get(font_flag)

        # CASE DONE
        # если тег не открыт, значит его нужно открыть
        if not self.tag_is_opened:  # тег пуст
            # но перед этим, подготовим buf к возврату
            # так как он имеет другой тег, а значит готов к возврату
            # если buf не пуст, значит мы в кейсе, когда
            # в buf уже лежит готовый chunk текса с закрытым тегом
            # TODO здесь self.buf может быть пустым
            if self.buf:
                buf = self.prepare_buf_for_return()

            # добавляем новый тег если он есть
            # его может не быть если на входе текст без тегов
            if current_text_tag:
                self.append_tag(current_text_tag)

        # CASE DONE
        # если последний сохраненный тег и тег нового текста не совпадают,
        # значит мы попали в кейс, когда следует закрыть buf последним
        # сохраненным тегом, подготовить buf к возврату отформатировав его и очистить self.buf
        # перед добавлением в него тега нового текста
        elif self.tag_is_opened and current_text_tag != self.tag:

            # закрываем тег в буфере
            self.append_tag(self.tag)

            # готовим буфер с предыдущим закрытым тегом к возврату
            if self.buf:
                buf = f'{self.tag}{" ".join(self.prepare_buf_for_return())}{self.tag}'

            # очищаем self.buf
            self.buf.clear()

            # добавляем новый тег в буфер
            self.append_tag(current_text_tag)

        # CASE DONE
        # кейс при котором последний сохраненный тег и тег нового текста совпадают
        # в этом случае нужно только добавить новый текст в self.buf
        # этот кейс не подразумевает возврата
        elif self.tag_is_opened and current_text_tag == self.tag:
            # self.buf.append(text) вызывается ниже
            # значит дополнительный вызов здесь не требуется
            # однако описание кейса лишним не будет
            ...

        self.buf.append(text)

        # FIXME buf может быть пустым в первом кейсе
        return buf

    def base_text_process(self, text, size, flags):
        if not flags:
            return text

        splited_flags = [str(i).replace(" ", "") for i in flags.split(",")]
        result: Optional[List] = None

        def handle_monospaced_text_font(text: str, flags: str, font_flag: str = None):
            tag_signature_map = {
                "monospaced": "`",
                "code": "```",
            }

            return self.tag_processor(
                tag_signature_map=tag_signature_map,
                flags=flags,
                font_flag=font_flag,
                text=text
            )

        def handle_text_font(text: str, flags: str, font_flag: str = None):
            if font_flag == 'monospaced':
                return handle_monospaced_text_font(
                    text=text,
                    flags=flags,
                    font_flag=font_flag
                )

            tag_signature_map = {
                "italic": "*",
                "bold": "**",
                "serifed": "",
                "proportional": ""
            }

            return self.tag_processor(
                tag_signature_map=tag_signature_map,
                flags=flags,
                font_flag=font_flag,
                text=text
            )

        if 'monospaced' in splited_flags:
            return handle_text_font(
                text=text, font_flag='monospaced', flags=flags
            )

        if 'italic' in splited_flags:
            result = handle_text_font(text=text, font_flag='italic', flags=flags)

        if 'bold' in splited_flags:
            result = handle_text_font(text=text, font_flag='bold', flags=flags)

        if not all(['italic', 'bold', 'monospaced']) in splited_flags:
            result = handle_text_font(text=text, flags=flags)
            # print(result)

        return result

    def process(self,
                text: str,
                size: int,
                flags: str,
                font: str,
                last_text: str = None,
                last_flags: str = None):

        result = None

        if 'serifed' in flags or 'proportional' in flags:
            result = self.base_text_process(text, size, flags)

        return result


text_processor = TextProcessor()
