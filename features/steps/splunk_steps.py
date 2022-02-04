from behave import step

from utils.splunk.splunk_client import SplunkSearch
from utils.splunk.splunk_fetch import SplunkFetch


@step('searches with the {splunk_query} for the event with the following {rule_type}')
def step_impl(context, splunk_query, rule_type):
    splunk = SplunkFetch()
    splunk.fetch_from_splunk(splunk_query, rule_type)
    context.rule_type = rule_type


@step('an admin checks if an event has been created in Splunk')
def step_impl(context):
    context = SplunkSearch(context.rule_type)
    context.check_event_time()
