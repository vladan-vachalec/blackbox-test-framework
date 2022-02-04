import datetime
import time

import yaml
from behave import then, when

from definitions import CONFIG_PATH
from utils.symantec_dlp_soap.dlp_soap_client import DLPSoapClient


@then("a DLP Incident with some severity will be generated")
def step_impl(context):
    config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)
    client = get_client(config)

    # loop to find the latest incident and timestamp subject in it
    timeout = 60
    step_time = 5
    # incident subject + policy
    incident_found = False
    for _ in range(1, timeout // step_time):
        time.sleep(step_time)
        incident_list = client.incident_list(savedReportId=config['symantec']['report_id'],
                                             incidentCreationDateLaterThan=datetime.datetime.now() - datetime.timedelta(
                                                 days=360))
        # We will for now take the last found incident and try to find the subject
        try:
            last_incident_id = incident_list['incidentId'][-1]
            print(last_incident_id)
        except IndexError:
            print('No incidents found yet.')
            continue
        incident_detail = client.incident_detail(incidentId=last_incident_id)
        incident_subject = incident_detail[0]['incident']['subject']
        policy = incident_detail[0]['incident']['policy']['name']

        if incident_subject.endswith(context.expected_subject) and policy == context.policy:
            context.incident_blocked_status = incident_detail[0]['incident']['blockedStatus']
            context.incident_id = incident_detail[0]['incidentId']
            context.match_count = incident_detail[0]['incident']['matchCount']
            context.severity = incident_detail[0]['incident']['severity']
            context.status = incident_detail[0]['incident']['status']
            incident_found = True
            break
    assert incident_found is True, "DLP Incident not found. Subject: {}".format(context.expected_subject)


@when("employee changes status of the incident to {incident_status}")
def step_impl(context, incident_status):
    context.updated_status = incident_status
    incident_attributes = {"status": incident_status}
    client = get_client()
    client.update_incidents(incident_long_id=context.incident_id, incident_id=context.incident_id,
                            incident_attributes=incident_attributes, batch_id='status_update')


@then("the incident attributes changes accordingly")
def step_impl(context):
    client = get_client()
    incident_detail = client.incident_detail(incidentId=context.incident_id)
    assert context.updated_status.lower() == incident_detail[0]['incident']['status'].lower()


def get_client(config=None):
    if config is None:
        config = yaml.load(open(CONFIG_PATH, 'r'), Loader=yaml.FullLoader)
    return DLPSoapClient(app_configs={"sdlp_wsdl": config['symantec']['sdlp_wsdl'],
                                      "sdlp_host": config['symantec']['sdlp_host'],
                                      "sdlp_username": config['symantec']['sdlp_username'],
                                      "sdlp_password": config['symantec']['sdlp_password']})


@then(
    "the generated incidents contain correct values ({expected_status}, {expected_nr_matches:d}, {expected_severity})")
def step_impl(context, expected_status, expected_nr_matches, expected_severity):
    print("  expected_subject = ", str(context.expected_subject))
    print("  ID = " + str(context.incident_id) + "   expected_cnt = " + str(
        expected_nr_matches) + "    match_cnt = " + str(context.match_count))

    assert context.status.lower() == expected_status.lower(), generate_assertion_error(context.expected_subject,
                                                                                       'Status',
                                                                                       context.status.lower(),
                                                                                       expected_status.lower())
    assert context.match_count == expected_nr_matches, generate_assertion_error(context.expected_subject,
                                                                                'Match count',
                                                                                context.match_count,
                                                                                expected_nr_matches)
    assert context.severity.lower() == expected_severity.lower(), generate_assertion_error(context.expected_subject,
                                                                                           'Severity',
                                                                                           context.severity.lower(),
                                                                                           expected_severity.lower())


def generate_assertion_error(dlp_timestamp, attribute, actual_value, expected_value):
    return "DLP Incident Subject: {}. Attribute: {}. Actual value: {}, Expected value: {}".format(
        dlp_timestamp, attribute, actual_value, expected_value)
