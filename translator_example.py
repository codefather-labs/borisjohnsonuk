import argparse
import os

import asyncio
from types import NoneType
from urllib.parse import quote
from urllib.request import urlopen
from typing import Optional, List

import shutil
from pyppeteer.browser import Browser  # type: ignore[import]
from pyppeteer.errors import TimeoutError  # type: ignore[import]
from pyppeteer.launcher import launch  # type: ignore[import]
from pyppeteer.page import Page  # type: ignore[import]


class DeepLCLIError(Exception):
    pass


class DeepLCLIPageLoadError(Exception):
    pass


class DeepLCLI:
    fr_langs = {
        "auto",
        "bg",
        "cs",
        "da",
        "de",
        "el",
        "en",
        "es",
        "et",
        "fi",
        "fr",
        "hu",
        "it",
        "ja",
        "lt",
        "lv",
        "nl",
        "pl",
        "pt",
        "ro",
        "ru",
        "sk",
        "sl",
        "sv",
        "zh",
    }
    to_langs = fr_langs - {"auto"}

    def __init__(self, fr_lang: str, to_lang: str) -> None:
        if fr_lang not in self.fr_langs:
            raise DeepLCLIError(
                f"{repr(fr_lang)} is not valid language. Valid language:\n"
                + repr(self.fr_langs)
            )
        elif to_lang not in self.to_langs:
            raise DeepLCLIError(
                f"{repr(to_lang)} is not valid language. Valid language:\n"
                + repr(self.to_langs)
            )
        self.fr_lang = fr_lang
        self.to_lang = to_lang
        self.translated_fr_lang: str | None = None
        self.translated_to_lang: str | None = None
        self.max_length = 5000

    def internet_on(self) -> bool:
        """Check an internet connection."""
        try:
            urlopen("http://www.google.com/", timeout=10)
            return True
        except IOError:
            return False

    def _chk_script(self, script: str) -> str:
        """Check cmdarg and stdin."""
        script = script.rstrip("\n")
        if self.max_length is not None and len(script) > self.max_length:
            # raise err if stdin > self.max_length chr
            raise DeepLCLIError(
                "Limit of script is less than {} chars(Now: {} chars).".format(
                    self.max_length, len(script)
                )
            )
        elif len(script) <= 0:
            # raise err if stdin <= 0 chr
            raise DeepLCLIError("Script seems to be empty.")
        else:
            return script

    def translate(self, script: str) -> str:
        if not self.internet_on():
            raise DeepLCLIPageLoadError("Your network seem to be offline.")
        self._chk_script(script)
        script = quote(script.replace("/", r"\/"), safe="")
        return asyncio.get_event_loop().run_until_complete(self._translate(script))

    async def _translate(self, script: str) -> str:
        """Throw a request."""
        browser: Browser = await launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--single-process",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-zygote",
            ],
        )
        page: Page = await browser.newPage()
        userAgent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)"
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/77.0.3864.0 Safari/537.36"
        )
        await page.setUserAgent(userAgent)
        hash = f"#{self.fr_lang}/{self.to_lang}/{script}"
        await page.goto("https://www.deepl.com/translator" + hash)
        try:
            await page.waitForSelector("#dl_translator > div.lmt__text", timeout=15000)
        except TimeoutError:
            raise DeepLCLIPageLoadError("Time limit exceeded. (30000ms)")

        try:
            await page.waitForFunction(
                """
                () => document.querySelector(
                'textarea[dl-test=translator-target-input]').value !== ""
            """
            )

            await page.waitForFunction(
                """
                () => !document.querySelector(
                'textarea[dl-test=translator-target-input]').value.includes("[...]")
            """
            )
            await page.waitForFunction(
                """
                () => document.querySelector("[dl-test='translator-source-input']") !== null
            """
            )
            # await page.waitForFunction(
            #     """
            #     () => document.querySelector("[dl-test='translator-target-lang']") !== null
            # """
            # )
        except TimeoutError:
            raise DeepLCLIPageLoadError("Time limit exceeded. (30000ms)")

        output_area = await page.J('textarea[dl-test="translator-target-input"]')
        res = await page.evaluate("elm => elm.value", output_area)
        self.translated_fr_lang = str(
            await page.evaluate(
                """() => {
            return document.querySelector("[dl-test='translator-source-input']").lang
            }"""
            )
        ).split("-")[0]

        self.translated_to_lang = str(
            await page.evaluate(
                """() => {
            const l = document.querySelector("[dl-test='translator-target-lang']");
            return l === null ? "" : l.getAttribute("dl-selected-lang")
            }"""
            )
        ).split("-")[0]
        await browser.close()
        if type(res) is str:
            return res.rstrip("\n")
        else:
            raise ValueError(
                f"Invalid response. Type of response must be str, got {type(res)})"
            )


