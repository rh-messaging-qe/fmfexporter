import configparser
import jira

from fmfexporter.adapters import PolarionTestCase


class JiraConfig(object):
    """
   PolarionConfig represents data that must be provided through
   config (ini) file (to enable communication with the polarion importer APIs)
   """

    KEY_SECTION = 'jira'
    KEY_PROJECT = 'project'
    KEY_URL = 'url'
    KEY_USERNAME = 'username'
    KEY_PASSWORD = 'password'

    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        assert JiraConfig.KEY_SECTION in self.config.sections()

    @property
    def project(self) -> str:
        """
        Returns the parsed jira project name
        :return:
        """
        return self.config[JiraConfig.KEY_SECTION][JiraConfig.KEY_PROJECT]

    @property
    def url(self) -> str:
        """
        Returns the parsed jira project url
        :return:
        """
        return self.config[JiraConfig.KEY_SECTION][JiraConfig.KEY_URL]

    @property
    def username(self) -> str:
        """
        Returns the parsed jira username
        :return:
        """
        return self.config[JiraConfig.KEY_SECTION][JiraConfig.KEY_USERNAME]

    @property
    def password(self) -> str:
        """
        Returns the parsed jira password
        :return:
        """
        return self.config[JiraConfig.KEY_SECTION][JiraConfig.KEY_PASSWORD]


class FMFJiraPopulator(object):
    TEST_WI = 'test-work-item'
    QE_TEST_COV = 'qe-test-coverage'
    VERIFIED_IN_REL = 'verified-in-release'

    def __init__(self, config_file):
        self.config = JiraConfig(config_file)
        credentials = (self.config.username, self.config.password)
        self.jira_login = jira.JIRA(self.config.url,
                              basic_auth=credentials)
        if self.config.project.lower() == "entmqbr":
            self.custom_fields = FMFJiraPopulator.get_entmqbr_custom_fields()

    def populate_testcases(self, tc_list: PolarionTestCase):
        tc_list_len = len(tc_list)
        tc_counter = 1
        for tc in tc_list:  # type: PolarionTestCase
            list_tcwi = []
            for defect in tc.defects:
                if defect.jira != "":
                    if "http" in defect['jira']:
                        defect_key = defect['jira'][defect['jira'].rfind("/") + 1:]
                    else:
                        defect_key = defect['jira']
                    print("Populating %s test case %s of %s (%s)" % (self.config.url + "/browse/" + defect_key,
                                                                     tc_counter, tc_list_len, tc.id))
                    issue = self.jira_login.issue(defect_key)
                    list_tcwi = issue.raw.get("fields").get(self.custom_fields[self.TEST_WI])
                    if list_tcwi is None:
                        list_tcwi = [tc.test_case_work_item_url]
                    else:
                        list_tcwi.append(tc.test_case_work_item_url)

                    updated_fields = {
                        self.custom_fields[self.TEST_WI]: ",".join(list_tcwi), # append more links
                        self.custom_fields[self.QE_TEST_COV]: {"value": "+"},
                        self.custom_fields[self.VERIFIED_IN_REL]: [{"value": "Verified in a release"}],
                    }

                    issue.update(fields=updated_fields)
            tc_counter += 1

    @staticmethod
    def get_entmqbr_custom_fields():
        return {
            # Test Work Item        'customfield_12312840' [str]
            FMFJiraPopulator.TEST_WI: 'customfield_12312840',
            # QE Test Coverage      'customfield_12312848': +:11656, -:11657, ?: 11658,
            FMFJiraPopulator.QE_TEST_COV: 'customfield_12312848',
            # Verified in release:  'customfield_12315440'
            FMFJiraPopulator.VERIFIED_IN_REL: 'customfield_12315440',
        }
