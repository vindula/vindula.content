# -*- coding: utf-8 -*-
from five import grok
from vindula.content import MessageFactory as _
from vindula.content.content.interfaces import IUnit
from Products.ATContentTypes.content.folder import ATFolder

from AccessControl import ClassSecurityInfo

from zope.interface import implements
from Products.Archetypes.atapi import *
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

from vindula.myvindula.models.instance_funcdetail import ModelsInstanceFuncdetails

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
            label=_(u"Unidade Organizacional"),
            description=_(u"Selecione uma Unidade Organizacional pai. Opcional."),

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
        #users = ModelsFuncDetails().get_allFuncDetails()
        users = ModelsInstanceFuncdetails().get_AllFuncDetails()
        terms = []
        result = ''
        
        if users is not None:
            for user in users:
                member_id = user.get('username')
                member_name = user.get('name') or member_id
                terms.append((member_id, unicode(member_name)))
        
        result = DisplayList(tuple(terms))
        return result

registerType(Unit, PROJECTNAME) 

class UnitView(grok.View):
    grok.context(IUnit)
    grok.require('zope2.View')
    grok.name('view')
    
