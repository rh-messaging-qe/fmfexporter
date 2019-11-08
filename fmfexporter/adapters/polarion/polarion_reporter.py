#!/usr/bin/env python3

"""
Provides mechanisms to submit TestCase XML files to Polarion.
"""
import json
import time
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
        self.testcase = None  # type: PolarionTestCase

    def submit_testcase(self, testcase: PolarionTestCase, parse_response=False):
        """
        Submits the given testcase instance to Polarion.
        If the given test case already exists (looking up by name as:
        "classname"."name") it will be updated. Created otherwise.
        :param testcase:
        :param parse_response
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
            self.testcase = testcase
            import_job_urls = self.get_job_urls(testcase, response.json())
            if parse_response:
                self.parse_import_job_data(import_job_urls)

    def get_job_urls(self, tc: PolarionTestCase, response: dict):
        """
        Parse response (dict) and extract "job-url" for each associated XML file.
        :param tc:
        :param response:
        :return:
        """
        job_urls = []
        files = [f for f in response['files']] if 'files' in response else []

        # Iterate through each file (right now only "testcase.xml" should exist)
        # and if a "job-ids" list is present, display the URL for each.
        for file in files:
            if 'job-ids' not in response['files'][file]:
                continue
            for j in response['files'][file]['job-ids']:
                tc_job_url = self.get_tc_job_url(tc.id, j)
                job_urls.append(tc_job_url)
                self.print_tc_job_url(tc_job_url, tc.id)
        return job_urls

    def get_tc_job_url(self, tc_id: str, job_id: str):
        """
        Create the test case id along with a statically generated URL for submitted job id.
        :param tc_id:
        :param job_id:
        :return:
        """
        tc_job_url = "%s-log?jobId=%s" % (self.config.test_case_url(), job_id)
        return tc_job_url

    def print_tc_job_url(self, tc_job_url: str, tc_id: str):
        """
        Print the statically generated URL for submitted job id.
        :param tc_job_url:
        :param tc_id:
        """
        tc_job_url = "%s (ID: %s)" % (tc_job_url, tc_id)
        LOGGER.info(tc_job_url)
        print(tc_job_url)

    def parse_import_job_data(self, import_job_urls: list):
        """
        Parse relevant part of import job output (UMB messsage reply), which contains critical data:
        test-case-id, name and status if imported test case.
        :param import_job_urls:
        :type import_job_urls:
        :return:
        :rtype:
        """
        for import_job_url in import_job_urls:
            import_successful = False
            out = None
            while not import_successful:
                try:
                    response: Response = requests.get(import_job_url, auth=self.auth, verify=False)
                except RequestException as req_ex:
                    err_msg = "Error getting response from import job: %s" % req_ex
                    LOGGER.error(err_msg)
                    print(err_msg)
                    raise req_ex

                if response.status_code != 200:
                    raise Exception('Error getting import job data from Polarion: %s' % response.content)
                else:
                    out = response.content.decode("UTF-8")
                    if "Ending import of test cases to Polarion" in out:
                        import_successful = True
                    else:
                        # we need to give some time to Polarion, to import test case itself, else we'll get empty data
                        time.sleep(0.5)

            out = out.replace("&#034;", "\"").splitlines()
            msg_content_json = PolarionReporter.parse_message_content(out)

            if msg_content_json['status'] == "passed":
                # construct http://polarion.devel.engineering.redhat.com/polarion/#/project/AMQ/workitem?id=AMQ-94
                polarion_main_url = "/".join(self.config.test_case_url().split("/")[:-2])
                for imp_tc in msg_content_json['import-testcases']:
                    if imp_tc['status'] == "passed":
                        tc_wi_url = "/".join([polarion_main_url, "#", "project", self.testcase.project,
                                              "workitem?id=%s" % imp_tc['id']])
                        LOGGER.debug(tc_wi_url)
                        self.testcase.test_case_work_item_url = tc_wi_url
                    else:
                        raise Exception('Polarion Import error for Testcase %s %s!' % (imp_tc['name'], imp_tc['id']))
            else:
                raise Exception('Polarion Import error for %s!' % import_job_url)

    @staticmethod
    def parse_message_content(out):
        """
        Parse import job output data. We are interested only in UMB message response,
        where status, jobid and test case id is present.

        :param out: whole response content from import job url as text
        :type out: list<str>
        :return: dict as json
        :rtype: dict
        """
        started = False
        json_lines = ""
        for line in out:
            if started:
                json_lines += line
            if "Message Content:" in line:
                started = True
                continue
            if line.startswith("}"):
                started = False
        return json.loads(json_lines)
