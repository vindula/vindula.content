# -*- coding: utf-8 -*-
from five import grok

from vindula.content import MessageFactory as _
from plone.uuid.interfaces import IUUID
from zope.app.component.hooks import getSite
from zope.event import notify
from zope.interface import Interface
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface

from zope.app.container.interfaces import IObjectRemovedEvent
from vindula.myvindula.user import BaseFunc, ModelsFuncDetails, ModelsMyvindulaHowareu, ModelsDepartment
from vindula.content.content.interfaces import IOrganizationalStructure, IOrgstructureModifiedEvent
from plone.app.folder.folder import ATFolder
from Products.UserAndGroupSelectionWidget.at import widget
from Products.SmartColorWidget.Widget import SmartColorWidget

from zope.interface import implements
from Products.Archetypes.atapi import *
from archetypes.referencebrowserwidget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

from vindula.myvindula.tools.utils import UtilMyvindula

from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget
from vindula.myvindula.models.instance_funcdetail import ModelsInstanceFuncdetails

OrganizationalStructure_schema =  ATFolder.schema.copy() + Schema((
    
    
    ReferenceField('structures',
        multiValued=0,
        allowed_types=('OrganizationalStructure',),
        relationship='structures',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            typeview='list',
            label=_(u"Tipo de Estrutura Organizacional"),
            description=_(u"Selecione o tipo de estrutura organizacional."),

            ),
        required=False
    ),

    LinesField(
            name="employees",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Funcionários desta Estrutura Organizacional"),
                description=_(u"Selecione os funcionários que estão nesta estrutura organizacional."),
                usersOnly=True,
                ),
            required=True,
            validators = ('isUserManageEmployees'),
            ),

    StringField(
            name='manager',
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Gestor"),
                description=_(u"Indique quem é o gestor dessa estrutura organizacional."),
                usersOnly=True
                ),
            required=True,
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
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            label=_(u"Imagem "),
            description='Será exibido na visualização desta estrutura. A imagem será redimensionada para um tamanho adequado.')
    ),

    #---------------------abas de permições no Objeto---------------------------------
     LinesField(
            name="Groups_view",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Grupo de usuários para visualização"),
                description=_(u"Selecione os grupos que terão permissão de visualizar esta unidade organizacional."),
                groupsOnly=True,
                ),
            required=0,
            schemata = 'Permissões',
            ),
    
     LinesField(
            name="Groups_edit",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Grupo de usuários de gerencia o conteúdo"),
                description=_(u"Selecione os grupos que terão permissão de gerenciar o conteúdo desta unidade organizacional."),
                groupsOnly=True,
                ),
            required=0,
            schemata = 'Permissões',
            ),
    
     LinesField(
            name="Groups_admin",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Grupo de usuários de administração"),
                description=_(u"Selecione os grupos que terão permissão de gerenciar totalmente esta unidade organizacional."),
                groupsOnly=True,
                ),
            required=0,
            schemata = 'Permissões',
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
        name='corGeralPortal',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor',
            description="Cor para esta área, todo o layout desta área usará esta cor.",
        ),
        schemata = 'Layout'
    ),    
                                                                   
    ReferenceField('logoPortal',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Logo"),
        relationship='logoPortal',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            label=_(u"Logo "),
            description='Será exibido no topo do portal desta área. A imagem será redimensionada para um tamanho adequado.'),
        schemata = 'Layout'
    ),
                                                                   
    ReferenceField('logoRodape',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Logo Rodapé "),
        relationship='logoRodape',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            label=_(u"Logo Rodapé"),
            description='Será exibido no rodapé desta área o imagem selecionada. A imagem será redimensionada para um tamanho adequado.'),
        schemata = 'Layout'
    ),                                                                   


    #-----------BackGroup do portal------------------
    ReferenceField('imageBackground',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"WallPapper do portal "),
        relationship='imageBackground',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            label=_(u"Imagem de fundo do portal"),
            description='A imagem será aplicada no background do portal. A imagem será mostrada em seu tamanho original, sem repetição.'),
        schemata = 'Layout'
    ),                                                                   
    
    StringField(
        name = 'posicaoImageBackground',
        widget=SelectionWidget(
            label='Posição da imagem de fundo',
            description="Selecione o coportamento da imagem de fundo.",
            format = 'select',
        ),
        vocabulary = [('no-repeat', 'Centralizar'), ('repeat', 'Repetir na pagina toda'), ('repeat-x', 'Repetir horizontalmente'), ('repeat-y', 'Repetir verticamente'),],
        default='no-repeat',
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
    
    ReferenceField('imageFooter',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem para o rodapé do portal."),
        relationship='imageFooter',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            label=_(u"Imagem para o rodapé do portal"),
            description='A imagem selecionada será exibida no rodapé do portal. Selecione uma imagem com dimenções 980x121'),
        schemata = 'Layout'
    ),

    #-----------Menu do portal------------------#
    
    StringField(
        name='corMenuFundo',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor de fundo do menu',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFundo.png'>aqui para exemplo</a>",
            #description="Cor para o fundo do primeiro nível do menu do portal.",
        ),
        schemata = 'Menu'
    ),
                                                            
    StringField(
        name='corMenuFonte',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor da fonte do menu',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonte.png'>aqui para exemplo</a>",
            #description="Cor para a fonte do primeiro nível do menu do portal.",
        ),
        schemata = 'Menu'
    ),
            
    StringField(
        name='corMenuHoverDropdown',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor do background do menu dropdown',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuHoverDropdown.png'>aqui para exemplo</a>",
            #description="Cor do background do link quando estiver com o mouse selecionado no primeiro nível, e a cor do fundo do Menu Dropdown.",
        ),
        schemata = 'Menu'
    ),   

    ReferenceField('imageSubmenuBkg',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem para o background do menu dropdown"),
        relationship='imageBkgSubmenu',
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Imagem para background do menu Dropdown"),
            description='A imagem selecionada será exibida como plano de fundo do menu dropdown.\
                         A imagem será mostrada com a sua largura original, com repetição.'),
        schemata = 'Menu'
    ),
                                                        
    ReferenceField('imageMenuBkg',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem para o background do menu dropdown"),
        relationship='imageBkgMenu',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            label=_(u"Imagem para background do primeiro nível do menu"),
            description='A imagem selecionada será exibida como plano de fundo do menu.\
                         A imagem será mostrada em seu tamanho original, com repetição.'),
        schemata = 'Menu'
    ),
    
    StringField(
        name='corMenuFonteDropdown',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor da fonte do menu dropdown',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteDropdown.png'>aqui para exemplo</a>",
            #description="Cor da fonte do link quando estiver selecionado pelo mouse no Menu Dropdown.",
        ),
        schemata = 'Menu'
    ), 
    
    StringField(
        name='corMenuFonteHoverDropdown',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor da fonte do menu quando ativo no menu dropdown',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteHoverDropdown.png'>aqui para exemplo</a>",
#            description="Cor para a fonte do primeiro nível do menu do portal quando ele\
#                         estiver quando selecionado pelo mouse e ao cor dos links dentro do Menu Dropdown.",
        ),
        schemata = 'Menu'
    ),
    
    StringField(
        name='corMenuDropdownHover',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor do background do link ativo dentro do menu dropdown',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuDropdownHover.png'>aqui para exemplo</a>",
            #description="Cor do link quando estiver selecionado pelo mouse dentro do Menu Dropdown.",
        ),
        schemata = 'Menu'
    ),     
    
    StringField(
        name='corMenuSelected',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor do background do link selecionado no primeiro nível do menu',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuSelected.png'>aqui para exemplo</a>",
            #description="Cor do fundo do link quando estiver selecionado no primeiro nível do Menu.",
        ),
        schemata = 'Menu'
    ),   
    
    StringField(
        name='corMenuFonteSelected',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor da fonte do link selecionado no primeiro nível do portal',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteSelected.png'>aqui para exemplo</a>",
            #description="Cor da fonte link quando estiver selecionado no primeiro nível.",
        ),
        schemata = 'Menu'
    ),   

    StringField(
        name='corMenuSelectedDropdown',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor do background do link selecionado no menu dropdown',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuSelectedDropdown.png'>aqui para exemplo</a>",
            #description="Cor do background do link quando estiver selecionado no Menu Dropdown.",
        ),
        schemata = 'Menu'
    ),                                                  

    StringField(
        name='corMenuFonteSelectedDropdown',
        searchable=0,
        required=0,
        widget=SmartColorWidget(
            label='Cor da fonte do link selecionado no menu ',
            description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteSelectedDropdown.png'>aqui para exemplo</a>",
            #description="Cor da fonte do link quando estiver selecionado no Menu.",
        ),
        schemata = 'Menu'
    ),

    # CONFIGURACAO DO TEMA DO PORTLET
    
    ReferenceField('imageTopPortlet',
        multiValued=0,
        allowed_types=('Image'),
        relationship='imageTopPortlet',
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Imagem para aparecer no topo do portlet"),
            description='A imagem selecionada será exibida como plano de fundo do menu.\
                         A imagem será mostrada com a sua altura original, com repetição.'),
        schemata = 'Portlet'

    ),
    
    IntegerField(
        name='heightTopPortlet',
        widget=IntegerWidget(
            label='Altura do topo do portlet',
            description='Altura, em pixels, do topo do portlet. Quando não definida, manterá o padrão de 15px',
        ),
        schemata = 'Portlet'
    ),
    
    ReferenceField('imageMiddlePortlet',
        multiValued=0,
        allowed_types=('Image'),
        relationship='imageMiddlePortlet',
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Imagem para aparecer no meio do portlet"),
            description='A imagem selecionada será exibida como plano de fundo do menu.\
                         A imagem será mostrada com a sua altura original, com repetição.'),
        schemata = 'Portlet'
    ),

    ReferenceField('imageBottomPortlet',
        multiValued=0,
        allowed_types=('Image'),
        relationship='imageBottomPortlet',
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Imagem para aparecer em baixo do portlet"),
            description='A imagem selecionada será exibida como plano de fundo do menu.\
                         A imagem será mostrada com a sua altura original, com repetição.'),
        schemata = 'Portlet'
    ),
    
    IntegerField(
        name='heightBottomPortlet',
        widget=IntegerWidget(
            label='Altura do rodapé do portlet',
            description='Altura, em pixels, do topo do portlet. Quando não definida manterá o padrão de 23px',
        ),
        schemata = 'Portlet'
    ),


))

