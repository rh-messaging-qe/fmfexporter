import abc
import os
import re
import logging
import argparse
import fmf
from typing import List

from fmfexporter.fmf_testcase import FMFTestCase


"""
Provides the generic classes used to represent an Adapter.
Adapters must be ALM related tools that can be used to store
Test Cases metadata.
"""

LOGGER = logging.getLogger(__name__)


class FMFAdapterArgParser(abc.ABC, object):
    """
    Argument parser Interface that defines the behaviors that
    must be provided by concrete argument parsers for external adapters.
    """
    @abc.abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        An ArgumentParser is passed and must be populated with
        adapter specific arguments.
        :param parser:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def parse_arguments(self, parsed_arguments: argparse.Namespace):
        """
        Hook method that will be invoked when arguments have been parsed,
        so adapter arguments can be properly validated.
        :param parsed_arguments:
        :return:
        """
        raise NotImplementedError()


class FMFAdapter(abc.ABC, object):
    """
    Abstract FMF Adapter class that defines the generic behaviors and
    the abstract behaviors that must be implemented by the external
    FMF Adapter implementations.
    """

    def __init__(self, fmf_tree_path: str = '.'):
        self._cur_path = os.path.abspath(fmf_tree_path)
        self._tree = fmf.Tree(self._cur_path)

    @staticmethod
    @abc.abstractmethod
    def adapter_id() -> str:
        """
        Concrete adapters must return a unique id (no spaces) to represent it.
        It will be used in command line arguments as the adapter id.
        :return:
        """
        raise NotImplementedError()

    @staticmethod
    @abc.abstractmethod
    def get_args_parser() -> FMFAdapterArgParser:
        """
        Return an FMFAdapterArgParser that adds extra arguments
        for parsing options related with external system.
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def convert_from(self, fmf_testcase: FMFTestCase):
        """
        Concrete adapters must be able to convert from FMFTestCase
        and return their specialized version of a test case.
        :param fmf_testcase:
        :return: Adapter object that represents a test case
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def submit_testcase(self, fmf_testcase: FMFTestCase):
        """
        This method is used to submit a generic FMFTestCase element
        into the external ALM related tool.
        :param fmf_testcase:
        :return:
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def submit_testcases(self, fmf_testcases: list):
        """
        This method is used to submit a list of generic FMFTestCase element
        into the external ALM related tool.
        :param fmf_testcases:
        :return:
        """
        raise NotImplementedError()

    @staticmethod
    def get_adapter(adapter_id: str, fmf_tree_path: str):
        """
        Returns an instance of an adapter based on its unique ID.
        The fmf_tree_path is also mandatory in the initialization.
        :param adapter_id:
        :param fmf_tree_path:
        :return:
        """
        adapter_class = FMFAdapter.get_adapter_class(adapter_id)
        return adapter_class(fmf_tree_path)

    @staticmethod
    def get_adapter_class(adapter_id: str):
        """
        Returns the concrete FMFAdapter class based on the unique ID.
        :param adapter_id:
        :return:
        """
        for sc in FMFAdapter.__subclasses__():
            if sc.adapter_id() == adapter_id:
                return sc
        # Should not happen if invoked from arg parser
        raise ValueError("Invalid Adapter ID")

    @staticmethod
    def get_available_adapters():
        """
        Return adapter id of each subclass of FMFAdapter
        :return:
        """
        return [sc.adapter_id() for sc in FMFAdapter.__subclasses__() if sc.adapter_id() != 'test']

    def convert_from_list(self, fmf_testcase_list: List[FMFTestCase]):
        """
        Convert list of FMFTestCase objects into a list of test cases
        based on Adapter's customized version of an FMFTestCase.
        :param fmf_testcase_list:
        :return: list
        """
        tc_list = []
        for tc in fmf_testcase_list:
            tc_list.append(self.convert_from(tc))
        return tc_list

    @staticmethod
    def _get_name_in_tree(classname: str, testname: str):
        """
        Internal method that converts a combination of "classname.testname"
        into an FMF Tree path (which is used internally as FMF Test Case name).
        :param classname:
        :param testname:
        :return:
        """

        # Name in tree will be composed by classname"/"testname
        # and eventual parameters (usually defined as '[param1-param2]' must
        # be removed.
        name_in_tree = "/{}/{}".format(classname.replace('.', '/'),
                                       re.sub('\\[.*', '', testname))
        return name_in_tree

    def get_testcase(self, classname: str, testname: str) -> FMFTestCase:
        """
        Returns an FMFTestCase object based on provided "classname.testname".
        :param classname:
        :param testname:
        :return:
        """
        name_in_tree = self._get_name_in_tree(classname, testname)
        node = self._tree.find(name_in_tree)
        if node:
            return FMFTestCase.from_fmf_testcase_node(node)

        return None

    def get_testcases_matching(self, name: str):
        """
        Returns a list of FMFTestCase elements whose provided name argument
        is contained in any part of the "FMFTestCase.name" property.
        :param name:
        :return:
        """
        nodes = []

        for node in self._tree.climb():
            if not name or name in node.name:
                nodes.append(FMFTestCase.from_fmf_testcase_node(node))

        return nodes


class FMFAdapterTest(FMFAdapter):
    """
    Dummy implementation just for unit tests.
    """

    @staticmethod
    def adapter_id() -> str:
        return "test"

    @staticmethod
    def get_args_parser() -> FMFAdapterArgParser:
        pass

    def convert_from(self, fmf_testcase: FMFTestCase):
        pass

    def submit_testcase(self, fmf_testcase: FMFTestCase):
        pass

    def submit_testcases(self, fmf_testcase: list):
        pass