class CustomDeepLCLI(DeepLCLI):
    def __init__(self,
                 fr_lang: str,
                 to_lang: str,
                 headless: bool = False,
                 executable_path: str = None,
                 timeout: int = 150000,
                 sleep_secs: int = 1):

        super().__init__(fr_lang, to_lang)
        self.browser: Optional[Browser] = None
        self.is_started = False
        self.headless = headless
        self.executable_path: Optional[str] = executable_path
        self.timeout = timeout
        self.sleep_secs = sleep_secs
        self.loop = asyncio.get_event_loop()
        self.page: Optional[Page] = None
        os.system('killall chrome')

    async def close_browser(self):
        await self.browser.close()
        self.is_started = False
        self.browser = None

    async def start_browser(self):
        if not self.is_started:
            """Throw a request."""
            args = [
                "--disable-blink-features=AutomationControlled",
                "--enable-javascript",
                "--enable-extensions",
                # "--single-process",
                # "--kiosk",
                # "--no-sandbox",
                # "--single-process",
                # "--disable-dev-shm-usage",
                # "--disable-gpu",
                # "--no-zygote",
            ]

            self.browser: Browser = await launch(
                headless=False,
                executablePath=self.executable_path,
                ignoreDefaultArgs=['--enable-automation'],
                useAutomationExtensions=False,
                args=args,
            )

            self.is_started = True

            self.page: Page = await self.browser.newPage()

            userAgent = (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6)"
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/77.0.3864.0 Safari/537.36"
            )
            await self.page.setUserAgent(userAgent)
            hash = f"#{self.fr_lang}/{self.to_lang}"
            await self.page.goto("https://www.deepl.com/translator" + hash)
            try:
                self.page.waitForSelector("#dl_translator > div.lmt__text", timeout=self.timeout)
            except TimeoutError:
                raise DeepLCLIPageLoadError(f"Time limit exceeded. ({self.timeout}ms)")

    async def translate(self, script: str) -> str:
        # if not self.internet_on():
        #     raise DeepLCLIPageLoadError("Your network seem to be offline.")
        # self._chk_script(script)
        # script = quote(script.replace("/", r"\/"), safe="")

        return await self._translate(script)

    def translate_sync(self, script: str) -> str:
        return self.loop.run_until_complete(self.translate(script))

    async def _translate(self, script: str) -> str:
        if not self.is_started:
            while not self.is_started:
                await self.start_browser()
                await asyncio.sleep(self.sleep_secs)

        hash = f"#{self.fr_lang}/{self.to_lang}/"
        await self.page.goto(f"https://www.deepl.com/translator" + hash)

        try:
            await self.page.waitForSelector("#dl_translator > div.lmt__text", timeout=self.timeout)
        except TimeoutError:
            raise DeepLCLIPageLoadError(f"Time limit exceeded. ({self.timeout}ms)")

        await self.page.click(selector="textarea")
        await self.page.type('textarea', script)
        await asyncio.sleep(self.sleep_secs)

        try:
            await self.page.waitForFunction(
                """
                () => document.querySelector(
                'textarea[dl-test=translator-target-input]').value !== ""
            """, timeout=self.timeout
            )

            await self.page.waitForFunction(
                """
                () => !document.querySelector(
                'textarea[dl-test=translator-target-input]').value.includes("[...]")
            """, timeout=self.timeout
            )
            await self.page.waitForFunction(
                """
                () => document.querySelector("[dl-test='translator-source-input']") !== null
            """, timeout=self.timeout
            )
            # await page.waitForFunction(
            #     """
            #     () => document.querySelector("[dl-test='translator-target-lang']") !== null
            # """
            # )
        except TimeoutError:
            raise DeepLCLIPageLoadError(f"Time limit exceeded. ({self.timeout}ms)")

        await asyncio.sleep(self.sleep_secs)
        output_area = await self.page.J('textarea[dl-test="translator-target-input"]')
        res = await self.page.evaluate("elm => elm.value", output_area)

        self.translated_fr_lang = str(
            await self.page.evaluate(
                """() => {
            return document.querySelector("[dl-test='translator-source-input']").lang
            }"""
            )
        ).split("-")[0]

        self.translated_to_lang = str(
            await self.page.evaluate(
                """() => {
            const l = document.querySelector("[dl-test='translator-target-lang']");
            return l === null ? "" : l.getAttribute("dl-selected-lang")
            }"""
            )
        ).split("-")[0]

        await self.page.evaluate(
            """
            document.getElementById('translator-source-clear-button').click()
            """
        )
        await asyncio.sleep(self.sleep_secs)

        if type(res) is str:
            return res.rstrip("\n")
        else:
            raise ValueError(
                f"Invalid response. Type of response must be str, got {type(res)})"
            )


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

    translator = CustomDeepLCLI(
        fr_lang='en',
        to_lang='ru',
        headless=False,
        executable_path="/usr/bin/google-chrome-stable",
        timeout=150000,
        sleep_secs=2
    )

    from boris import Boris, MuPDFBackend
    from processor import ContentProcessor


    class TranslatableContentProcessor(ContentProcessor):

        """
        In this case, out post_processor method will
        have a chunks of rendered md text in List view.
        Boris guarantees that all List elements is view of one page.
        For ease PDF Document page, will be created a Processor.
        """

        @staticmethod
        def translate(text: str):
            # we don't care about global cuz it doing small i/o job
            global translator
            return translator.translate_sync(text)

        @staticmethod
        def post_processor(text: List[str]):
            result = []
            for el in text:
                # we want ot translate only common text.
                # Not code blocks or images lol.
                # Translator ignore Keywords with tag '`' - this way we need

                if '```' in el or '![' in el:
                    ...
                else:
                    el = TranslatableContentProcessor.translate(el)
                    ...

                result.append(el)

            return result


    class TranslatableMuPDFBackend(MuPDFBackend):
        translated_path_dir = 'translated'

        def move_translated_page(self, page_number: int):
            file_name = f"{page_number}.md"
            shutil.move(
                src=os.path.join(
                    self.output_dir_path,
                    file_name
                ),
                dst=os.path.join(
                    self.output_dir_path,
                    self.translated_path_dir,
                    file_name
                )
            )

        def fetch_pages(self):
            for page in self.doc.pages(start=self.from_page):
                page_result = self.create_page(page)

                self.save_page(page.number, page_result)

                # move mechanism for not translated already translated pages
                self.move_translated_page(page.number)

                print(f"Page: {page.number} from {self.doc.page_count} done 👌")

                del page

            print(f"{self.output_dir_path.split('/')[-1]} converting success 👌")
            print(f"Result is there -> {self.output_dir_path}")


    class TranslatableBoris(Boris, TranslatableMuPDFBackend):
        def initial_boris(self):
            super(TranslatableBoris, self).initial_boris()
            translated_folder_path = os.path.join(
                self.output_dir_path,
                self.translated_path_dir
            )
            if not os.path.exists(translated_folder_path):
                os.mkdir(translated_folder_path)


    # initialize Boris and make him doing his job

    boris = TranslatableBoris(
        source_path=pdf_absolute_path,
        output_dir_path=output_dir_path,
        from_page=from_page,
        to_page=to_page
    )
    boris.processor = TranslatableContentProcessor
    boris.fetch_pages()
