#!/usr/bin/env python3

"""
Provides mechanisms to submit TestCase XML files to Polarion.
"""

import requests
import logging
from requests.auth import HTTPBasicAuth
import urllib3

from fmfexporter.adapters.polarion.polarion_test_case import PolarionTestCase
from fmfexporter.adapters.polarion.utils.polarion_config import PolarionConfig


LOGGER = logging.getLogger(__name__)
urllib3.disable_warnings()


class PolarionReporter(object):

    """
    Provides methods for submitting test cases (from PolarionTestCase) objects into Polarion.
    """
    def __init__(self, config_file):
        self.config = PolarionConfig(config_file)
        self.headers = {'Accept': 'application/json'}
        self.auth = HTTPBasicAuth(self.config.username(), self.config.password())

    def submit_testcase(self, testcase: PolarionTestCase):
        """
        Submits the given testcase instance to Polarion.
        If the given test case already exists (looking up by name as:
        "classname"."name") it will be updated. Created otherwise.
        :param testcase:
        :return:
        """
        xml = testcase.to_xml()
        LOGGER.debug(xml)

        xml_file = {'file': ('testcase.xml', xml)}

        response = requests.post(self.config.test_case_url(),
                                 auth=self.auth,
                                 headers=self.headers,
                                 verify=False,
                                 files=xml_file)

        LOGGER.debug("HTTP Response [Code: %s]: %s" % (response.status_code, response.content))
        if response.status_code != 200:
            raise Exception('Error submitting test-case to Polarion: %s' % response.content)
