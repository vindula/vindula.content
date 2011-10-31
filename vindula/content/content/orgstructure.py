# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from z3c.relationfield.schema import RelationChoice
from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.formwidget.contenttree import ObjPathSourceBinder
from vindula.content import MessageFactory as _
from vindula.content.vocabularies import Categories


# Interface and schema

class IOrganizationalStructure(form.Schema):
    """ Organizational Structure """
    
    category = schema.Choice(
         title=_(u"Categoria"),
         description=_(u"Selecione a categoria desta estrutura.\
                         Para gerenciar as categorias <a href=\"/control-panel-objects/vindula_categories\" target=\"_blank\">clique aqui</a>."),
         source=Categories('orgstructure'),
         required=True,
        )
    
    structures = schema.TextLine(
        title=_(u"Estrutura Organizacional"),
        description=_(u"Selecione uma estrutura organizacional pai. Opcional."),
        required=False,
        )
    
    employees = schema.TextLine(
        title=_(u"Colaboradores"),
        description=_(u"Indique quais são os colaboradores dessa estrutura organizacional."),
        required=False,
        )
    
    manager = schema.TextLine(
        title=_(u"Gestor"),
        description=_(u"Indique quem é o gestor dessa estrutura organizacional."),
        required=False,
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