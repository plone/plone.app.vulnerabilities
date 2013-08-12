from zope.interface import Interface,implements
from plone.dexterity.content import Container
from zope import schema
from plone.app.vulnerabilities import VulnerabilitiesMessageFactory as _
from plone.app.content.interfaces import INameFromTitle
from plone.app.textfield import RichText
from plone.directives import form
from plone.autoform.directives import read_permission

from plone.app.vulnerabilities.field import ChecksummedFile
from Products.CMFCore.utils import getToolByName


class IHotfix(Interface):
    """ Marker interface for Hotfixes """

    description = schema.Text(title=_(u"Summary"),
                              description=_(u"A summary of the hotfix contents, used in item listings and search results."),
                              default=u"")

    release_date = schema.Date(title=_(u"Release date"),
                               description=_(u"Date the hotfix will be released"))

    read_permission(affected_versions='plone.app.vulnerabilities.hotfix.view_release')
    affected_versions = schema.List(title=_(u"Affected Plone versions"),
                                    value_type=schema.Choice(source="plone.app.vulnerabilities.ploneversions"))

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



class NameFromReleaseDate(object):
    implements(INameFromTitle)
    
    def __init__(self, context):
        self.context = context

    @property
    def title(self):
        # Hotfixes have their ID generated from their release date.
        return self.context.release_date.strftime("%Y%m%d")


class Hotfix(Container):
    implements(IHotfix)
    
    def released(self):
        workflowTool = getToolByName(self, "portal_workflow")
        status = workflowTool.getStatusOf("hotfix_workflow", self)
        state = status["review_state"]
        return state

    def setTitle(self,title):
        # Don't allow anything to change the title. While a little
        # crude, this prevents the rename page from setting a title
        # on a hotfix which it's not possible to remove
        return