from fmf import Tree

"""
Provides FMF TestCase related classes.
"""


class FMFTestCase(object):
    """
    FMFTestCase is used to represent a test case metadata,
    defined in YAML using an internal FMF test case schema.
    """
    def __init__(self):

        # TC Identification
        self.name = ""
        self.summary = ""
        self.description = ""
        self.tags = []

        # Authoring and approvals
        self.authors = []
        self.approvals = []

        # Classification
        self.type = ""
        self.subtype = ""
        self.subtypes = []
        self.level = ""

        # Components
        self.components = []
        self.subcomponents = []

        # Importance / priority
        self.importance = ""

        # Relationships
        self.defects = []
        self.requirements = []
        self.customer_scenarios = []

        # Steps
        self.test_steps = []

        # Test Case and Test suite parameters
        self.parameters = []
        self.testsuite_parameters = []

    def get_testsuite_parameter(self, name, _default=''):
        """
        Returns a parameter from the testsuite_parameters.
        TODO it currently holds a list of single dictionaries. We should evaluate adding such parameters to another field
        :param name:
        :param _default:
        :return:
        """
        for param in self.testsuite_parameters:
            if not isinstance(param, dict):
                continue
            for key, value in param.items():
                if key == name:
                    return value
        return _default

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
            fmf_tc.subtype = get_fmf_data(fmf_node, 'subtype', '')
            fmf_tc.subtypes = get_fmf_data(fmf_node, 'subtypes', [])

            fmf_tc.level = get_fmf_data(fmf_node, 'level', '')

            # Components
            fmf_tc.components = get_fmf_data(fmf_node, 'components', [])
            fmf_tc.subcomponents = get_fmf_data(fmf_node, 'subcomponents', [])

            # Importance / priority
            fmf_tc.importance = get_fmf_data(fmf_node, 'importance', '')

            # Relationships
            fmf_tc.defects = get_fmf_data(fmf_node, 'defects', [])
            fmf_tc.requirements = get_fmf_data(fmf_node, 'requirements', [])
            fmf_tc.customer_scenarios = get_fmf_data(fmf_node, 'customer-scenarios', [])

            # Steps
            fmf_tc.test_steps = get_fmf_data(fmf_node, 'test-steps', [])

            # Test Case parameters
            fmf_tc.parameters = get_fmf_data(fmf_node, 'parameters', [])

            # Test Suite parameters
            ts = get_fmf_data(fmf_node, 'testsuite', [])
            fmf_tc.testsuite_parameters = ts['parameters'] if 'parameters' in ts else []

            return fmf_tc
        except Exception as e:
            return None
