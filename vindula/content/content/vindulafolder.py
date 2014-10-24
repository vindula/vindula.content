# -*- coding: utf-8 -*-
from five import grok

from vindula.content import MessageFactory as _
from zope.app.component.hooks import getSite
from AccessControl import ClassSecurityInfo
from vindula.content.content.interfaces import IVindulaFolder
from plone.contentrules.engine.interfaces import IRuleAssignable

from plone.app.folder.folder import ATFolder

#from Products.UserAndGroupSelectionWidget.at import widget
#from Products.SmartColorWidget.Widget import SmartColorWidget

from zope.interface import implements
from vindula.content.config import *
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema


from zope.schema.interfaces import IVocabularyFactory
from zope.component import queryUtility

from hashlib import md5

VindulaFolder_schema =  ATFolder.schema.copy() + Schema((

    StringField(
        name='itens_menu',
        widget=InAndOutWidget(
            label=_(u"Itens do Menu"),
            description=_(u"Selecione os tipos de itens que serão apresentados no menu e no sub-menu. Caso nenhum item seja selecionado, o padrão global será utilizado."),
            format = 'select',
        ),
        vocabulary='voc_itens_menu',
        required=False,
        schemata = 'settings'
    ),

))

finalizeATCTSchema(VindulaFolder_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}

class VindulaFolder(ATFolder):
    """ VindulaFolder """

    security = ClassSecurityInfo()
    implements(IVindulaFolder, IRuleAssignable)
    portal_type = 'VindulaFolder'
    _at_rename_after_creation = True
    schema = VindulaFolder_schema

    def voc_itens_menu(self):
        types = self.portal_types.listContentTypes()
        return types


registerType(VindulaFolder, PROJECTNAME)


#class VindulaFolderView(grok.View):
#    grok.context(IVindulaFolder)
#    grok.require('zope2.View')
#    grok.name('view')
#

# class VindulaFolderSync(grok.View):
#     grok.context(IVindulaFolder)
#     grok.require('zope2.View')
#     grok.name('enable-sync')

#     def __init__(self,context,request):
#         super(VindulaFolderSync,self).__init__(context,request)
#         context = self.context
#         self.portal_type = context.portal_type
#         self.UID = context.UID()

#     def get_id_frame(self):
#         return md5(self.portal_type + self.UID).hexdigest()

#     def get_url_frame(self):
#         url = self.context.portal_url()
#         user_token = self.request.SESSION.get('user_token')

#         return '%s/vindula-api/sync/habilitar/%s/%s/%s?iframe_id=%s' %(url,user_token,self.portal_type,self.UID,self.get_id_frame())
