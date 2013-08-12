from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


def plone_version_vocabulary(context):
	registry = getUtility(IRegistry)
	versions = registry['plone.versions']
	items = [SimpleTerm(i, i, i) for i in versions]
	return SimpleVocabulary(items)
