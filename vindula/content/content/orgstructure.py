# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from z3c.relationfield.schema import RelationChoice
from plone.directives import form, dexterity
from plone.app.textfield import RichText
from plone.formwidget.contenttree import ObjPathSourceBinder
from vindula.content import MessageFactory as _
from vindula.controlpanel.vocabularies import ControlPanelObjects
from plone.uuid.interfaces import IUUID

from vindula.myvindula.user import BaseFunc, ModelsFuncDetails, ModelsMyvindulaHowareu

# Interface and schema

class IOrganizationalStructure(form.Schema):
    """ Organizational Structure """
    
    category = schema.Choice(
         title=_(u"Categoria"),
         description=_(u"Selecione a categoria desta estrutura.\
                         Para gerenciar as categorias <a href=\"/control-panel-objects/vindula_categories\" target=\"_blank\">clique aqui</a>."),
         source=ControlPanelObjects('vindula_categories', 'orgstructure'),
         required=False,
        )
    
    structures = RelationChoice(
        title=_(u"Estrutura Organizacional"),
        description=_(u"Selecione uma estrutura organizacional pai. Opcional."),
        source=ObjPathSourceBinder(
            portal_type = 'vindula.content.content.orgstructure',  
            review_state='published'      
            ),
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
    
    
    
class OrganizationalStructure(grok.View):
    grok.context(IOrganizationalStructure)
    grok.require('zope2.View')
    grok.name('view')
    
    def get_UID(self):
        return IUUID(self.context)
    
    def get_howareu_departament(self, departament):
        D={}
        D['visible_area'] = departament
        return ModelsMyvindulaHowareu().get_myvindula_howareu(**D)
    
    def get_prefs_user(self, user):
        try:
            user_id = unicode(user, 'utf-8')    
        except:
            user_id = user 

        return ModelsFuncDetails().get_FuncDetails(user_id)

    def getPhoto(self,photo):
        prefs_user = self.get_prefs_user(photo)
        if prefs_user:
            if prefs_user.photograph is not None and \
                not ' ' in prefs_user.photograph  and \
                not prefs_user.photograph == '':
                return BaseFunc().get_imageVindulaUser(prefs_user.photograph)
                #return self.context.absolute_url()+'/'+prefs_user.photograph # + '/image_thumb'
            else:
                return self.context.absolute_url()+'/defaultUser.png'
        else:
            return self.context.absolute_url()+'/defaultUser.png'
    


