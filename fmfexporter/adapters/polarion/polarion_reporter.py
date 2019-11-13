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

    def submit_testcases(self, testcases: list[PolarionTestCase]):
        """
        Submits the given testcase instance to Polarion.
        If the given test case already exists (looking up by name as:
        "classname"."name") it will be updated. Created otherwise.
        :param testcases:
        :return:
        """

        xml = self.to_xml(testcases)
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
            for testcase in testcases:
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

    def to_xml(self, polarion_testcase_list: list[PolarionTestCase]):
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

        return xml_str
