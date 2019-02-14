from fmfexporter import FMFTestCase
import re
import xml.etree.ElementTree as etree
from xml.dom import minidom

from fmfexporter.adapters.polarion.utils.polarion_xml import PolarionXmlUtils
"""
Representation of a Polarion Test Case XML.
"""


class PolarionTestCase(object):
    """
    Represents the data that must be added to a Test Case workitem before
    submitting to the Polarion importer.
    """
    # Used to define file name for test case based on
    # classname.name (keeping just characters, numbers and dot)
    RE_FILE_NAME = re.compile(r'[^A-Za-z0-9_\.]')

    #
    # Regular expression used to match user part of an e-mail address
    # matching the authors schema.
    #
    RE_USER_ID = re.compile(r'.*<(.*)@.*')

    #
    # Test Case Constants
    #
    DESC_PREFIX_SUFFIX = "-- DO NOT EDIT THROUGH THE POLARION UI --"

    @staticmethod
    def from_fmf_testcase(fmf_testcase: FMFTestCase):
        """
        Creates an instance of PolarionTestCase based on the
        provided FMFTestCase object.
        :param fmf_testcase:
        :return:
        """

        tc = PolarionTestCase()

        # Identification
        tc.id = fmf_testcase.name.replace('/', '.')[1:]
        tc.title = tc.id
        tc.description = "%s\n%s" % (fmf_testcase.summary, fmf_testcase.description)

        # Set the assignee in case author is defined correctly
        if len(fmf_testcase.authors) > 0:
            author = fmf_testcase.authors[0]
            # Expects author to be according to metadata schema: "Name Surname <email@redhat.com>"
            if re.match(PolarionTestCase.RE_USER_ID, author):
                tc.assignee = re.sub(PolarionTestCase.RE_USER_ID, r'\1', author)

        # Set verifies list
        # TODO Discuss about it
        tc.verifies = fmf_testcase.requirements + fmf_testcase.defects + fmf_testcase.customer_scenarios
        # tc.verifies = fmf_testcase.requirements

        # TODO Need to discuss how to handle other fields (for now keeping in testsuite_parameters)
        # TODO Convert testsuite parameters into a single dictionary instead of a list?
        tc.project = fmf_testcase.get_testsuite_parameter('polarion-project-id')
        tc.status = ''  # TODO how to handle it?
        tc.positive = fmf_testcase.get_testsuite_parameter('polarion-testcase-positive', 'positive')
        tc.automated = fmf_testcase.get_testsuite_parameter('polarion-testcase-automated', 'automated')
        tc.lookup_method = fmf_testcase.get_testsuite_parameter('polarion-testcase-lookup-method', 'name')

        # Component
        tc.component = fmf_testcase.components[0] if fmf_testcase.components else ''

        # Level and types
        tc.level = fmf_testcase.level
        tc.type = fmf_testcase.type
        tc.subtype1 = fmf_testcase.subtypes[0] if fmf_testcase.subtypes else ''
        tc.subtype2 = fmf_testcase.subtypes[1] if fmf_testcase.subtypes and len(fmf_testcase.subtypes) > 1 else ''

        # Importance
        tc.importance = fmf_testcase.importance

        # Steps
        for fmf_step in fmf_testcase.test_steps:
            tc.steps.append(PolarionTestCase.Step(fmf_step['step'], fmf_step['expected']))

        # Approvals
        for approver in fmf_testcase.approvals:
            # Expects approver to be according to metadata schema: "Name Surname <email@redhat.com>"
            if not re.match(PolarionTestCase.RE_USER_ID, approver):
                continue
            tc.approvals.append(re.sub(PolarionTestCase.RE_USER_ID, r'\1', approver))

        # Tags
        tc.tags = fmf_testcase.tags

        return tc

    class Step(object):
        """
        Represent the step and expected result
        """

        def __init__(self, step, result):
            self._step = step
            self._result = result

        @property
        def step(self):
            return self._step

        @property
        def result(self):
            return self._result

    class Environment(object):
        """
        Represents a test-case environment
        """

        def __init__(self):
            # server, workstation, client
            self.variant = ""
            # i386, x86_64, ppc64, s390x, ia64
            self.arch = ""

    def __init__(self):
        self.id = ""
        self.title = ""
        self.description = ""
        self.project = ""
        self.status = ""
        self.assignee = ""
        self.verifies = ""
        self.positive = "positive"
        self.automated = "notautomated"
        self.lookup_method = ""

        # router = Qpid Dispatch Router
        # currently accepting only: -, comp1, comp2 and router (in devel)
        self.component = ""
        # functional, non-functional, structural
        self.type = ""
        # component, integration, system, acceptance
        self.level = ""
        # low, medium, high, critial
        self.importance = ""

        self.steps = []
        self.approvals = []

        # -, compliance, documentation, i18n, installability, interoperability,
        # performance, reliability, scalability,
        # security, usability, recovery-failover
        self.subtype1 = "-"
        # -, fips, 508, common criteria, whql, user guide, help, load, stress
        self.subtype2 = "-"

        # TODO future use
        self.tags = ""
        self.environment = PolarionTestCase.Environment()

    def to_xml(self):
        """
        Returns an XML representation of a Polarion TestCase based
        on current state of this instance.
        :return: str representing the test case xml
        """
        xmltree = etree.ElementTree(element=etree.Element('testcases'))

        # root element - testcases and attributes
        xmlroot = xmltree.getroot()
        xmlroot.attrib['project-id'] = self.project

        # properties
        properties = etree.SubElement(xmlroot, 'properties')
        PolarionXmlUtils.new_property_sub_element(properties, 'lookup-method', self.lookup_method)

        # testcase and attributes
        tc = etree.SubElement(xmlroot, 'testcase')
        tc.set('assignee-id', self.assignee)
        if self.approvals:
            tc.set('approver-ids', ",".join([ap + ":approved" for ap in self.approvals]))
        tc.set('id', self.id)
        # tc.set('status', self.status)

        # testcase child elements
        # testcase/title
        tc_title = etree.SubElement(tc, 'title')
        tc_title.text = self.title

        # testcase/description
        tc_description = etree.SubElement(tc, 'description')
        tc_description.text = PolarionTestCase.DESC_PREFIX_SUFFIX
        if self.description:
            tc_description.text += "<br>"
            tc_description.text += self.description
            tc_description.text += "<br>"
            tc_description.text += PolarionTestCase.DESC_PREFIX_SUFFIX

        # testcase/custom-fields
        tc_custom = etree.SubElement(tc, 'custom-fields')
        PolarionXmlUtils.new_custom_field(tc_custom, 'casecomponent', self.component)
        PolarionXmlUtils.new_custom_field(tc_custom, 'testtype', self.type)
        PolarionXmlUtils.new_custom_field(tc_custom, 'subtype1', self.subtype1)
        PolarionXmlUtils.new_custom_field(tc_custom, 'subtype2', self.subtype2)
        PolarionXmlUtils.new_custom_field(tc_custom, 'caselevel', self.level)
        PolarionXmlUtils.new_custom_field(tc_custom, 'caseimportance', self.importance)
        PolarionXmlUtils.new_custom_field(tc_custom, 'caseposneg', self.positive)
        PolarionXmlUtils.new_custom_field(tc_custom, 'caseautomation', self.automated)

        # testcase/linked-work-items
        if self.verifies:
            tc_linked = etree.SubElement(tc, 'linked-work-items')
            PolarionXmlUtils.new_linked_verifies(tc_linked, self.verifies)

        # testcase/test-steps
        if self.steps:
            tc_steps = etree.SubElement(tc, 'test-steps')
            for step in self.steps:
                PolarionXmlUtils.new_test_step(tc_steps, step.step, step.result)

        xml_str = minidom.parseString(etree.tostring(xmlroot)).toprettyxml()

        return xml_str
