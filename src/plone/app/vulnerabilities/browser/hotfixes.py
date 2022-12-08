from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from datetime import datetime
from plone.app.vulnerabilities.content.hotfix import IHotfix
from plone.registry.interfaces import IRegistry
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getMultiAdapter
from zope.component import getUtility

import json


class HotfixFeed(BrowserView):
    """ Load the collection of hotfixes and perform any processing required to
    present the correct feed to the client
    """

    pass


class HostfixListing(BrowserView):
    """ Load the collection of hotfixes and perform any processing required to
    present the correct list to the client
    """

    def get_hotfixes(self):
        context = aq_inner(self.context)
        tools = getMultiAdapter((context, self.request), name=u'plone_tools')

        portal_catalog = tools.catalog()
        brains = portal_catalog(object_provides=IHotfix.__identifier__)

        return sorted(brains, key=lambda hotfix: hotfix.id, reverse=True)

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

    @lazy_property
    def _all_hotfix_objects(self):
        return [brain.getObject() for brain in self.get_hotfixes()]

    def get_hotfixes_for_version(self, version):
        result = []

        for hotfix in self._all_hotfix_objects:
            if version in hotfix.getAffectedVersions():
                result.append(hotfix)

        return result


class HostfixJSONListing(HostfixListing):
    """ Load the collection of hotfixes and perform any processing required to
    present the correct list to the client via json
    """

    def __init__(self, context, request):
        super(HostfixJSONListing, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        registry = getUtility(IRegistry)
        versions = registry['plone.versions']
        security = registry['plone.securitysupport']
        maintenance = registry['plone.activemaintenance']
        result = []

        for v in sorted(versions, reverse=True):
            version = v.split('-')[0]
            date_format = '%b %d, %Y'
            plone_version_release_date = datetime.strptime(
                v.split('-')[1], date_format).date()

            vdata = {
                'name': version,
                'date': plone_version_release_date.isoformat(),
                'security': version in security,
                'maintenance': version in maintenance,
                'hotfixes': {

                }
            }

            applied_hotfixes = []
            fixes = self.get_hotfixes_for_version(version)
            for fix in fixes:
                fix_data = {
                    'name': fix.id,
                    'url': fix.absolute_url(),
                    'release_date': fix.release_date.isoformat(),
                }
                if fix.hotfix is not None:
                    fix_data['download_url'] = fix.absolute_url() + \
                        '/@@download/hotfix'
                    fix_data['md5'] = fix.hotfix.md5
                    fix_data['sha1'] = fix.hotfix.sha1
                    fix_data['pypi_name'] = 'Products.PloneHotfix' + fix.id

                applied_hotfixes.append(fix_data)
            vdata['hotfixes'] = applied_hotfixes
            result.append(vdata)

        self.request.RESPONSE.setHeader('Content-Type',
                                        'application/json; charset="UTF-8"')

        if 'version' in self.request.form:
            requested_version = self.request.form['version']
            for r in result:
                if r['name'] == requested_version:
                    result = r
                    break
            else:
                result = None

        self.request.response.setBody(json.dumps(result))
        return self.request.response
