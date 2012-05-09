# -*- coding: utf-8 -*-
from five import grok

from vindula.content import MessageFactory as _
from plone.uuid.interfaces import IUUID
from zope.app.component.hooks import getSite
#from zope.component import getUtility
from zope.event import notify
from AccessControl import ClassSecurityInfo
from zope.interface import Interface

from vindula.myvindula.user import BaseFunc, ModelsFuncDetails, ModelsMyvindulaHowareu, ModelsDepartment
from vindula.content.content.interfaces import IOrganizationalStructure, IOrgstructureModifiedEvent
#from Products.ATContentTypes.content.folder import ATFolder
from plone.app.folder.folder import ATFolder
from Products.SmartColorWidget.Widget import SmartColorWidget

from zope.interface import implements
from Products.Archetypes.atapi import *
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *


OrganizationalStructure_schema =  ATFolder.schema.copy() + Schema((
    
    StringField(
        name='categoria',
        widget=SelectionWidget(
            label=_(u"Categoria"),
            description=_(u"Selecione a categoria desta estrutura.\
                         Para gerenciar as categorias <a href=\"/control-panel-objects/vindula_categories\" target=\"_blank\">clique aqui</a>."),

            format = 'select',
        ),
        vocabulary='voc_categoria',
        required=False,
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
            name='employees',
            widget=InAndOutWidget(
                label=_(u"Funcionarios desta Estrutura Organizacional"),
                description=_(u"Selecione os funcionarios que estão nesta estrutura organizacional."),
                
            ),
            required=0,
            vocabulary='voc_employees',
    ),

    StringField(
        name='manager',
        widget=SelectionWidget(
            label=_(u"Gestor"),
            description=_(u"Indique quem é o gestor dessa estrutura organizacional."),

            format = 'select',
        ),
        vocabulary='voc_employees',
        required=False,
    ),

    TextField(
            name='text',
            default_content_type = 'text/restructured',
            default_output_type = 'text/x-html-safe',
            widget=RichWidget(
                label=_(u"Anotações"),
                description=_(u"Insira aqui as anotações da estrutura."),
                rows="10",
            ),
            required=False,
    ),

    ReferenceField('image',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem "),
        relationship='Imagem',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Imagem "),
            description='Será exibido na listagem de notícias e na própria notícia. A imagem será redimensionada para um tamanho adequado.')
    ),

#---------------------abas de permições no Objeto---------------------------------
     
    StringField(
            name='Groups_view',
            widget=InAndOutWidget(
                label=_(u"Grupo de usuários para visualização"),
                description=_(u"Selecione os grupos que teram permisão de visualizar este unidade Organizacional."),
                
            ),
            required=0,
            vocabulary='voc_listGroups',
            schemata = 'Permisões',
            #validators = ('isUserUpdate',),
    ),
    
    StringField(
            name='Groups_edit',
            widget=InAndOutWidget(
                label=_(u"Grupo de usuários de gerencia o conteudo"),
                description=_(u"Selecione os grupos que teram permisão de gerenciar o conteudo  desta unidade Organizacional."),
            ),
            required=0,
            vocabulary='voc_listGroups',
            schemata = 'Permisões',
            #validators = ('isUserUpdate',),
    ),

    StringField(
            name='Groups_admin',
            widget=InAndOutWidget(
                label=_(u"Grupo de usuários de adiministração"),
                description=_(u"Selecione os grupos que teram permisão de gerenciar totalmente este unidade Organizacional."),
            ),
            required=0,
            vocabulary='voc_listGroups',
            schemata = 'Permisões',
            validators = ('isUserUpdate',),
    ),

#---------------------abas de permições no Objeto---------------------------------

    BooleanField(
        name='activ_personalit',
        default=False,
        widget=BooleanWidget(
            label="Ativar Personalização",
            description='Se selecionado, Ativa a opção de personalização dos itens inferiores a estrutura organizacional.',
        ),
        schemata = 'Layout'
    ),                                                       

    StringField(
        name='corPortal',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor',
            description="Cor para esta area, todo o layout desta area usara esta cor.",
        ),
        schemata = 'Layout'
    ),    
    
    StringField(
        name='CorMenu',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor do background do Menu da Unidade',
            description="Cor do background do Menu da Unidade Organizacional.",
        ),
        schemata = 'Layout'
    ),
                                                                   
    ReferenceField('logoPortal',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Logo"),
        relationship='logoPortal',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Logo "),
            description='Será exibido no topo do portal desta area. A imagem será redimensionada para um tamanho adequado.'),
        schemata = 'Layout'
    ),
                                                                   
    ReferenceField('logoRodape',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Logo Rodape "),
        relationship='logoRodape',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Logo Rodape"),
            description='Será exibido no rodape desta area o imagem selecionada. A imagem será redimensionada para um tamanho adequado.'),
        schemata = 'Layout'
    ),                                                                   


    #-----------BackGroup do portal------------------
    ReferenceField('imageBackground',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"WallPapper do portal "),
        relationship='imageBackground',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"WallPaper do portal"),
            description='Será exibido no backgroup do portal a imagem selecionada. A imagem será mostrada em seu tamanho original, sem repetição.'),
        schemata = 'Layout'
    ),                                                                   
    
    StringField(
        name='corBackground',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor de background',
            description="Cor para o background do portal, caso a imagem não carregue ou não esteja selecionada.",
        ),
        schemata = 'Layout'
    ),    


))

