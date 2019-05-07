from fmfexporter import FMFTestCase
import re
import xml.etree.ElementTree as etree
from xml.dom import minidom
from html import escape
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

        # If authors defined, add them to the description
        if fmf_testcase.authors:
            tc.description += "\n\nAuthors:\n"
            tc.description += "\n".join(fmf_testcase.authors)

        # If approvals defined, add them to the description
        if fmf_testcase.approvals:
            tc.description += "\n\nApprovals:\n"
            tc.description += "\n".join(fmf_testcase.approvals)

        # Set the assignee in case author is defined correctly
        if len(fmf_testcase.authors) > 0:
            author = fmf_testcase.authors[0]
            # Expects author to be according to metadata schema: "Name Surname <email@redhat.com>"
            if re.match(PolarionTestCase.RE_USER_ID, author):
                tc.assignee = re.sub(PolarionTestCase.RE_USER_ID, r'\1', author)

        # Set verifies list
        # TODO Discuss with team about it
        tc.verifies = fmf_testcase.requirements + fmf_testcase.defects

        # TODO Need to research / discuss how to handle it
        tc.status = ''

        # Fields expected inside adapater.polarion
        if fmf_testcase.adapter and 'polarion' in fmf_testcase.adapter:
            polarion: dict = fmf_testcase.adapter.get('polarion')
            tc.project = polarion.get('project')
            tc.positive = 'positive' if polarion.get('positive', False) else 'negative'
            tc.automated = 'automated' if polarion.get('automated', False) else 'notautomated'
            tc.lookup_method = polarion.get('lookup-method', 'name')
            subtypes = polarion.get('subtypes', [])
            tc.subtype1 = subtypes[0] if len(subtypes) >= 1 else ''
            tc.subtype2 = subtypes[1] if len(subtypes) >= 2 else ''

        # Component
        tc.component = ''
        if fmf_testcase.components:
            if isinstance(fmf_testcase.components, list):
                tc.component = fmf_testcase.components[0]
            else:
                tc.component = fmf_testcase.components

        # Sub Component
        tc.sub_component = ''
        if fmf_testcase.sub_components:
            if isinstance(fmf_testcase.sub_components, list):
                tc.sub_component = fmf_testcase.sub_components[0]
            else:
                tc.sub_component = fmf_testcase.sub_components

        # Level and types
        tc.level = fmf_testcase.level
        tc.type = fmf_testcase.type

        # Importance
        tc.importance = fmf_testcase.importance

        # Parameters
        tc.parameters = fmf_testcase.parameters

        # Setup
        for fmf_setup_step in fmf_testcase.test_setup:
            tc.setup.append(PolarionTestCase.Step(fmf_setup_step['step'], fmf_setup_step['expected']))

        # Teardown
        for fmf_teardown_step in fmf_testcase.test_teardown:
            tc.teardown.append(PolarionTestCase.Step(fmf_teardown_step['step'], fmf_teardown_step['expected']))

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
        self.component = ""
        self.sub_component = ""
        self.type = ""
        self.level = ""
        self.importance = ""
        self.setup = []
        self.teardown = []
        self.steps = []
        self.approvals = []
        self.subtype1 = ""
        self.subtype2 = ""
        self.parameters = []

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
            tc_description.text += escape(self.description).replace('\n', '<br>')
            tc_description.text += "<br>"
            tc_description.text += PolarionTestCase.DESC_PREFIX_SUFFIX

        # testcase/custom-fields
        tc_custom = etree.SubElement(tc, 'custom-fields')
        PolarionXmlUtils.new_custom_field(tc_custom, 'casecomponent', self.component)
        PolarionXmlUtils.new_custom_field(tc_custom, 'subcomponent', self.sub_component)
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
            for verify in [verify for verify in self.verifies if isinstance(verify, dict)]:
                PolarionXmlUtils.new_linked_work_item(tc_linked,
                                                      verify.get('polarion', verify.get('jira', '')),
                                                      'verifies')

        # testcase/test-steps
        if self.steps or self.setup or self.teardown:
            tc_steps = etree.SubElement(tc, 'test-steps')

            for step in self.setup:
                PolarionXmlUtils.new_test_step(tc_steps, "(setup) #. {}".format(step.step), step.result)

            for step in self.teardown:
                PolarionXmlUtils.new_test_step(tc_steps, "(teardown) #. {}".format(step.step), step.result)

            # If test case has parameters, add them
            if self.parameters:
                PolarionXmlUtils.new_test_step_params(tc_steps, self.parameters)

            for step in self.steps:
                PolarionXmlUtils.new_test_step(tc_steps, step.step, step.result)

        xml_str = minidom.parseString(etree.tostring(xmlroot)).toprettyxml()

        return xml_str
