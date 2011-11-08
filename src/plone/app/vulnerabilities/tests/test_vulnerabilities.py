import unittest2 as unittest

from zExceptions import Unauthorized
from ZPublisher import NotFound
from plone.app.testing import setRoles, TEST_USER_NAME, TEST_USER_ID
from plone.testing.z2 import Browser
from plone.app.testing import login, logout

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
    
    def testVulnerabilityCreation(self):
        plonesite = self.layer["portal"]
        workflow = plonesite.portal_workflow
        #import pdb; pdb.set_trace( )
        
        login(plonesite, TEST_USER_NAME)
        setRoles(plonesite, TEST_USER_ID, ["Manager"])
        plonesite.invokeFactory('vulnerability', 'v1', title=u"Vulnerability 1")
        
        app = self.layer["app"]
        browser = Browser(app)
        browser.handleErrors = False
        #import pdb; pdb.set_trace( )
        
        
        
        # Try navigating to a draft vulnerability as an Anonymous user
        with self.assertRaises(NotFound):
            browser.open(plonesite.absolute_url()+"/v1")
            
        
        # Publish the vulnerability and try visiting it again
        #workflow.doActionFor(plonesite["v1"], 'publish')
        #browser.open(plonesite.absolute_url()+"/v1")
        #self.assertTrue(u"Vulnerability 1" in browser.contents)
        
        # login(plonesite, TEST_USER_NAME)
        #plonesite.restrictedTraverse("++add++vulnerability")