finalizeATCTSchema(OrganizationalStructure_schema, folderish=True)


class OrganizationalStructure(ATFolder):
    """ OrganizationalStructure """
    
    security = ClassSecurityInfo()
    implements(IOrganizationalStructure)
    portal_type = 'OrganizationalStructure'
    _at_rename_after_creation = True
    schema = OrganizationalStructure_schema
    
    def at_post_create_script(self):
        """Notify that the employee has been saved.
        """
        notify(OrgstructureModifiedEvent(self))

    def at_post_edit_script(self):
        """Notify that the employee has been saved.
        """
        notify(OrgstructureModifiedEvent(self))
    
    
    def voc_categoria(self):
        terms = []
        try:obj = getSite()['control-panel-objects']['vindula_categories']
        except:obj = None
        
        if obj:
            try:
                field = obj.__getattribute__( 'orgstructure')
            except:
                field = None
            if field is not None:
                terms = field.splitlines()
                      
        return terms    
    
    
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
    
    def voc_listGroups(self):
        terms = []
        if 'acl_users' in getSite().keys():
            groups = getSite().get('acl_users').getGroups() 
            
            for group in groups:
                member_id = group.id
                member_name = group.getProperties().get('title','')
                terms.append((member_id, unicode(member_name)))
        
        return terms

registerType(OrganizationalStructure, PROJECTNAME) 

class OrgstructureModifiedEvent(object):
    """Event to notify that Orgstructure have been saved.
    """
    implements(IOrgstructureModifiedEvent)

    def __init__(self, context):
        self.context = context

def CreatGroupInPloneSite(event):
    ctx = event.context
    ctxPai = ctx.aq_parent
    portalGroup = getSite().portal_groups 
    tipos = [{'tipo':'view' ,'name':'',              'permissao':['Reader']                                    },
             {'tipo':'edit' ,'name':'- Edição',      'permissao':['Reviewer','Reader','Contributor']           },
             {'tipo':'admin','name':'- Administração', 'permissao':['Editor','Reviewer','Reader','Contributor']}
            ]
    
    for tipo in tipos:
        id_grupo = ctx.UID() +'-'+tipo['tipo']    
    
        if not id_grupo in portalGroup.listGroupIds():
            if ctxPai.portal_type == 'OrganizationalStructure':
                paiTitle = ctxPai.title
            else:
                paiTitle = ''
            
            nome_grupo = 'EO: '+ paiTitle +"\\"  + ctx.title + tipo['name']
            portalGroup.addGroup(id_grupo, title=nome_grupo)
            #Adiciona o grupo a 'AuthenticatedUsers'
            portalGroup.getGroupById('AuthenticatedUsers').addMember(id_grupo)
             
            ctx.manage_setLocalRoles(id_grupo, tipo['permissao'])  
        
        for view in eval('ctx.getGroups_'+tipo['tipo']+'()'):
            portalGroup.getGroupById(id_grupo).addMember(view)
    
        if ctxPai.portal_type == 'OrganizationalStructure':
            group_pai = ctxPai.UID()+"-view"
            portalGroup.getGroupById(group_pai).addMember(id_grupo)
        
    
    
class OrganizationalStructureView(grok.View):
    grok.context(IOrganizationalStructure)
    grok.require('zope2.View')
    grok.name('view_organizarional')
    
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
