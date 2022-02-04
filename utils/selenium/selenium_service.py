import os

from selenium import webdriver

from definitions import SELENIUM_BIN


class SeleniumService:
    class __WebDriver:
        def __init__(self):
            options = webdriver.ChromeOptions()
            options.add_argument('--lang=de')
            self.driver = webdriver.Chrome(os.path.join(SELENIUM_BIN, "chromedriver.exe"), chrome_options=options)

    driver = None

    def __init__(self):
        if not self.driver:
            SeleniumService.driver = SeleniumService.__WebDriver().driver

    def open_webpage(self, url):
        self.driver.get(url)

    def refresh_page(self, count):
        for i in range(count):
            self.driver.refresh()
