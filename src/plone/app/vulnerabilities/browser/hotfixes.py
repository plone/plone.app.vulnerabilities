from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from copy import deepcopy
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

    @lazy_property
    def hotfixes(self):
        context = aq_inner(self.context)
        tools = getMultiAdapter((context, self.request), name=u'plone_tools')

        portal_catalog = tools.catalog()
        brains = portal_catalog(object_provides=IHotfix.__identifier__)

        brains = sorted(brains, key=lambda hotfix: hotfix.id, reverse=True)
        return [brain.getObject() for brain in brains]

    def get_versions(self):
        registry = getUtility(IRegistry)
        versions = registry['plone.versions']
        security = registry['plone.securitysupport']
        maintenance = registry['plone.activemaintenance']
        requested_version = self.request.form.get('version', '')
        result = []
        for v in sorted(versions, reverse=True):
            version = v.split('-')[0]
            if requested_version and version != requested_version:
                continue
            data = {
                'name': version,
                'date': self.get_date_from_version(v),
                'security': version in security,
                'maintenance': version in maintenance
            }
            if requested_version and version == requested_version:
                return [data]
            result.append(data)
        if requested_version:
            # No matching version found.
            return []
        return result

    def get_hotfixes_for_version(self, version):
        result = []

        for hotfix in self.hotfixes:
            if version in hotfix.getAffectedVersions():
                result.append(hotfix)

        return result

    @lazy_property
    def all_hotfixes_info(self):
        result = []

        for fix in self.hotfixes:
            fix_data = {
                'name': fix.id,
                'url': fix.absolute_url(),
                'release_date': fix.release_date.isoformat(),
                'affected_versions': fix.getAffectedVersions(),
            }
            result.append(fix_data)

        return result

    def get_date_from_version(self, version):
        # This expects a version from registry['plone.versions'], like this:
        # 4.3.1-Jun 17, 2013
        return version.split('-')[1]

    def get_combined_info(self):
        result = []
        versions = self.get_versions()
        for vdata in versions:
            version = vdata['name']
            applied_hotfixes = []
            for fix in self.all_hotfixes_info:
                if version in fix["affected_versions"]:
                    copied = deepcopy(fix)
                    del copied["affected_versions"]
                    applied_hotfixes.append(copied)
            vdata['hotfixes'] = applied_hotfixes
            result.append(vdata)
        return result


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
        self.request.RESPONSE.setHeader('Content-Type',
                                        'application/json; charset="UTF-8"')

        result = self.get_combined_info()
        self.request.response.setBody(json.dumps(result))
        return self.request.response
