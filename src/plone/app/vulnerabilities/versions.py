from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


def plone_version_vocabulary(context):
	registry = getUtility(IRegistry)
	versions = registry['plone.versions']
	list_versions = [a.split('-')[0] for a in versions]
	items = [SimpleTerm(i, i, i) for i in sorted(list_versions, reverse=True)]
	return SimpleVocabulary(items)
