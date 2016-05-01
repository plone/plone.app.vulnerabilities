from Products.CMFCore.utils import getToolByName
import pkg_resources
from plone.app.content.interfaces import INameFromTitle
from plone.app.textfield import RichText
from plone.app.vulnerabilities import VulnerabilitiesMessageFactory as _
from plone.app.vulnerabilities.content.vulnerability import IVulnerability
from plone.app.vulnerabilities.field import ChecksummedFile
from plone.autoform.directives import read_permission
from plone.dexterity.content import Container
from plone.directives import form
from plone.supermodel import model
from zope import schema
from zope.interface import implements


class IHotfix(model.Schema):
    """ Marker interface for Hotfixes """

    description = schema.Text(title=_(u"Summary"),
                              description=_(u"A summary of the hotfix contents, used in item listings and search results."),
                              default=u"")

    release_date = schema.Date(title=_(u"Release date"),
                               description=_(u"Date the hotfix will be released"))

    read_permission(hotfix='plone.app.vulnerabilities.hotfix.view_release')
    hotfix = ChecksummedFile(title=_(u"Hotfix"),
                             description=_(u"Old-style product tarball for this hotfix"),
                             required=False)

    read_permission(text='plone.app.vulnerabilities.hotfix.view_release')
    text = RichText(title=_(u"Release body"),
                    description=_(u"This will be shown after the hotfix is released"),
                    default=u"",
                    allowed_mime_types=("text/html",),
                    required=False)

    form.fieldset(
        'preannounce',
        label=_(u"Preannounce"),
        fields=['preannounce_text']
    )

    read_permission(preannounce_text='plone.app.vulnerabilities.hotfix.view_preannounce')
    preannounce_text = RichText(title=_(u"Preannounce body"),
                                description=_(u"This will be shown while the hotfix is in the preannounce state"),
                                default=u"",
                                allowed_mime_types=("text/html",),
                                required=False)


class INameFromReleaseDate(INameFromTitle):
    def title():
        """Return a processed title"""


class NameFromReleaseDate(object):
    implements(INameFromReleaseDate)

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        # Hotfixes have their ID generated from their release date.
        return self.context.release_date.strftime("%Y%m%d")


class Hotfix(Container):
    implements(IHotfix)

    @property
    def title(self):
        # Hotfixes have their ID generated from their release date.
        return self.release_date.strftime("%Y%m%d")

    def released(self):
        workflowTool = getToolByName(self, "portal_workflow")
        status = workflowTool.getStatusOf("hotfix_workflow", self)
        state = status["review_state"]
        return state

    def setTitle(self, title):
        # Don't allow anything to change the title. While a little
        # crude, this prevents the rename page from setting a title
        # on a hotfix which it's not possible to remove
        return

    def getAffectedVersions(self):
        """ Pull affected versions from the contained vulnerabilities."""

        catalog = getToolByName(self, 'portal_catalog')

        brains = catalog(object_provides=IVulnerability.__identifier__,
                         path={"query": '/'.join(self.getPhysicalPath())})

        result = []
        for brain in brains:
            result.extend(brain.getObject().affected_versions)

        result = sorted(set(result), key=pkg_resources.parse_version)
        result.reverse()

        return result
