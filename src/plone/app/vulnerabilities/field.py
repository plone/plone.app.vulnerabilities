from hashlib import sha1, md5
from zope.interface import implements
from zope import schema
from zope.schema.fieldproperty import FieldProperty
from plone.namedfile.interfaces import INamedFile, INamedFileField
from plone.namedfile.field import NamedFile
from plone.namedfile.file import NamedFile as FileValueType

class IChecksummedFile(INamedFile):
    md5 = schema.TextLine(title=u"MD5", required=False, default=None)
    sha1 = schema.TextLine(title=u"SHA1", required=False, default=None)
    
class IChecksummedFileField(INamedFileField):
    pass

class ChecksummedFileValueType(FileValueType):

    implements(IChecksummedFile)

    md5 = FieldProperty(IChecksummedFile['md5'])
    sha1 = FieldProperty(IChecksummedFile['sha1'])

    def __init__(self, **kw):
        super(ChecksummedFileValueType,self).__init__(**kw)
        
    def _setData(self,data):
        super(ChecksummedFileValueType,self)._setData(data)
        body = self._getData()
        self.sha1 = unicode(sha1(body).hexdigest())
        self.md5 = unicode(md5(body).hexdigest())

    data = property(FileValueType._getData, _setData)

class ChecksummedFile(NamedFile):
    """ A file field which computes MD5 and SHA1 checksums for the uploaded file """
    implements(IChecksummedFileField)
    
    _type = ChecksummedFileValueType
    schema = IChecksummedFile
    
    def __init__(self, **kw):
        if 'schema' in kw:
            self.schema = kw.pop('schema')
        super(ChecksummedFile, self).__init__(schema=self.schema, **kw)
    
    