# -*- coding: utf-8 -*-
from five import grok
from vindula.content import MessageFactory as _
from vindula.content.content.interfaces import IUnit
from Products.ATContentTypes.content.folder import ATFolder

from vindula.myvindula.user import ModelsFuncDetails
from AccessControl import ClassSecurityInfo

from zope.interface import implements
from Products.Archetypes.atapi import *
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *


Unit_schema =  ATFolder.schema.copy() + Schema((

    TextField(
            name='address',
            widget=StringWidget(
                label=_(u"Endereço"),
                description=_(u"Localização com endereço completo, será utilizado para gerar o mapa.",),
            ),
        required=True,
    ),
                                                
    ReferenceField('structures',
        multiValued=0,
        allowed_types=('OrganizationalStructure',),
        relationship='structures',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Estrutura Organizacional"),
            description=_(u"Selecione uma estrutura organizacional pai. Opcional."),

            ),
        required=False
    ),

    StringField(
            name='users',
            widget=InAndOutWidget(
                label=_(u"Usuários"),
                description=_("Relacionamentos com os usuários."),
                
            ),
            required=0,
            vocabulary='voc_employees',
    ),


))

finalizeATCTSchema(Unit_schema, folderish=True)

class Unit(ATFolder):
    """ Unit Folder """
    security = ClassSecurityInfo()
    
    implements(IUnit)    
    portal_type = 'Unit'
    _at_rename_after_creation = True
    schema = Unit_schema


    def voc_employees(self):
        users = ModelsFuncDetails().get_allFuncDetails()
        terms = []
        result = ''
        
        if users is not None:
            for user in users:
                member_id = user.username
                member_name = user.name or member_id
                terms.append((member_id, unicode(member_name)))
        
        result = DisplayList(tuple(terms))
        return result

registerType(Unit, PROJECTNAME) 

class UnitView(grok.View):
    grok.context(IUnit)
    grok.require('zope2.View')
    grok.name('view')
    











## Interface and schema
#class IUnit(form.Schema):
#    """ Unit Folder """
#    
#    address = schema.TextLine(
#        title=_(u"Endereço"),
#        description=u"Localização com endereço completo, será utilizado para gerar o mapa.",
#        required=False,
#        )
#
#    structures = RelationChoice(
#        title=_(u"Estruturas Organizacionais"),
#        description=u"Relacionamentos com as estruturas organizacionais.",
#        source=ObjPathSourceBinder(
#            portal_type = 'vindula.content.content.orgstructure',  
#            review_state='published'      
#            ),
#        required=False,
#        )
#
#    users = schema.TextLine(
#        title=_(u"Usuários"),
#        description=u"Relacionamentos com os usuários.",
#        required=False,
#        )