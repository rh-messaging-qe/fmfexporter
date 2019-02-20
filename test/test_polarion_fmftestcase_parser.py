import pytest
import os
from fmfexporter.adapters.polarion.polarion_test_case import PolarionTestCase
from fmfexporter.adapters.polarion.fmf_adapter_polarion import FMFAdapterPolarion

"""
Ensures that a generic FMF Test Case is being converted into a
Polarion Test Case properly.
"""


@pytest.fixture(scope="module")
def testcase(request):
    """
    Creates a testcase fixture which is an instance of a PolarionTestCase class,
    and it is created from a generic FMF Test Case metadata.
    :param request:
    :return:
    """
    fmf_adapter = FMFAdapterPolarion(os.path.dirname(os.path.abspath(__file__)))
    tc = fmf_adapter.get_testcase('test_path.some_test_class.foo_test.TestFoo', 'test_foo_sample_01')
    ptc = PolarionTestCase.from_fmf_testcase(tc)
    return ptc


def test_polarion_fmftestcase_parser_id(testcase):
    """
    Asserts that the Polarion Test Case identification is mapped correctly from an FMF Test Case
    :param testcase:
    :return:
    """
    assert testcase.id == 'test_path.some_test_class.foo_test.TestFoo.test_foo_sample_01'
    assert testcase.title == testcase.id
    assert testcase.description == 'This is the summary\nThis is the description'


def test_polarion_fmftestcase_parser_authoring(testcase):
    """
    Asserts that the Polarion Test Case authoring is mapped correctly from an FMF Test Case
    :param testcase:
    :return:
    """
    assert testcase.assignee == 'fgiorget'
    assert 'fgiorget' in testcase.approvals
    assert 'dlenoch' in testcase.approvals
    assert len(testcase.approvals) == 2


def test_polarion_fmftestcase_parser_relationship(testcase):
    """
    Asserts that the Polarion Test Case verifies elements are mapped correctly from an FMF Test Case
    TODO Probably need to be split into other fields for Polarion. Currently everything becomes "verifies".
    :param testcase:
    :return:
    """
    verify_list = [{'jira': 'ENTMQIC-1111', 'customer-case': True}, {'jira': 'ENTMQIC-2222'},
                   {'jira': 'ENTMQIC-3333', 'customer-case': True}, {'jira': 'ENTMQIC-4444'}]

    assert all(item in testcase.verifies for item in verify_list)
    assert len(verify_list) == len(testcase.verifies)


def test_polarion_fmftestcase_parser_components(testcase):
    """
    Asserts that the Polarion Test Case component is mapped correctly from an FMF Test Case
    :param testcase:
    :return:
    """
    assert testcase.component == 'router'
    assert testcase.sub_component == 'Core_Engine'


def test_polarion_fmftestcase_parser_level_and_type(testcase):
    """
    Asserts that the Polarion Test Case level and types are mapped correctly from an FMF Test Case
    :param testcase:
    :return:
    """
    assert testcase.level == 'component'
    assert testcase.type == 'functional'


def test_polarion_fmftestcase_parser_importance(testcase):
    """
    Asserts that the Polarion Test Case importance is mapped correctly from an FMF Test Case
    :param testcase:
    :return:
    """
    assert testcase.importance == 'critical'


def test_polarion_fmftestcase_parser_steps(testcase):
    """
    Asserts that the Polarion Test Case steps elements are mapped correctly from an FMF Test Case
    :param testcase:
    :return:
    """

    steps = [PolarionTestCase.Step('Step 1', 'Expected 1'),
             PolarionTestCase.Step('Step 2', 'Expected 2')]

    for i in range(len(steps)):
        assert steps[i].step == testcase.steps[i].step
        assert steps[i].result == testcase.steps[i].result

    assert len(testcase.steps) == 2


def test_polarion_fmftestcase_parser_custom_parameters(testcase):
    """
    Asserts that the Polarion Test Case custom parameters are mapped correctly from an FMF Test Case
    :param testcase:
    :return:
    """
    assert testcase.project == 'ENTMQIC'
    assert testcase.status == ''  # TODO Need to define how to handle it
    assert testcase.positive == 'positive'
    assert testcase.automated == 'automated'
    assert testcase.lookup_method == 'name'
    assert testcase.subtype1 == 'compliance'
    assert testcase.subtype2 == '-'
