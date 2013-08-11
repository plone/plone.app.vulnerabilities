from zope.interface import Interface, implements
from plone.dexterity.content import Container
from zope import schema
from plone.app.vulnerabilities import VulnerabilitiesMessageFactory as _
from plone.app.content.interfaces import INameFromTitle


class IHotfix(Interface):
    """ Marker interface for Hotfixes """

    release_date = schema.Date(title=_(u"Release date"),
                                   description=_(u"Date the hotfix was released"),
                                   )

    description = schema.Text(title=_(u"Description"),
                              description=_(u"Summary of hotfix contents"),
                              default=u"")

    # XXX: Original schema contained a hotfix_version field, which made no sense.

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
    
