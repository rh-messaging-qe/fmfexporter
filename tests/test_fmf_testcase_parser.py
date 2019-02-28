import os
import pytest

from fmfexporter import FMFTestCase
from fmfexporter.fmf_adapter import FMFAdapterTest


"""
Validates if FMF Test Cases are being parsed as expected.
"""


@pytest.fixture(scope="module")
def testcase() -> FMFTestCase:
    """
    Generate a testcase fixture containing a static test case.
    :return:
    """
    fmf_adapter = FMFAdapterTest(os.path.dirname(os.path.abspath(__file__)))
    tc = fmf_adapter.get_testcase('test_path.some_test_class.foo_test.TestFoo',
                                  'test_foo_sample_01')
    return tc


def test_fmftestcase_parser_test_identification(testcase):
    """
    Asserts the FMF test case identification elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert testcase.name == "/test_path/some_test_class/foo_test/TestFoo/test_foo_sample_01"
    assert testcase.summary == "This is the summary"
    assert testcase.description == "This is the description"
    assert "TAG1" in testcase.tags
    assert len(testcase.tags) == 1


def test_fmftestcase_parser_test_authoring(testcase):
    """
    Asserts the FMF test case authoring elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert "Fernando Giorgetti <fgiorget@redhat.com>" in testcase.authors
    assert len(testcase.authors) == 1

    assert "Fernando Giorgetti <fgiorget@redhat.com>" in testcase.approvals
    assert "Dominik Lenoch <dlenoch@redhat.com>" in testcase.approvals
    assert len(testcase.approvals) == 2


def test_fmftestcase_parser_test_component(testcase):
    """
    Asserts the FMF test case components and sub_components elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert "router" in testcase.components
    assert len(testcase.components) == 1

    assert "Core_Engine" in testcase.sub_components
    assert len(testcase.sub_components) == 1


def test_fmftestcase_parser_test_priorities(testcase):
    """
    Asserts the FMF test case priority related elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert testcase.importance == "critical"
    assert testcase.estimate == "40h"


def test_fmftestcase_parser_test_level_type(testcase):
    """
    Asserts the FMF test case level and type elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert testcase.level == "component"
    assert testcase.type == "functional"


def test_fmftestcase_parser_test_relationships(testcase):
    """
    Asserts the FMF test case relationship elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    defects = [{'polarion': 'ENTMQIC-1111', 'customer-case': True}, {'jira': 'ENTMQIC-2222'}]
    assert defects[0] in testcase.defects
    assert defects[1] in testcase.defects
    assert len(testcase.defects) == 2

    requirements = [{'polarion': 'ENTMQIC-3333', 'customer-case': True}, {'jira': 'ENTMQIC-4444'}]
    assert requirements[0] in testcase.requirements
    assert requirements[1] in testcase.requirements
    assert len(testcase.requirements) == 2


def test_fmftestcase_parser_test_steps(testcase: FMFTestCase):
    """
    Asserts the FMF test case step elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    exp_steps = [
        {"step": "Step 1", "expected": "Expected 1"},
        {"step": "Step 2", "expected": "Expected 2"},
    ]

    assert exp_steps[0] in testcase.test_steps
    assert exp_steps[1] in testcase.test_steps
    assert len(testcase.test_steps) == 2


def test_fmftestcase_parser_test_parameters(testcase):
    """
    Asserts the FMF test case parameters element is properly parsed from YAML
    :param testcase:
    :return:
    """
    exp_parameters = ["router", "broker", "client"]
    for exp_param in exp_parameters:
        assert exp_param in testcase.parameters
    assert len(exp_parameters) == len(testcase.parameters)


def test_fmftestcase_parser_test_testsuite(testcase: FMFTestCase):
    """
    Asserts the FMF testsuite element has been properly parsed from YAML
    :param testcase:
    :return:
    """
    exp_parameters = ['PARAM1', 'PARAM2']
    exp_properties = {
        'property1': 'value1',
        'property2': 'value2'
    }
    exp_topologies = ['TOPO1', 'TOPO2']

    assert exp_parameters == testcase.testsuite.parameters
    assert exp_properties == testcase.testsuite.properties
    assert exp_topologies == testcase.testsuite.compatible_topologies
