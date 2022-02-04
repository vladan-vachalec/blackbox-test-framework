import logging
from datetime import datetime

from behave import when, step, then

import utils.email.exchange as exchange_service
import utils.email.inbucket as inbucket_service


@step("the email will be {action}")
def step_impl(context, action):
    email_found = False
    resp = inbucket_service.get_emails()
    for email in resp.json():
        if email['subject'].endswith(context.timestamp):
            email_found = True
            break
    if action == 'blocked':
        assert context.incident_blocked_status.lower() == action.lower()
        assert email_found is False

    else:
        assert email_found is True

        # email clean up
        resp = inbucket_service.delete_email(email['id'])
        assert resp.status_code == 200


@when('employee sends an "{action}" "{medium}" to a non-organisation entity')
def step_impl(context, action, medium):
    context.medium = medium
    context.timestamp = datetime.now().strftime("%d-%b-%Y_%H:%M:%S")
    message = 'BLOCKME' if action == 'blocked' else 'FINDME'
    inbucket_service.send_email(context.timestamp, message)


@when("employee sends an email with a content from {input_file}")
def step_impl(context, input_file):
    context.medium = 'email'
    policy = 'no_policy' if not hasattr(context, 'policy') else context.policy
    context.expected_subject = policy + "_" + str(input_file) + "_" + str(
        datetime.now().strftime("%d-%b-%Y_%H:%M:%S"))

    logging.debug(f'Sending mail with subject = {context.expected_subject}')
    if context.use_exchange:
        exchange_service.send_email(context.expected_subject, input_file, context.send_attachments)
    else:
        inbucket_service.send_email_from_file(context.expected_subject, input_file)


@then("user gets last {email_count:d} emails")
def step_impl(context, email_count):
    exchange_service.get_emails(email_count)


@step("the email is present in inbox")
def step_impl(context):
    assert exchange_service.find_email(context.expected_subject), "Couldn't find email with subject: {}".format(
        context.expected_subject)
