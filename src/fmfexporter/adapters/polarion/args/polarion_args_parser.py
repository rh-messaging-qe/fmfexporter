import argparse
import os
import sys

from fmfexporter.adapters.polarion.utils.polarion_config import PolarionConfig
from fmfexporter.fmf_adapter import FMFAdapterArgParser

"""
Argument parser for the FMF Polarion Adapter.
"""


class PolarionArgParser(FMFAdapterArgParser):
    """
    Argument parser that is used when polarion adapter is selected.
    """

    # Once configured properly, must point to the config file name
    CONFIG_FILE: str = None
    SUBMIT: bool = False

    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Defines the argument list expected when using polarion as the adapter.
        :param parser:
        :return:
        """
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("-c", "--config",
                           help="Polarion config file")
        group.add_argument("--generate-config",
                           help="Generate a sample config file using provided file name")
        parser.add_argument("--submit", action="store_true", default=False,
                            help="If specified, submits all matching test cases into Polarion, "
                                 "otherwise converted test cases will simply get logged.")

    def parse_arguments(self, parsed_arguments: argparse.Namespace):
        """
        Parses the argument list, validating polarion specific args.
        :param parsed_arguments:
        :return:
        """
        if parsed_arguments.config:
            if not os.path.isfile(parsed_arguments.config):
                print("Invalid config file provided.")
                sys.exit(1)
            PolarionArgParser.CONFIG_FILE = parsed_arguments.config
            # Validates if config file can be parsed
            try:
                PolarionConfig(PolarionArgParser.CONFIG_FILE)
            except:
                print("Unable to parse config file")
                sys.exit(1)
        else:
            self.generate_sample_config(parsed_arguments.generate_config)

        PolarionArgParser.SUBMIT = bool(parsed_arguments.submit)

    @staticmethod
    def generate_sample_config(config_file):
        """
        Generates a sample configuration file for the FMF Polarion Adapter.
        :param config_file:
        :return:
        """

        if os.path.exists(config_file):
            print("Unable to generate config file. Provided file name already exists.")
            sys.exit(1)

        with open(config_file, 'w') as cfg:
            cfg.write("[%s]\n" % PolarionConfig.KEY_SECTION)
            cfg.write("%s=https://127.0.0.1/polarion/import/testcase\n" % PolarionConfig.KEY_TC_URL)
            cfg.write("%s=https://127.0.0.1/polarion/import/xunit\n" % PolarionConfig.KEY_XUNIT_URL)
            cfg.write("%s=user\n" % PolarionConfig.KEY_USER)
            cfg.write("%s=pass\n" % PolarionConfig.KEY_PASS)
            cfg.close()

        print("Config file has been generated: %s" % config_file)
        sys.exit(0)
