from plone.restapi.services import Service
from zope.component import getMultiAdapter


class HotfixesGet(Service):
    """Get a list of Plone versions with their applicable hotfixes."""

    def reply(self):
        # Reuse the hotfix_json view.
        serializer = getMultiAdapter((self.context, self.request), name="hotfix_json")

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message="No serializer available."))

        return serializer.get_combined_info()
