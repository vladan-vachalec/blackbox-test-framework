import yaml
from behave import when, step

from definitions import CONFIG_PATH
from utils.selenium.selenium_service import SeleniumService

config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)['website']


@when('a user opens a page {url}')
def step_impl(context, url):
    SeleniumService.open_webpage(SeleniumService(), url)


@step("refreshes the pages {count:d} times")
def step_impl(context, count):
    SeleniumService.refresh_page(SeleniumService(), count)


@step('logs into the website')
def step_impl(context):
    context.page = context.page.login(config['username'], config['password'])
