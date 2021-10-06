import argparse
import sys

import fmf

from fmfexporter.fmf_adapter import FMFAdapter
from fmfexporter.adapters import *

"""
Common arguments for the fmfexporter tool.
"""


class FMFExporterArgParser(object):
    """
    Common argument parser for fmfexporter tool.
    The arguments defined here must be provided, no matter which
    external adapter is used.
    """

    def __init__(self, *args, **kwargs):

        self._parser = argparse.ArgumentParser(prog='fmfexporter')

        # Common arguments
        adapters = FMFAdapter.get_available_adapters()

        self._parser.add_argument(
            "-p", "--path", required=True, help="FMF Tree path containing your "
            "test cases")
        self._parser.add_argument(
            "--tc", action="append", help="FMF Test Case filter (by name)")
        self._parser.add_argument(
            "--log-level", choices=['WARNING', 'INFO', 'DEBUG'], default='INFO',
            # action='store_true', dest='log_level',
            help="Specify logging level to use")
        self._parser.add_argument(
            "--show-scheme", action='store_true', dest='show_scheme',
            help="Show metadata scheme")

        # Sub-commands from available adapters
        sp = self._parser.add_subparsers(title='Adapter', help='Adapter help', dest='adapter')
        for adapter in adapters:
            parser = sp.add_parser(adapter, add_help=True)
            FMFAdapter.get_adapter_class(adapter).get_args_parser().add_arguments(parser)

        self._parsed_args = None
        self._adapter = None
        self._adapter_parsed_args = None

    def parse_args(self, args=None, namespace=None):
        """
        Parses the common arguments, and invokes the argument parser for the specified adapter.
        :param args:
        :param namespace:
        :return: Parsed arguments
        """
        self._parsed_args = self._parser.parse_args(args, namespace)

        # Give a change for adapter's arg parser
        adapter_parser = FMFAdapter.get_adapter_class(self.parsed_args.adapter).get_args_parser()
        adapter_parser.parse_arguments(self._parsed_args)

        # Validate if parsed arguments are ok
        try:
            self._adapter = FMFAdapter.get_adapter(self._parsed_args.adapter, self._parsed_args.path)
        except fmf.utils.FileError:
            print("Invalid FMF Tree path: %s" % self._parsed_args.path)
            sys.exit(1)

        # Returned parsed args
        return self._parsed_args

    @property
    def parsed_args(self):
        return self._parsed_args

    @property
    def adapter(self):
        return self._adapter