finalizeATCTSchema(OrganizationalStructure_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}
# Dates
L = ['effectiveDate','expirationDate','creation_date','modification_date']   
# Categorization
L += ['subject','relatedItems','location','language']
# Ownership
L += ['creators','contributors','rights']
# Settings
L += ['allowDiscussion','excludeFromNav', 'nextPreviousEnabled']

for i in L:
    OrganizationalStructure_schema[i].widget.visible = invisivel 


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
    
    def voc_listGroups(self):
        terms = []
        if 'acl_users' in getSite().keys():
            groups = getSite().get('acl_users').getGroups() 
            
            for group in groups:
                member_id = group.id
                member_name = group.getProperties().get('title','')
                terms.append((member_id, unicode(member_name)))
        
        return terms

    def voc_itens_menu(self):
        types = self.portal_types.listContentTypes()
        return types

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
             {'tipo':'edit' ,'name':' - Edição',      'permissao':['Reviewer','Reader','Contributor']           },
             {'tipo':'admin','name':' - Administração', 'permissao':['Editor','Reviewer','Reader','Contributor']}
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

    
    id_grupo_employees = ctx.UID() +'-view'
    new_tupla = list(ctx.Groups_view)
    for user in ctx.getEmployees():
        if new_tupla.count(user) == 0:
            new_tupla.append(user)
        
        portalGroup.getGroupById(id_grupo_employees).addMember(user)
    ctx.Groups_view = tuple(new_tupla)


