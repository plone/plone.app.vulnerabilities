from zope.interface import implements
from plone.dexterity.content import Container
from zope import schema
from plone.app.vulnerabilities import VulnerabilitiesMessageFactory as _
from plone.app.content.interfaces import INameFromTitle
from plone.app.textfield import RichText
from plone.supermodel import model

from plone.app.vulnerabilities.field import ChecksummedFile
class IHotfix(model.Schema):
    """ Marker interface for Hotfixes """

    description = schema.Text(title=_(u"Summary"),
                              description=_(u"A summary of the hotfix contents, used in item listings and search results."),
                              default=u"")

    release_date = schema.Date(title=_(u"Release date"),
                               description=_(u"Date the hotfix will be released"))

    # XXX: What about non-core packages?
    affected_versions = schema.List(title=_(u"Affected Plone versions"),
                                    value_type=schema.Choice(source="plone.app.vulnerabilities.ploneversions"))

    hotfix = ChecksummedFile(title=_(u"Hotfix"),
                        description=_(u"Old-style product tarball for this hotfix"),
                        required=False)
    
    text = RichText(title=_(u"Release body"),
                    description=_(u"This will be shown after the hotfix is released"),
                    default=u"",
                    allowed_mime_types=("text/html",),
                    required=False)

    model.fieldset(
            'preannounce',
            label=_(u"Preannounce"),
            fields=['preannounce_text']
        )

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
    
    def setTitle(self,title):
        # Don't allow anything to change the title.
        return