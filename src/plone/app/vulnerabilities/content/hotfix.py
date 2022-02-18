from Products.CMFCore.utils import getToolByName
import pkg_resources
from plone.app.content.interfaces import INameFromTitle
from plone.app.textfield import RichText
from plone.app.vulnerabilities import VulnerabilitiesMessageFactory as _
from plone.app.vulnerabilities.content.vulnerability import IVulnerability
from plone.app.vulnerabilities.field import ChecksummedFile
from plone.autoform.directives import read_permission
from plone.dexterity.content import Container
from plone.supermodel.directives import fieldset
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


class IHotfix(model.Schema):
    """ Marker interface for Hotfixes """

    description = schema.Text(title=_("Summary"),
                              description=_("A summary of the hotfix contents, used in item listings and search results."),
                              default="")

    release_date = schema.Date(title=_("Release date"),
                               description=_("Date the hotfix will be released"))

    read_permission(hotfix='plone.app.vulnerabilities.hotfix.view_release')
    hotfix = ChecksummedFile(title=_("Hotfix"),
                             description=_("Old-style product tarball for this hotfix"),
                             required=False)

    read_permission(text='plone.app.vulnerabilities.hotfix.view_release')
    text = RichText(title=_("Release body"),
                    description=_("This will be shown after the hotfix is released"),
                    default="",
                    allowed_mime_types=("text/html",),
                    required=False)

    fieldset(
        'preannounce',
        label=_("Preannounce"),
        fields=['preannounce_text']
    )

    read_permission(preannounce_text='plone.app.vulnerabilities.hotfix.view_preannounce')
    preannounce_text = RichText(title=_("Preannounce body"),
                                description=_("This will be shown while the hotfix is in the preannounce state"),
                                default="",
                                allowed_mime_types=("text/html",),
                                required=False)


class INameFromReleaseDate(INameFromTitle):
    def title():
        """Return a processed title"""


@implementer(INameFromReleaseDate)
class NameFromReleaseDate(object):

    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        # Hotfixes have their ID generated from their release date.
        return self.context.release_date.strftime("%Y%m%d")


@implementer(IHotfix)
class Hotfix(Container):

    @property
    def title(self):
        # Hotfixes have their ID generated from their release date.
        return self.release_date.strftime("%Y%m%d")

    @title.setter
    def title(self, value):
        pass

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
