from typing import Union, List

from fmf import Tree

"""
Provides FMF TestCase related classes.
"""


class FMFTestSuite(dict):
    """
    Dictionary with properties to access currently supported (and documented) keys.
    """
    def __init__(self, *args, **kwargs):
        super(FMFTestSuite, self).__init__(*args, **kwargs)

    @property
    def parameters(self) -> list:
        return self.get('parameters', [])

    @property
    def properties(self) -> dict:
        return self.get('properties', {})

    @property
    def compatible_topologies(self) -> list:
        return self.get('compatible_topologies', self.get('compatible-topologies', []))


class FMFTestCaseRelationship(dict):
    """
    Dictionary with properties exposing currently supported (and documented) keys.
    """
    def __init__(self, *args, **kwargs):
        super(FMFTestCaseRelationship, self).__init__(*args, **kwargs)

    @property
    def jira(self) -> str:
        return self.get('jira', '')

    @property
    def bugzilla(self) -> str:
        return self.get('bugzilla', '')

    @property
    def customer_case(self) -> bool:
        return self.get('customer-case', False)


class FMFTestCase(object):
    """
    FMFTestCase is used to represent a test case metadata,
    defined in YAML using an internal FMF test case schema.
    """
    def __init__(self):

        # TC Identification
        self.name: str = ""
        self.summary: str = ""
        self.description: str = ""
        self.tags: list = []

        # Authoring and approvals
        self.authors: list = []
        self.approvals: list = []

        # Classification
        self.type: str = ""
        self.subtypes: list = []
        self.level: str = ""

        # Components
        self.components: Union[list, str] = ""
        self.sub_components: Union[list, str] = ""

        # Importance / priority
        self.importance: str = ""
        self.estimate: str = ""

        # Relationships
        self.defects: List[FMFTestCaseRelationship] = []
        self.requirements: List[FMFTestCaseRelationship] = []

        # Setup
        self.test_setup = []

        # Teardown
        self.test_teardown = []

        # Steps
        self.test_steps = []

        # Test Case parameters
        self.parameters = []

        # Test suite
        self.testsuite: FMFTestSuite = FMFTestSuite()

        # Adapter
        self.adapter: dict = {}

    @staticmethod
    def from_fmf_testcase_node(fmf_node: Tree):
        """
        This method is used to create an instance of an FMFTestCase based on a given node in the FMF Tree.
        :param fmf_node:
        :return: FMFTestCase instance
        """

        def get_fmf_data(node, data, _default):
            """
            Returns the value for the given data (key) or a default value
            :param node:
            :param data:
            :param _default:
            :return:
            """
            if data not in node.data:
                return _default
            return node.data[data]

        fmf_tc = FMFTestCase()

        try:
            # TC Identification
            fmf_tc.name = fmf_node.name
            fmf_tc.summary = get_fmf_data(fmf_node, 'summary', '')
            fmf_tc.description = get_fmf_data(fmf_node, 'description', '')
            fmf_tc.tags = get_fmf_data(fmf_node, 'tags', [])

            # Authoring and approvals
            fmf_tc.authors = get_fmf_data(fmf_node, 'authors', [])
            fmf_tc.approvals = get_fmf_data(fmf_node, 'approvals', [])

            # Classification
            fmf_tc.type = get_fmf_data(fmf_node, 'type', '')
            fmf_tc.subtypes = get_fmf_data(fmf_node, 'subtypes', [])
            fmf_tc.level = get_fmf_data(fmf_node, 'level', '')

            # Components
            fmf_tc.components = get_fmf_data(fmf_node, 'components', '')
            fmf_tc.sub_components = get_fmf_data(fmf_node, 'subcomponents', '')

            # Importance / priority
            fmf_tc.importance = get_fmf_data(fmf_node, 'importance', '')
            fmf_tc.estimate = get_fmf_data(fmf_node, 'estimate', '')

            # Relationships
            fmf_tc.defects = [FMFTestCaseRelationship(defect) for defect in get_fmf_data(fmf_node, 'defects', [])]
            fmf_tc.requirements = [FMFTestCaseRelationship(req) for req in get_fmf_data(fmf_node, 'requirements', [])]

            # Setup
            fmf_tc.test_setup = get_fmf_data(fmf_node, 'test-setup', [])

            # Teardown
            fmf_tc.test_teardown = get_fmf_data(fmf_node, 'test-teardown', [])

            # Steps
            fmf_tc.test_steps = get_fmf_data(fmf_node, 'test-steps', [])

            # Test Case parameters
            fmf_tc.parameters = get_fmf_data(fmf_node, 'parameters', [])

            # Test Suite parameters
            ts = get_fmf_data(fmf_node, 'testsuite', {})
            fmf_tc.testsuite = FMFTestSuite(**ts)

            # Adapter specific info
            fmf_tc.adapter = get_fmf_data(fmf_node, 'adapter', {})

            return fmf_tc
        except Exception as e:
            print("Unable to parse FMF test case: %s" % str(e))
            raise e