@grok.subscribe(IOrganizationalStructure, IObjectRemovedEvent)        
def RemoveGroupInPloneSite(context, event):
    portalGroup = getSite().portal_groups 
    tipos = [{'tipo':'view' ,'name':'',              'permissao':['Reader']                                    },
             {'tipo':'edit' ,'name':' - Edição',      'permissao':['Reviewer','Reader','Contributor']           },
             {'tipo':'admin','name':' - Administração', 'permissao':['Editor','Reviewer','Reader','Contributor']}
            ]
    
    for tipo in tipos:
        id_grupo = context.UID() +'-'+tipo['tipo']
        try: portalGroup.removeGroup(id_grupo)
        except: pass
    
    
class OrganizationalStructureView(grok.View, UtilMyvindula):
    grok.context(IOrganizationalStructure)
    grok.require('zope2.View')
    grok.name('view_organizational')
    
    def get_UID(self):
        return IUUID(self.context)
    
    def get_howareu_departament(self, departament):
        D={}
        D['visible_area'] = departament
        return ModelsMyvindulaHowareu().get_myvindula_howareu(**D)
    
    def get_department(self, user):
        try:
            user_id = unicode(user, 'utf-8')    
        except:
            user_id = user
        
        return ModelsDepartment().get_departmentByUsername(user_id)    

    def get_LastContent(self):
        ctool = getSite().portal_catalog
        objs = ctool(path = {'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
                      sort_on='modified', sort_order='decrescent')   

        if objs:
            return objs
        else:
            return []


class FolderOrganizationalStructureView(grok.View, BaseFunc):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('folder-organizational-structure')
    
    def getCategorias(self):
        return OrganizationalStructure(self.context).voc_categoria();
    
    def getOrgStruc(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        L = []
        
        if 'categoria' in self.request.form.keys():
            categoria = self.request.form.get('categoria')
        
        if categoria:
            results = catalog(portal_type='OrganizationalStructure',
                      review_state='published',
                      categoria = categoria,
                      )
            if results:
                for item in results:
                    item = item.getObject()
                    D = {}
                    D['title'] = item.Title()
                    D['url'] =   item.absolute_url()
                    L.append(D)
        return L
