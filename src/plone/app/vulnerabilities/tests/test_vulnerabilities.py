import unittest2 as unittest

from zExceptions import Unauthorized
from ZPublisher import NotFound
from plone.app.testing import setRoles, TEST_USER_NAME, TEST_USER_ID
from plone.testing.z2 import Browser
from plone.app.testing import login, logout
import transaction

from plone.app.vulnerabilities.testing import VULN_POLICY_FUNCTIONAL_TESTING

class TestVulnerabilities(unittest.TestCase):

    layer = VULN_POLICY_FUNCTIONAL_TESTING
    
    def test_anonymous_vulnerability_generation_is_not_allowed(self):
        plonesite = self.layer["portal"]
        app = self.layer["app"]
        browser = Browser(app)
        browser.handleErrors = False
        # Try adding a vulnerability as an Anonymous user
        with self.assertRaises(Unauthorized):
            browser.open(plonesite.absolute_url()+"/++add++vulnerability")
    
    def test_publishing_a_vulnerability_makes_it_visible_to_anonymous(self):
        plonesite = self.layer["portal"]
        workflow = plonesite.portal_workflow
        #import pdb; pdb.set_trace( )
        
        login(plonesite, TEST_USER_NAME)
        setRoles(plonesite, TEST_USER_ID, ["Manager", "Member"])
        transaction.commit()
        plonesite.invokeFactory('vulnerability', 'v1', title=u"Vulnerability 1")
        transaction.commit()
        vulnerability = plonesite["v1"]
        
        app = self.layer["app"]
        browser = Browser(app)
        browser.handleErrors = False
        #import pdb; pdb.set_trace( )
        
        # Try navigating to a draft vulnerability as an Anonymous user
        with self.assertRaises(Unauthorized):
            browser.open(vulnerability.absolute_url())
        
        # Publish the vulnerability and try visiting it again
        workflow.doActionFor(vulnerability, 'publish')
        transaction.commit()
        
        browser.open(vulnerability.absolute_url())
        self.assertTrue(u"Vulnerability 1" in browser.contents)
    
    def test_cve_number_calculation(self):
        # Put a definitely failing test here because we don't have any code for this at all yet
        self.assertEquals([1,2], [1,2,3])
    
    