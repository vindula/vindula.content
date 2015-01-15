# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.base import ATCTContent, ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes.atapi import *
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.contentrules.engine.interfaces import IRuleAssignable
from zope.interface import implements

from vindula.content.config import *
from vindula.content.content.interfaces import IVindulaMural


VindulaMural_schema =  ATContentTypeSchema.copy() + Schema((

    BooleanField(
        name='activ_portlteRight',
        default=True,
        widget=BooleanWidget(
            label="Coluna Direita",
            description='Ativa a visualização dos itens da coluna da direita. Ex: Portlets.',
        ),
        required=False,
        schemata="settings",
    ),

    BooleanField(
        name='activ_portletLeft',
        default=True,
        widget=BooleanWidget(
            label="Coluna Esquerda",
            description='Ativa a visualização dos itens da coluna da esquerda. Ex: Portlets.',
        ),
        required=False,
        schemata="settings",
    ),

))

finalizeATCTSchema(VindulaMural_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}

class VindulaMural(ATCTContent):
    """ VindulaMural """
    
    security = ClassSecurityInfo()
    implements(IVindulaMural, IRuleAssignable)
    portal_type = 'VindulaMural'
    _at_rename_after_creation = True
    schema = VindulaMural_schema

    
registerType(VindulaMural, PROJECTNAME) 


class VindulaMuralView(grok.View):
    grok.context(IVindulaMural)
    grok.require('zope2.View')
    grok.name('view')

    def update(self):
        self.UID = self.context.UID()
        self.portal_url = self.context.portal_url()
        
        session_manager = getToolByName(self.context, 'session_data_manager')
        session = session_manager.getSessionData()
        self.token_user = session.get('user_token', '')