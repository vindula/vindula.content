# -*- coding: utf-8 -*-
from five import grok
from zope import schema
from z3c.relationfield.schema import RelationChoice, RelationList
from plone.directives import form, dexterity
from plone.app.textfield import RichText

from plone.formwidget.contenttree import ObjPathSourceBinder
from vindula.content import MessageFactory as _
from vindula.controlpanel.vocabularies import ControlPanelObjects
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from plone.uuid.interfaces import IUUID
from zope.app.component.hooks import getSite

from vindula.controlpanel.vocabularies import ListUserPortal

from vindula.myvindula.user import BaseFunc, ModelsFuncDetails, ModelsMyvindulaHowareu, ModelsDepartment


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
    
    employees = schema.List(title=_(u"Colaboradores"),
                            description=_(u"Indique quais são os colaboradores dessa estrutura organizacional."),
                            value_type=schema.Choice(source=ListUserPortal()),
                            required=False,
        )
    
    manager = schema.Choice(title=_(u"Gestor"),
                            description=_(u"Indique quem é o gestor dessa estrutura organizacional."),
                            source=ListUserPortal(),
                            required=False,)

    
#    employees = schema.TextLine(
#        title=_(u"Colaboradores"),
#        description=_(u"Indique quais são os colaboradores dessa estrutura organizacional."),
#        required=False,
#        )
    
#    manager = schema.TextLine(
#        title=_(u"Gestor"),
#        description=_(u"Indique quem é o gestor dessa estrutura organizacional."),
#        required=False,
#        )
    
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
    
@grok.subscribe(IOrganizationalStructure, IObjectCreatedEvent)
def CreatFormDataBase(context, event):
    id_grupo = context.id
    portalGroup = getSite().portal_groups 
    if not id_grupo in portalGroup.listGroupIds():
        nome_grupo = 'Estrutura Organizacional: ' + context.title
        portalGroup.addGroup(id_grupo, title=nome_grupo)
        #Adiciona o grupo a 'AuthenticatedUsers'
        portalGroup.getGroupById('AuthenticatedUsers').addMember(id_grupo)  
    
    
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
    
    def get_department(self, user):
        try:
            user_id = unicode(user, 'utf-8')    
        except:
            user_id = user
        
        return ModelsDepartment().get_departmentByUsername(user_id)    


    def getPhoto(self,photo):
        if photo is not None and not ' ' in photo:
            url_foto = BaseFunc().get_imageVindulaUser(photo)
            if url_foto:
                return url_foto
                #return self.context.absolute_url()+'/'+photo # + '/image_thumb'
            else:
                return self.context.absolute_url()+'/defaultUser.png'
        else:
            return self.context.absolute_url()+'/defaultUser.png'       

    def get_LastContent(self):
        ctool = getSite().portal_catalog
        objs = ctool(path = {'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                      sort_on='modified', sort_order='decrescent')   

        if objs:
            return objs
        else:
            return []
