from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
from zope.configuration import xmlconfig


class VulnerabilitiesTests(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, z2.ZSERVER_FIXTURE)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.app.vulnerabilities
        xmlconfig.file('configure.zcml', plone.app.vulnerabilities, context=configurationContext)
        z2.installProduct(app, 'plone.app.vulnerabilities')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.app.vulnerabilities:default')


VULN_POLICY_FIXTURE = VulnerabilitiesTests()

VULN_POLICY_INTEGRATION_TESTING = IntegrationTesting(bases=(VULN_POLICY_FIXTURE,), name="Vulnerabilites:Integration")
VULN_POLICY_FUNCTIONAL_TESTING = FunctionalTesting(bases=(VULN_POLICY_FIXTURE,), name="Vulnerabilites:Functional")
