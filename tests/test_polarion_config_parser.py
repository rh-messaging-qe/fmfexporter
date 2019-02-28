import pytest
import os
from fmfexporter.adapters.polarion.utils.polarion_config import PolarionConfig

"""
Test if configuration file needed by Polarion adapter is being properly parsed.
"""


@pytest.fixture(scope="module")
def polarion_config():
    """
    Creates a polarion_config fixture based on a pre-populated config file for the
    Polarion adapter.
    :return:
    """
    return PolarionConfig(os.path.dirname(os.path.abspath(__file__)) + '/fmfexporter.config.ini')


def test_polarion_config_parser(polarion_config):
    """
    Asserts that the polarion adapter configuration keys and values have been
    parsed correctly.
    :param polarion_config:
    :return:
    """
    assert polarion_config.test_case_url() == 'https://127.0.0.1/polarion/import/testcase'
    assert polarion_config.test_run_url() == 'https://127.0.0.1/polarion/import/xunit'
    assert polarion_config.username() == 'my_user'
    assert polarion_config.password() == 'my_pass'
