import logging

from fmfexporter.adapters.polarion.args.polarion_args_parser import PolarionArgParser
from fmfexporter import FMFTestCase
from fmfexporter.adapters.polarion.connectors.jira.fmf_jira import FMFJiraPopulator
from fmfexporter.adapters.polarion.polarion_reporter import PolarionReporter
from fmfexporter.adapters.polarion.polarion_test_case import PolarionTestCase
from fmfexporter.fmf_adapter import FMFAdapter, FMFAdapterArgParser
"""
FMF Adapter for the Polarion ALM tool.
"""


# Constants
ADAPTER_ID = "polarion"
LOGGER = logging.getLogger(__name__)


class FMFAdapterPolarion(FMFAdapter):
    """
    FMF Adapter implementation for the Polarion ALM tool.
    """

    def __init__(self, fmf_tree_path: str = '.'):
        super(FMFAdapterPolarion, self).__init__(fmf_tree_path)
        # If the config file has been parsed, create a reporter...
        self._reporter = None
        if PolarionArgParser.CONFIG_FILE:
            self._reporter: PolarionReporter = PolarionReporter(PolarionArgParser.CONFIG_FILE)

    @staticmethod
    def adapter_id() -> str:
        return ADAPTER_ID

    @staticmethod
    def get_args_parser() -> FMFAdapterArgParser:
        return PolarionArgParser()

    def convert_from(self, fmf_testcase: FMFTestCase):
        return PolarionTestCase.from_fmf_testcase(fmf_testcase)

    def submit_testcase(self, fmf_testcase: FMFTestCase):
        ptc = self.convert_from(fmf_testcase)

        #
        # If config file has been parsed (and there is a reporter available)
        # and --submit has been given, submit. Otherwise simply prints the tc.
        #
        if self._reporter and PolarionArgParser.SUBMIT:
            LOGGER.info("Submitting test case: %s" % ptc.id)
            tc = self._reporter.submit_testcase(ptc, PolarionArgParser.POPUL_TC)
            self.populate_jira(tc)
            return ptc
        else:
            print("Dumping test case: %s\n%s\n" % (ptc.id, ptc.to_xml()))

    def submit_testcases(self, fmf_testcases: list):
        submitted_tc = []
        polarion_test_cases = []
        for fmf_testcase in fmf_testcases:
            polarion_test_cases.append(self.convert_from(fmf_testcase))
        #
        # If config file has been parsed (and there is a reporter available)
        # and --submit has been given, submit. Otherwise simply prints the tc.
        #

        if self._reporter and PolarionArgParser.SUBMIT:
            if PolarionArgParser.ONE_BY_ONE:
                for ptc in polarion_test_cases:
                    LOGGER.info("Submitting test case: %s" % ptc.id)
                    submitted_tc.append(self._reporter.submit_testcase(ptc, PolarionArgParser.POPUL_TC))
            else:
                for ptc in polarion_test_cases:
                    LOGGER.info("Submitting test case: %s" % ptc.id)
                submitted_tc.extend(self._reporter.submit_testcases(polarion_test_cases, PolarionArgParser.POPUL_TC))
        else:
            if PolarionArgParser.ONE_BY_ONE:
                for ptc in polarion_test_cases:
                    print("Dumping test case: %s\n%s\n" % (ptc.id, ptc.to_xml()))
            else:
                print("Dumping test cases: \n%s\n" % (PolarionReporter.to_xml(polarion_test_cases)))

        self.populate_jira(submitted_tc)

    def populate_jira(self, submitted_testcases: list):
        # Linking Test Case Work items in jira
        if PolarionArgParser.JIRA_CONFIG is not None:
            jira_pop = FMFJiraPopulator(PolarionArgParser.JIRA_CONFIG)
            jira_pop.populate_testcases(submitted_testcases)
        else:
            LOGGER.warning("Jira configuration not provided")