from Products.Five.browser import BrowserView
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from plone.app.vulnerabilities.content.hotfix import IHotfix


class HotfixFeed(BrowserView):
    """ Load the collection of hotfixes and perform any processing required to present 
        the correct feed to the client """
    
    pass


class HostfixListing(BrowserView):
    """ Load the collection of hotfixes and perform any processing required to present 
        the correct list to the client """

    def get_hotfixes(self):
        context = aq_inner(self.context)
        tools = getMultiAdapter((context, self.request), name=u'plone_tools')

        portal_catalog = tools.catalog()
        brains = portal_catalog(object_provides=IHotfix.__identifier__)

        return sorted(result, key=lambda hotfix: hotfix.id, reverse=True)


    def get_versions(self):
        registry = getUtility(IRegistry)
        versions = registry['plone.versions']
        security = registry['plone.securitysupport']
        maintenance = registry['plone.activemaintenance']
        result = []
        for v in sorted(versions, reverse=True):
            version = v.split('-')[0]
            data = {
                'name': version,
                'date': v.split('-')[1],
                'security': version in security,
                'maintenance': version in maintenance
               }
            result.append(data)
        return result

    def get_hotfixes_for_version(self, version):
        # get all hotfixes
        result = []
        context = aq_inner(self.context)
        tools = getMultiAdapter((context, self.request), name=u'plone_tools')

        portal_catalog = tools.catalog()
        brains = portal_catalog(object_provides=IHotfix.__identifier__)

        for brain in brains:
            if version in brain.getObject().getAffectedVersions():
                result.append(brain)

        return sorted(result, key=lambda hotfix: hotfix.id, reverse=True)

