# -*- coding: utf-8 -*-
from zope import schema
from plone.directives import form
from vindula.content import MessageFactory as _

# Interface and schema

class IUnit(form.Schema):
    """ Unit Folder """
    
    address = schema.TextLine(
        title=_(u"Endereço"),
        description=u"Localização com endereço completo, será utilizado para gerar o mapa.",
        )
    
    orgstructures = schema.TextLine(
        title=_(u"Estruturas Organizacionais"),
        description=u"Relacionamentos com as estruturas organizacionais.",
        )

    users = schema.TextLine(
        title=_(u"Usuários"),
        description=u"Relacionamentos com os usuários.",
        )