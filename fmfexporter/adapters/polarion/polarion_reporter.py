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

import xml.etree.ElementTree as etree
from xml.dom import minidom
from html import escape
from fmfexporter.adapters.polarion.utils.polarion_xml import PolarionXmlUtils


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

        xml_file = {'file': ('testcase.xml', xml)}
        submitted_tc = []

        try:
            response: Response = requests.post(self.config.test_case_url(),
                                               auth=self.auth,
                                               headers=self.headers,
                                               verify=False,
                                               files=xml_file)
        except RequestException as req_ex:
            err_msg = "Error submitting test case: %s" % req_ex
            LOGGER.error(err_msg)
            raise req_ex

        LOGGER.debug("HTTP Response [Code: %s]: %s" % (response.status_code, response.content))

        if response.status_code != 200 or "Project id not specified or invalid" in response.content.decode('utf-8'):
            raise Exception('Error submitting test-case to Polarion: %s' % response.content)
        else:
            submitted_tc.extend(self.handle_response(response, [testcase], parse_response))
        return submitted_tc

    def submit_testcases(self, testcases: list, parse_response=False):
        """
        Submits the given testcases instance to Polarion as ONE file.
        If the given test case already exists (looking up by name as:
        "classname"."name") it will be updated. Created otherwise.
        :param testcases:
        :return:
        """
        xml = PolarionReporter.to_xml(testcases)

        xml_file = {'file': ('testcase.xml', xml)}
        submitted_tc = []
        try:
            response: Response = requests.post(self.config.test_case_url(),
                                     auth=self.auth,
                                     headers=self.headers,
                                     verify=False,
                                     files=xml_file)
        except RequestException as req_ex:
            err_msg = "Error submitting test case: %s" % req_ex
            LOGGER.error(err_msg)
            raise req_ex

        LOGGER.debug("HTTP Response [Code: %s]: %s" % (response.status_code, response.content))

        if response.status_code != 200 or "Project id not specified or invalid" in response.content.decode('utf-8'):
            raise Exception('Error submitting test-case to Polarion: %s' % response.content)
        else:
            submitted_tc.extend(self.handle_response(response, testcases, parse_response))
        return submitted_tc


    def assign_imported_work_item(self, msg_content_json, testcases):
        test_wi_map = {}
        testcase_tuples = [(testcase.id, testcase) for testcase in testcases]

        # construct http://polarion.devel.engineering.redhat.com/polarion/#/project/AMQ/workitem?id=AMQ-94
        polarion_main_url = "/".join(self.config.test_case_url().split("/")[:-2])
        for imp_tc in msg_content_json['import-testcases']:
            if imp_tc['status'] == "passed":
                for tc_tuple in testcase_tuples:
                    if imp_tc['name'] == tc_tuple[0]:
                        tc_wi_url = "/".join([polarion_main_url, "#", "project", tc_tuple[1].project,
                                              "workitem?id=%s" % imp_tc['id']])
                        LOGGER.debug(tc_wi_url)
                        tc_tuple[1].test_case_work_item_url = tc_wi_url
            else:
                raise Exception('Polarion Import error for Testcase %s %s!' % (imp_tc['name'], imp_tc['id']))

        return testcases

    def get_job_urls(self, response: dict):
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
                job_urls.append(self.get_job_url(j))
        return job_urls

    def get_job_url(self, job_id: str):
        """
        Create the test case id along with a statically generated URL for submitted job id.
        :param tc_id:
        :param job_id:
        :return:
        """
        tc_job_url = "%s-log?jobId=%s" % (self.config.test_case_url(), job_id)
        return tc_job_url

    def print_tc_job_urls(self, tc_job_urls: list):
        """
        Print the statically generated URL for submitted job id.
        :param tc_job_url:
        :param tc_id:
        """
        for url in tc_job_urls:
            tc_job_url = "Reporting job url: %s" % (url)
            LOGGER.info(tc_job_url)

    @staticmethod
    def to_xml(polarion_testcase_list: list):
        """
        Returns an XML representation of a Polarion TestCase based
        on current state of this instance.
        :return: str representing the test case xml
        """
        xmltree = etree.ElementTree(element=etree.Element('testcases'))

        # root element - testcases and attributes
        xmlroot = xmltree.getroot()
        xmlroot.attrib['project-id'] = polarion_testcase_list[0].project

        # properties
        properties = etree.SubElement(xmlroot, 'properties')
        PolarionXmlUtils.new_property_sub_element(properties, 'lookup-method', polarion_testcase_list[0].lookup_method)

        for ptc in polarion_testcase_list:
            # testcase and attributes
            tc = etree.SubElement(xmlroot, 'testcase')
            tc.set('assignee-id', ptc.assignee)
            if ptc.approvals:
                tc.set('approver-ids', ",".join([ap + ":approved" for ap in ptc.approvals]))
            tc.set('id', ptc.id)

            # workflow is:
            # - proposed if description, level and importance defined
            # - approved if proposed conditions met, plus:
            #   - automation_script set (when automated)
            #   - requirement with role 'verifies' populated
            if ptc.description != "" and ptc.level != "" and ptc.importance != "":
                ptc.status = "proposed"
                if len(ptc.verifies) > 0 and (ptc.automated == "notautomated" or ptc.automation_script != ""):
                    ptc.status = "approved"
            tc.set('status-id', ptc.status)

            # testcase child elements
            # testcase/title
            tc_title = etree.SubElement(tc, 'title')
            tc_title.text = ptc.title

            # testcase/description
            tc_description = etree.SubElement(tc, 'description')
            tc_description.text = PolarionTestCase.DESC_PREFIX_SUFFIX
            if ptc.description:
                tc_description.text += "<br>"
                tc_description.text += escape(ptc.description).replace('\n', '<br>')
                tc_description.text += "<br>"
                tc_description.text += PolarionTestCase.DESC_PREFIX_SUFFIX

            # testcase/custom-fields
            tc_custom = etree.SubElement(tc, 'custom-fields')
            PolarionXmlUtils.new_custom_field(tc_custom, 'casecomponent', ptc.component)
            PolarionXmlUtils.new_custom_field(tc_custom, 'subcomponent', ptc.sub_component)
            PolarionXmlUtils.new_custom_field(tc_custom, 'testtype', ptc.type)
            PolarionXmlUtils.new_custom_field(tc_custom, 'subtype1', ptc.subtype1)
            PolarionXmlUtils.new_custom_field(tc_custom, 'subtype2', ptc.subtype2)
            PolarionXmlUtils.new_custom_field(tc_custom, 'caselevel', ptc.level)
            PolarionXmlUtils.new_custom_field(tc_custom, 'caseimportance', ptc.importance)
            PolarionXmlUtils.new_custom_field(tc_custom, 'caseposneg', ptc.positive)
            PolarionXmlUtils.new_custom_field(tc_custom, 'caseautomation', ptc.automated)
            PolarionXmlUtils.new_custom_field(tc_custom, 'setup', ptc.create_step_result_table(ptc.setup))
            PolarionXmlUtils.new_custom_field(tc_custom, 'teardown', ptc.create_step_result_table(ptc.teardown))
            PolarionXmlUtils.new_custom_field(tc_custom, 'automation_script', ptc.automation_script)
            PolarionXmlUtils.new_custom_field(tc_custom, 'customerscenario', str(ptc.is_customer_scenario))
            if ptc.tags:
                PolarionXmlUtils.new_custom_field(tc_custom, 'tags', ', '.join(ptc.tags))

            # testcase/linked-work-items
            if ptc.verifies:
                tc_linked = etree.SubElement(tc, 'linked-work-items')
                for verify in [verify for verify in ptc.verifies if isinstance(verify, dict)]:
                    PolarionXmlUtils.new_linked_work_item(tc_linked,
                                                          verify.get('polarion', verify.get('jira', '')),
                                                          'verifies')

            # testcase/test-steps
            if ptc.steps:
                tc_steps = etree.SubElement(tc, 'test-steps')

                # If test case has parameters, add them
                if ptc.parameters:
                    PolarionXmlUtils.new_test_step_params(tc_steps, ptc.parameters)

                for step in ptc.steps:
                    PolarionXmlUtils.new_test_step(tc_steps, step.step, step.result)

            # external links Jira, BZ
            if ptc.defects:
                tc_hyperlinks = etree.SubElement(tc, "hyperlinks")
                for defect in ptc.defects:
                    for key in defect:
                        PolarionXmlUtils.new_hyperlink_sub_element(tc_hyperlinks, "tc_customerdefect", defect[key])
                        # PolarionXmlUtils.new_hyperlink_sub_element(tc_hyperlinks, "testscript", defect[key])

        xml_str = minidom.parseString(etree.tostring(xmlroot)).toprettyxml()

        output_file_name = "testcase.xml"
        LOGGER.info("Generated: %s", output_file_name)
        with open(output_file_name, 'w') as out_file:
            out_file.write(xml_str)
            out_file.close()

        return xml_str

    def parse_import_job_data(self, import_job_url: list, testcases):
        """
        Parse relevant part of import job output (UMB messsage reply), which contains critical data:
        test-case-id, name and status if imported test case.
        :param import_job_urls:
        :type import_job_urls:
        :return:
        :rtype:
        """
        import_successful = False
        out = None
        max_attempts = 120
        attempt = 0
        while not import_successful and attempt < max_attempts:
            attempt += 1
            try:
                response: Response = requests.get(import_job_url, auth=self.auth, verify=False)
            except RequestException as req_ex:
                err_msg = "Error getting response from import job: %s" % req_ex
                LOGGER.error(err_msg)
                raise req_ex

            if response.status_code != 200 or "Project id not specified or invalid" in response.content.decode('utf-8'):
                raise Exception('Error getting import job data from Polarion: %s' % response.content)
            else:
                out = response.content.decode("UTF-8")
                if "Ending import of test cases to Polarion" in out and "Rolling back test case import due to earlier errors" not in out:
                    import_successful = True
                else:
                    # we need to give some time to Polarion, to import test case itself, else we'll get empty data
                    LOGGER.debug("import data not yet available - attempt %d/%d" % (attempt, max_attempts))
                    if attempt == max_attempts:
                        break
                    time.sleep(2)

        out = out.replace("&#034;", "\"").splitlines()
        msg_content_json = PolarionReporter.parse_message_content(out)
        if msg_content_json['status'] == "passed":
            self.assign_imported_work_item(msg_content_json, testcases)
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

    def handle_response(self, response, testcases, parse_response):
        tcs = []
        urls = self.get_job_urls(response.json())
        if len(urls) != 1:
            # We don't track testcase vs import job mapping (multiple import xml files).
            # All testcases submitted by this execution are imported from 1 xml file.
            raise RuntimeError("Error occurred when importing testcase! Multiple job urls found.")

        for testcase in testcases:
            tcs.append(testcase)

        self.print_tc_job_urls(urls)

        if parse_response:
            self.parse_import_job_data(urls, testcases)



        return tcs