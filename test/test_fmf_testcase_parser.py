import os
import pytest
from fmfexporter.fmf_adapter import FMFAdapterTest


"""
Validates if FMF Test Cases are being parsed as expected.
"""

@pytest.fixture(scope="module")
def testcase(request):
    """
    Generate a testcase fixture containing a static test case.
    :param request:
    :return:
    """
    fmf_adapter = FMFAdapterTest(os.path.dirname(os.path.abspath(__file__)))
    tc = fmf_adapter.get_testcase('test_path.some_test_class.foo_test.TestFoo', 'test_foo_sample_01')
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
    Asserts the FMF test case components and subcomponents elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert "router" in testcase.components
    assert len(testcase.components) == 1

    assert "Core_Engine" in testcase.subcomponents
    assert len(testcase.subcomponents) == 1


def test_fmftestcase_parser_test_importance(testcase):
    """
    Asserts the FMF test case importance element is properly parsed from YAML
    :param testcase:
    :return:
    """
    assert testcase.importance == "critical"


def test_fmftestcase_parser_test_level_type(testcase):
    """
    Asserts the FMF test case level and type elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert testcase.level == "component"
    assert testcase.type == "functional"

    assert 'compliance' in testcase.subtypes
    assert '-' in testcase.subtypes
    assert len(testcase.subtypes) == 2


def test_fmftestcase_parser_test_relationships(testcase):
    """
    Asserts the FMF test case relationship elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    assert 'ENTMQIC-1111' in testcase.defects
    assert 'ENTMQIC-2222' in testcase.defects
    assert len(testcase.defects) == 2

    assert 'ENTMQIC-3333' in testcase.requirements
    assert 'ENTMQIC-4444' in testcase.requirements
    assert len(testcase.requirements) == 2

    assert 'ENTMQIC-5555' in testcase.customer_scenarios
    assert 'ENTMQIC-6666' in testcase.customer_scenarios
    assert len(testcase.customer_scenarios) == 2


def test_fmftestcase_parser_test_steps(testcase):
    """
    Asserts the FMF test case step elements are properly parsed from YAML
    :param testcase:
    :return:
    """
    exp_steps = [
        {"step": "Step 1", "expected": "Expected 1"},
        {"step": "Step 2", "expected": "Expected 2"},
    ]
    cur_step = 0
    for step_item in exp_steps:
        assert testcase.test_steps[cur_step]["step"] == step_item["step"]
        assert testcase.test_steps[cur_step]["expected"] == step_item["expected"]
        cur_step += 1
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


def test_fmftestcase_parser_test_testsuite_parameters(testcase):
    """
    Asserts the FMF testsuite.parameters elements are properly parsed from YAML
    TODO Discuss if this is really the right place to store it and if we should rename and make it a dict
    :param testcase:
    :return:
    """
    ts_parameters = {
        "polarion-project-id": "ENTMQIC",
        "polarion-lookup-method": "name"
    }
    for ts_param in testcase.testsuite_parameters:
        for (k, v) in ts_param.items():
            assert ts_parameters[k] == v
    assert len(ts_parameters.items()) == len(testcase.testsuite_parameters)
