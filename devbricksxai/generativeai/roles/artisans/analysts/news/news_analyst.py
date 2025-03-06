import os
import time
from abc import ABC
from os import path
from random import randrange

import tldextract
from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

from devbricksx.common.string_ops import to_trimmed_str
from devbricksx.development.log import debug, warn, error
from devbricksxai.generativeai.roles.artisans.analyst import Analyst
from devbricksxai.generativeai.roles.artisans.escort import Escort
from devbricksxai.generativeai.roles.character import get_character_by_name

TMP_DIRECTORY = "drivers/tmp/"
__IMAGE_DIR__ = "trending/images"
__CLOUD_STORAGE_DIRECTORY__ = "trending/"

class News:
    id = None
    title = None
    link = None
    content = []
    provider = None
    datetime = None
    abstract = None
    cover_image = None
    ref = 0
    tags = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    @staticmethod
    def from_dict(data):
        return News(**data)

    def __str__(self):
        print_str = '[%s, id: %s][title: %s, link: %s, date: %s, ref: %s]: abstract = [%s], cover = [%s], content = [%s], tags = [%s]'

        if self.ref is None:
            ref_str = "unknown"
        else:
            ref_str = f"{self.ref}"

        return print_str % (self.provider,
                            self.id,
                            self.title,
                            self.link,
                            self.datetime,
                            ref_str,
                            self.abstract,
                            self.cover_image,
                            to_trimmed_str(self.content),
                            ', '.join(t for t in self.tags)
                            )



class NewsAnalyst(Analyst, ABC):

    MAX_ITEMS = 20

    ACTION_EXTRACT_ITEMS = "extract_items"
    ACTION_ANALYZE_ITEM = "analyze_item"

    def perform_navigations(self, driver: webdriver.Chrome, **kwargs):
        debug("No navigations performed by default...")
        pass

    def get_page_source(self, driver: webdriver.Chrome, **kwargs):
        dumped_len = 0
        if driver.page_source is not None:
            dumped_len = len(driver.page_source)
        debug(f"browser content: {dumped_len} characters")

        return driver.page_source

    def get_html_by_url(self, url, timeout=None, **kwargs):
        if not path.exists(TMP_DIRECTORY):
            os.mkdir(TMP_DIRECTORY)

        user_agent = (
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            ' Chrome/58.0.3029.110 Safari/537.36'
        )

        debug(f"using user-agent: {user_agent}")

        chrome_options = Options()

        chrome_options.add_argument("--headless")  # Ensures the browser runs in headless mode
        chrome_options.add_argument("--disable-gpu")  # Applicable to windows os only
        chrome_options.add_argument("--no-sandbox")  # This bypass the OS security model, it's not recommended for production
        chrome_options.add_argument("window-size=1024,768")
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument(f"user-agent={user_agent}")

        # use separated TMP directory to avoid crash of ChromeDriver by sharing same directory
        chrome_options.add_argument(f"--user-data-dir={TMP_DIRECTORY}")
        chrome_options.add_argument(f"--crash-dumps-dir={TMP_DIRECTORY}/Crashpad")

        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities['acceptSslCerts'] = True
        desired_capabilities['acceptInsecureCerts'] = True

        browser = webdriver.Chrome(
            executable_path="drivers/chromedriver",
            options=chrome_options,
            desired_capabilities=desired_capabilities
        )
        browser.set_page_load_timeout(timeout)
        debug("starting get url: {}, timeout {}s".format(url, timeout))

        page_content = ""
        try:
            browser.get(url)
            interval = randrange(3, 10)
            debug(f"randomly sleep {interval}s to bypass captcha")
            time.sleep(interval)

            navigation_target = self.perform_navigations(browser, **kwargs)
            page_content = self.get_page_source(
                browser,  navigation_target = navigation_target)

        except TimeoutException:
            warn("get page took too long to load, the page content might not be completely loaded.")
        except WebDriverException as e:
            error(f"failed to get content from url[{url}]: {e}")
        debug("ending get url: {}".format(url))

        browser.quit()

        return page_content

    @classmethod
    def get_hostname(cls, url):
        extracted = tldextract.extract(url)
        base_domain = "{}.{}".format(extracted.domain,
                                     extracted.suffix) if extracted.domain and extracted.suffix else ''
        return base_domain

    @staticmethod
    def copy_cover_image(cover_image_url, **kwargs):
        debug(f"copying cover image: {cover_image_url}")
        if cover_image_url is None:
            return cover_image_url

        painter_name = kwargs.get('painter', None)
        if painter_name is None:
            debug(f"painter is not set yet.")
            return cover_image_url

        painter = get_character_by_name(painter_name)
        if painter is None:
            return cover_image_url
        debug(f"using painter: {painter}")

        in_escort_name = kwargs.get('in_escort', None)
        if in_escort_name is None:
            debug(f"in_escort is not set yet.")
            return cover_image_url

        in_escort = get_character_by_name(in_escort_name)
        if in_escort is None:
            return cover_image_url
        debug(f"using in_escort: {in_escort}")

        out_escort_name = kwargs.get('out_escort', None)
        if out_escort_name is None:
            debug(f"out_escort_name is not set yet.")
            return cover_image_url

        out_escort = get_character_by_name(out_escort_name)
        if out_escort is None:
            return cover_image_url
        debug(f"using out_escort: {out_escort}")

        if not os.path.exists(__IMAGE_DIR__):
            debug('image directory [{}] is not existed. creating one...'
                  .format(__IMAGE_DIR__))
            os.mkdir(__IMAGE_DIR__)

        now = int(round(time.time() * 1000))
        file_name = path.join(__IMAGE_DIR__, "news_analyst_{}.jpg".format(now))

        local_file = in_escort.craft(direction=Escort.DIRECTION_IN, src=cover_image_url, dest=file_name)
        debug(f"image downloaded to: {local_file}")

        painter.compress_image(local_file, local_file, 85)

        download_link = None
        if local_file is not None:
            download_link = out_escort.craft(direction=Escort.DIRECTION_OUT,
                                             src=local_file,
                                             dest=__CLOUD_STORAGE_DIRECTORY__,
                                             metadata={
                                                 "firebaseStorageDownloadTokens": now,
                                                 "contentType": "image/jpeg",
                                                 "cacheControl": "public, max-age=31536000"
                                             })
        debug(f"image uploaded to: {download_link}")

        image_str = download_link
        if image_str is None:
            image_str = local_file

        return image_str