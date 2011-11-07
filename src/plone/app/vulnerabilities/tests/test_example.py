import unittest2 as unittest

from plone.app.testing import setRoles

from plone.app.vulnerabilities.testing import VULN_POLICY_INTEGRATION_TESTING

class TestExamples(unittest.TestCase):

    layer = VULN_POLICY_INTEGRATION_TESTING

    def test_first_example_comparison(self):
        self.assertEqual([1,2], [1,2,3])