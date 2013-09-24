# -*- coding: utf-8 -*-
from five import grok

from vindula.content import MessageFactory as _
from AccessControl import ClassSecurityInfo
from vindula.content.content.interfaces import IVindulaEmployee
from vindula.content.content.vindulanews import VindulaNews
from zope.interface import implements
from vindula.content.config import *
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
   

from zope.schema.interfaces import IVocabularyFactory   
from zope.component import queryUtility


VindulaEmployee_schema =  VindulaNews.schema.copy() + Schema((

    StringField(
            name = 'email',
            widget=StringWidget(
                label= 'Email',
                description= 'Digite o email de contato do funcionário.',
            ),
        ),
        StringField(
            name = 'phone_number',
            widget=StringWidget(
                label= 'Telefone',
                description= 'Digite o telefone de contato do funcionário.',
            ),
        ),
    
        StringField(
            name = 'cargo',
            widget=StringWidget(
                label= 'Cargo',
                description= 'Digite o cargo do funcionário.',
            ),
    ),
   

))

finalizeATCTSchema(VindulaEmployee_schema, folderish=False)
invisivel = {'view':'invisible','edit':'invisible',}
VindulaEmployee_schema['activ_discussion'].widget.visible = invisivel
VindulaEmployee_schema['activ_share_footer'].widget.visible = invisivel
VindulaEmployee_schema['active_date'].widget.visible = invisivel
VindulaEmployee_schema['active_author'].widget.visible = invisivel
VindulaEmployee_schema['structures'].widget.visible = invisivel
VindulaEmployee_schema['description'].widget.label = 'Informação Adicional'
VindulaEmployee_schema['description'].widget.description = 'Informações adicionais do funcionário'
VindulaEmployee_schema['text'].widget.label = 'Sobre'
VindulaEmployee_schema['text'].widget.description = 'Descrição do funcionário'
VindulaEmployee_schema['title'].widget.description = 'Nome do funcionário'
VindulaEmployee_schema.moveField('cargo', before='description')









class VindulaEmployee(VindulaNews):
    """ VindulaEmployee """
    
    security = ClassSecurityInfo()
    implements(IVindulaEmployee)
    portal_type = 'VindulaEmployee'
    _at_rename_after_creation = True
    schema = VindulaEmployee_schema
    

registerType(VindulaEmployee, PROJECTNAME) 

    
class VindulaEmployeeView(grok.View):
    grok.context(IVindulaEmployee)
    grok.require('zope2.View')
    grok.name('view')
    

