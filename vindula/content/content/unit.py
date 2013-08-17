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


Unit_schema =  ATFolder.schema.copy() + Schema((

    TextField(
            name='address',
            widget=StringWidget(
                label=_(u"Endereço"),
                description=_(u"Localização com endereço completo, será utilizado para gerar o mapa.",),
            ),
        required=True,
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


registerType(Unit, PROJECTNAME)

class UnitView(grok.View):
    grok.context(IUnit)
    grok.require('zope2.View')
    grok.name('view')
