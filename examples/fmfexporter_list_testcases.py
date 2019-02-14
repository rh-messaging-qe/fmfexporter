from fmfexporter.fmf_adapter import FMFAdapterTest
import os
import pprint

"""
This is a simple example that demonstrates an FMF test case being parsed and displayed.
It fetches all test cases containing "test_path" in their names.
"""

# Loading FMF Tree from ../tests
fmf_adapter = FMFAdapterTest(os.path.dirname(os.path.abspath(__file__)) + "/../test")

# Listing all test cases found and containing "test_path" in their names
test_cases = [tc for tc in fmf_adapter.get_testcases_matching('test_path')]

# List all test case names and their content
for tc in test_cases:
    print(tc.name)
    pprint.PrettyPrinter(indent=4).pprint(tc.__dict__)
