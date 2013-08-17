from zope.interface import implements
from zope.component import adapts

from vindula.content.content.interfaces import IVindulaFile
from plone.app.blob.interfaces import IBlobbable, IBlobWrapper

from plone.app.blob.adapters.ofsfile import BlobbableOFSFile


class BlobbableVindulaFile(object):
    """ adapter for VindulaFile objects to work with blobs """
    implements(IBlobbable)
    adapts(IVindulaFile)

    def feed(self, blob):
        """ see interface ... """
        raise ReuseBlob(self.context.getBlob())

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()

    def mimetype(self):
        """ see interface ... """
        return self.context.getContentType()
