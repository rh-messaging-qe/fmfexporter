#!/usr/bin/env python3

"""
Provides mechanisms to submit TestCase XML files to Polarion.
"""

import requests
import logging

from requests import RequestException, Response
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

        try:
            response: Response = requests.post(self.config.test_case_url(),
                                     auth=self.auth,
                                     headers=self.headers,
                                     verify=False,
                                     files=xml_file)
        except RequestException as req_ex:
            err_msg = "Error submitting test case: %s" % req_ex
            LOGGER.error(err_msg)
            print(err_msg)
            raise req_ex

        LOGGER.debug("HTTP Response [Code: %s]: %s" % (response.status_code, response.content))

        if response.status_code != 200:
            raise Exception('Error submitting test-case to Polarion: %s' % response.content)
        else:
            self.print_job_ids(testcase, response.json())

    def print_job_ids(self, tc: PolarionTestCase, response: dict):
        """
        Parse response (dict) and extract "job-ids" for each associated XML file.
        :param tc:
        :param response:
        :return:
        """
        files = [f for f in response['files']] if 'files' in response else []

        # Iterate through each file (right now only "testcase.xml" should exist)
        # and if a "job-ids" list is present, display the URL for each.
        for file in files:
            if 'job-ids' not in response['files'][file]:
                continue
            [self.print_tc_job_url(tc.id, j) for j in response['files'][file]['job-ids']]

    def print_tc_job_url(self, tc_id: str, job_id: str):
        """
        Print the test case id along with a statically generated URL for submitted job id.
        :param tc_id:
        :param job_id:
        :return:
        """
        tc_job_url = "%s-log?jobId=%s (ID: %s)" % (self.config.test_case_url(), job_id, tc_id)
        LOGGER.info(tc_job_url)
        print(tc_job_url)
