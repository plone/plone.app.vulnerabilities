from zope.interface import Interface, implements
from plone.dexterity.content import Item
from zope import schema
from plone.app.vulnerabilities import VulnerabilitiesMessageFactory as _

class IHotfix(Interface):
    """ Marker interface for Hotfixes """

    release_date = schema.Datetime(title=_(u"Release date"),
                                   description=_(u"Date the hotfix was released"),
                                   )

    description = schema.Text(title=_(u"Description"),
                              description=_(u"Summary of hotfix contents"),
                              default=u"")

    # XXX: Original schema contained a hotfix_version field, which made no sense.

class Hotfix(Item):
    implements(IHotfix)