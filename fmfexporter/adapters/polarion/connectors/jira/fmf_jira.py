import configparser
import jira


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
    KEY_TC_WI = "testcase_work_item"
    KEY_QE_TC = "qe_test_coverage"
    KEY_VER_IR = "verified_in_release"

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

    @property
    def test_case_work_item_custom_field(self) -> str:
        """
        Returns the parsed jira custom field for test case work item
        :return:
        """
        return self.config[JiraConfig.KEY_SECTION][JiraConfig.KEY_TC_WI]

    @property
    def qe_test_coverage_custom_field(self) -> str:
        """
        Returns the parsed jira custom field for qe test coverage
        :return:
        """
        return self.config[JiraConfig.KEY_SECTION][JiraConfig.KEY_QE_TC]

    @property
    def verified_release_custom_field(self) -> str:
        """
        Returns the parsed jira custom field for verified in release
        :return:
        """
        return self.config[JiraConfig.KEY_SECTION][JiraConfig.KEY_VER_IR] or None

class FMFJiraPopulator(object):
    TEST_WI = 'test-work-item'
    QE_TEST_COV = 'qe-test-coverage'
    VERIFIED_IN_REL = 'verified-in-release'

    def __init__(self, config_file):
        self.config = JiraConfig(config_file)
        credentials = (self.config.username, self.config.password)
        self.jira_login = jira.JIRA(self.config.url,
                              basic_auth=credentials)

    def populate_testcases(self, tc_list: list):
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
                    list_tcwi = issue.raw.get("fields").get(self.config.test_case_work_item_custom_field)
                    if list_tcwi is None:
                        list_tcwi = [tc.test_case_work_item_url]
                    else:
                        list_tcwi.append(tc.test_case_work_item_url)

                    updated_fields = {
                        self.config.test_case_work_item_custom_field: ",".join(list_tcwi),
                        self.config.qe_test_coverage_custom_field: {"value": "+"},
                    }
                    if self.config.verified_release_custom_field:
                        updated_fields[self.config.verified_release_custom_field] = [{"value": "Verified in a release"}]

                    issue.update(fields=updated_fields)
            tc_counter += 1

