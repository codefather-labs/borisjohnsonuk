import argparse
import os
import shutil

import asyncio
from urllib.parse import quote
from urllib.request import urlopen
from typing import Optional

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

    async def close_browser(self):
        await self.browser.close()
        self.is_started = False
        self.browser = None

    async def start_browser(self):
        os.system('killall Google\ Chrome')
        if not self.is_started:
            """Throw a request."""
            options = {
                "headless": self.headless,
                "no-sandbox": True,
                "single-process": True,
                "disable-dev-shm-usage": True,
                "disable-gpu": True,
                "no-zygote": True,
            }
            if self.executable_path:
                options.setdefault("executablePath", self.executable_path)

            self.browser: Browser = await launch(options)
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

    async def _translate(self, script: str) -> str:
        if not self.is_started:
            while not self.is_started:
                await self.start_browser()
                await asyncio.sleep(self.sleep_secs)

        hash = f"#{self.fr_lang}/{self.to_lang}/{script}"
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

    args = parser.parse_args()

    pdf_absolute_path = os.path.abspath(args.source_pdf_path)  # get filename from command line
    output_dir_path = os.path.abspath(args.output_dir_path)

    translator = CustomDeepLCLI(
        fr_lang='en',
        to_lang='ru',
        headless=False,
        executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        timeout=150000,
        sleep_secs=2
    )

    # import here only for demonstration
    import fonts
    from boris import MarkdownBoris

    # There are AVAIlABLE_FONTS_FOR_MAPPING fonts which we will use
    # for choosing available for translate fonts. For example:
    # images and code is not available for translating
    translatable_fonts = fonts.AVAIlABLE_FONTS_FOR_MAPPING
    translatable_fonts.remove(fonts.Image)
    translatable_fonts.remove(fonts.Code)


    def pre_processing(self, text: str):
        # we don't care about non-secure global var
        # cuz it making small i/o bound job
        global translator
        return translator.translate(text)


    for font in translatable_fonts:
        # then for each caught font, we patch them pre_processing method
        # which will call a translation text method
        font.pre_processing = pre_processing

        # then we need to remove old fonts for font module and set patched fonts
        delattr(fonts, font.__name__)
        setattr(fonts, font.__name__, font)

    # initialize Boris and make him doing his job
    boris = MarkdownBoris(
        source_path=pdf_absolute_path,
        output_dir_path=output_dir_path
    )
    boris.fetch_pages()
