# -*- coding: utf-8 -*-
# pragma pylint: disable=unused-argument, no-self-use

import datetime
import os

import zeep
from requests import Session
from requests.auth import HTTPBasicAuth, AuthBase
from zeep.cache import SqliteCache


class SymantecAuth(AuthBase):
    """SymantecAuth a class which inherits from requests.AuthBase, 
    if the URL starts with our DLP Instance hostname, add Basic Authentication to requests
    otherwise send a request without credentials.

    Needed due to a call to www.w3.org/2005/05/xmlmime which fails if credentials are passed
    Referenced from here : https://www.symantec.com/connect/forums/api-dlp-servers
    :param AuthBase: [description]
    :type AuthBase: [type]  
    :return: [description]
    :rtype: [type]
    """

    def __init__(self, username, password, host):
        self.basic = HTTPBasicAuth(username, password)
        self.host = host

    def __call__(self, r):
        if r.url.startswith(self.host):
            return self.basic(r)
        else:
            return r


class DLPSoapClient():
    class_vars_loaded = False

    def __init__(self, app_configs):
        """__init__ setup the DLPSOAPClient; 
        loading in the parameters from app_configs
        then initialise a soap_client with the details
        
        :param app_configs: a dictionary containing key-value pairs used for 
        setting up a client with Symantec DLP. 
        :type app_configs: dict
        """
        print(app_configs)
        if not self.class_vars_loaded:
            self.load_class_variables(app_configs)

    @classmethod
    def load_class_variables(cls, app_configs):
        """load_class_variables loads in the app_configs dict
        and assigned each value as a class variable.
        After loading, a zeep symantec_dlp_soap Client is created with our credentials
        
        :param app_configs: a dictionary containing key-value pairs used for 
        setting up a client with Symantec DLP. 
        :type app_configs: dict
        """

        from definitions import ROOT_DIR
        xmlmime = os.path.join(ROOT_DIR, 'utils', 'symantec_dlp_soap', '2005_05_xmlmime.xml')
        with open(xmlmime, mode="rb") as f:
            filecontent = f.read()
            cache = SqliteCache(timeout=None)
            cache.add("http://www.w3.org/2005/05/xmlmime", filecontent)
            cache.add("https://www.w3.org/2005/05/xmlmime", filecontent)

        cls.host = cls.get_config_option(app_configs=app_configs,
                                         option_name="sdlp_host",
                                         optional=False)
        cls.wsdl = cls.get_config_option(app_configs=app_configs,
                                         option_name="sdlp_wsdl",
                                         optional=False)
        # Gather the DLP User Name
        cls.dlp_username = cls.get_config_option(app_configs=app_configs,
                                                 option_name="sdlp_username",
                                                 optional=False)
        # Gather the DLP User Password
        cls.dlp_password = cls.get_config_option(app_configs=app_configs,
                                                 option_name="sdlp_password",
                                                 optional=False)

        cls.session = Session()
        cls.session.verify = False  # TODO: Expose as app.config
        cls.session.auth = SymantecAuth(cls.dlp_username, cls.dlp_password, cls.host)

        # Setup Transport with our credentials 
        cls.transport = zeep.Transport(session=cls.session, cache=cache)
        # Create a soap_client from the wsdl and transport
        cls.soap_client = zeep.Client(wsdl=cls.wsdl, transport=cls.transport)
        cls.class_vars_loaded = True

    @staticmethod
    def get_config_option(app_configs, option_name, optional=False, placeholder=None):
        """get_config_option Given option_name, checks if it is in appconfig. 
        Raises ValueError if a mandatory option is missing
        
        :param app_configs: a dictionary containing key-value pairs used for 
        setting up a client with Symantec DLP. 
        :type app_configs: dict
        :param option_name: the name of the option to get
        :type option_name: string
        :param optional: defaults to False
        :type optional: bool, optional
        :param placeholder: defaults to None
        :type placeholder: optional
        :return: returns the specified app.config if found
        """
        option = app_configs.get(option_name)
        err = "'{0}' is mandatory and is not set in app.config file. You must set this value to run this function".format(
            option_name)

        if not option and optional is False:
            raise ValueError(err)
        elif optional is False and placeholder is not None and option == placeholder:
            raise ValueError(err)
        else:
            return option

    @classmethod
    def incident_list(cls, savedReportId=0, incidentCreationDateLaterThan=datetime.datetime.now()):
        """incident_list API Call to gather a list of incidents from a saved report.
        
        :param savedReportId: the ID of a saved report, 
        if not provided no incidents will be found, defaults to 0
        :type savedReportId: int, optional
        :param incidentCreationDateLaterThan: Only incidents that were created after the incidentCreationDateLaterThan date will be returned, defaults to datetime.datetime.now()
        :type incidentCreationDateLaterThan: datetime, required
        :return: A list of incidentIds and incidentLongIds
        :rtype: [type]
        """
        incident_list = cls.soap_client.service.incidentList(
            savedReportId=savedReportId,
            incidentCreationDateLaterThan=incidentCreationDateLaterThan)

        return incident_list

    @classmethod
    def incident_detail(cls, incidentId=None):
        """incident_detail API Call to gather the details for a specified incident
        Even though incidentLongId isin't exposed in the function call, 
        that is usable for a query also
        
        :param incidentId: the ID of the incident to retreive, defaults to None
        :type incidentId: [type], optional
        :return: [description]
        :rtype: [type]
        """
        incident_detail = cls.soap_client.service.incidentDetail(incidentId=incidentId)

        return incident_detail

    @classmethod
    def incident_binaries(cls, incidentId=None, includeOriginalMessage=False, includeAllComponents='?'):
        """incident_binaries API Call to gather the binaries (Attachments) for an incident.
        
        :param incidentId: [description], defaults to None
        :type incidentId: [type], optional
        :param includeOriginalMessage:  defaults to False
        :type includeOriginalMessage: bool, optional
        :param includeAllComponents: defaults to '?'
        :type includeAllComponents: str, optional
        """
        binaries = cls.soap_client.service.incidentBinaries(
            incidentId=incidentId,
            includeOriginalMessage=includeOriginalMessage,
            includeAllComponents=includeAllComponents)

    @classmethod
    def incident_status(cls):
        """incident_status Used to retreive the incident status
        
        :return: [description]
        :rtype: incidentStatusList Object
        """
        status = cls.soap_client.service.listIncidentStatus()

        return status

    @classmethod
    def list_custom_attributes(cls):
        """list_custom_attributes return a list of all custom attribute names
        
        :return: [description]
        :rtype: list
        """
        custom_attributes = cls.soap_client.service.listCustomAttributes()

        return custom_attributes

    @classmethod
    def update_incidents(cls, incident_long_id, incident_id, incident_attributes, batch_id=None):
        """Update incident details for one or more incidents.

        Params:
            batch_id - unique identifier for the batch to execute.
            incident_long_ids - list of incident IDs (long) to update.
            incident_ids - list of incident IDs (int) to update.
            incident_attributes - dict of attributes to update.
        """
        attributes = {
            "severity": None,
            "status": None,
            "note": None,
            "customAttribute": None,
            "dataOwner": None,
            "remediationStatus": None,
            "remediationLocation": None,
        }
        attributes.update(incident_attributes)
        payload = {
            "updateBatch": {
                "batchId": batch_id,
                "incidentId": incident_id,
                "incidentLongId": incident_long_id,
                "incidentAttributes": attributes,
            }
        }
        update_incident = cls.soap_client.service.updateIncidents(**payload)
        return update_incident
