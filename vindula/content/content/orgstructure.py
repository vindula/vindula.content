# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from z3c.relationfield.schema import RelationChoice
from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.formwidget.contenttree import ObjPathSourceBinder
from vindula.content import MessageFactory as _
from vindula.content.vocabularies import TypesAgenda


# Interface and schema

class IOrganizationalStructure(form.Schema):
    """ Organizational Structure """
    
    category = schema.Choice(
         title=_(u"Categoria"),
         description=_(u"Selecione a categoria desta estrutura."),
         required=True,
         source=TypesAgenda('News Item')
        )
    
    text = RichText(
        title=_(u"Anotações"),
        description=_(u"Insira aqui as anotações da estrutura."),
        required=False,
        )
    
    image = RelationChoice(
        title=_(u"Imagem"),
        description=_(u"Logo da estrutura organizacional."),
        source=ObjPathSourceBinder(
            portal_type = 'Image',
            ),
        required=False,
        )