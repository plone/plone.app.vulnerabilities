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
                'date': self.get_date_from_version(v),
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

    @lazy_property
    def all_hotfixes_info(self):
        result = []

        for fix in self._all_hotfix_objects:
            fix_data = {
                'name': fix.id,
                'url': fix.absolute_url(),
                'release_date': fix.release_date.isoformat(),
                'affected_versions': fix.getAffectedVersions(),
            }
            if fix.hotfix is not None:
                fix_data['download_url'] = fix.absolute_url() + \
                    '/@@download/hotfix'
                fix_data['md5'] = fix.hotfix.md5
                fix_data['sha1'] = fix.hotfix.sha1
                fix_data['pypi_name'] = 'Products.PloneHotfix' + fix.id
            result.append(fix_data)

        return result

    def get_date_from_version(self, version):
        # This expects a version from registry['plone.versions'], like this:
        # 4.3.1-Jun 17, 2013
        return version.split('-')[1]


class HostfixJSONListing(HostfixListing):
    """ Load the collection of hotfixes and perform any processing required to
    present the correct list to the client via json
    """

    def __init__(self, context, request):
        super(HostfixJSONListing, self).__init__(context, request)
        self.context = context
        self.request = request

    def get_date_from_version(self, version):
        # This expects a version from registry['plone.versions'], like this:
        # 4.3.1-Jun 17, 2013.
        # We turn this into 2013-06-17 so callers can handle it how they like.
        date_format = '%b %d, %Y'
        plone_version_release_date = datetime.strptime(
            version.split('-')[1], date_format).date()
        return plone_version_release_date.isoformat()

    def __call__(self):
        result = []
        versions = self.get_versions()
        for vdata in versions:
            version = vdata['name']
            applied_hotfixes = []
            for fix in self.all_hotfixes_info:
                if version in fix["affected_versions"]:
                    # To keep the returned info exactly the same as before,
                    # we could remove the affected_versions from a copy
                    # and add this copy.
                    # from copy import deepcopy
                    # copied = deepcopy(fix)
                    # del copied["affected_versions"]
                    # applied_hotfixes.append(copied)
                    applied_hotfixes.append(fix)
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
