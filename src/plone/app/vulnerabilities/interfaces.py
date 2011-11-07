from zope.interface import Interface

class IVulnerability(Interface):
    """ Marker Interface for Vulnerabilities """
    pass

class IHotfix(Interface):
    """ Marker interface for Hotfixes """
    pass
