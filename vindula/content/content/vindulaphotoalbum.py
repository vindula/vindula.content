# -*- coding: utf-8 -*-
from five import grok

from vindula.content import MessageFactory as _
from AccessControl import ClassSecurityInfo
from vindula.content.content.interfaces import IVindulaPhotoAlbum

from plone.app.folder.folder import ATFolder

from zope.interface import implements
from vindula.content.config import *
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from zope.component import adapter
from zope.app.container.interfaces import IObjectAddedEvent
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping 
from zope.component import getUtility, getMultiAdapter
from collective.quickupload.portlet import quickuploadportlet as QuickUpload


VindulaPhotoAlbum_schema =  ATFolder.schema.copy() + Schema((
))

finalizeATCTSchema(VindulaPhotoAlbum_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}

class VindulaPhotoAlbum(ATFolder):
    """ VindulaPhotoAlbum """
    
    security = ClassSecurityInfo()
    implements(IVindulaPhotoAlbum)
    portal_type = 'VindulaPhotoAlbum'
    _at_rename_after_creation = True
    schema = VindulaPhotoAlbum_schema
    
registerType(VindulaPhotoAlbum, PROJECTNAME) 

@adapter(IVindulaPhotoAlbum, IObjectAddedEvent)
def CreatVindulaPhotoAlbum(context, event):
    
    right_manager = getUtility(IPortletManager,
                               name = u'plone.rightcolumn',
                               context = context)
    
    right_portlets = getMultiAdapter( (context, right_manager),
                                     IPortletAssignmentMapping,
                                     context = context)
    
    if not 'UploadPhoto' in right_portlets:
        right_portlets['UploadPhoto'] = QuickUpload.Assignment(header='Adicione as imagens no álbum.',
                                                               upload_media_type='image')
    

        
        