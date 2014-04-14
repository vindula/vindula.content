# -*- coding: utf-8 -*-
from five import grok
from zope.interface import implements

from zope.app.container.interfaces import IObjectRemovedEvent, IObjectAddedEvent
from vindula.content.content.interfaces import IOrganizationalStructure, IOrgstructureModifiedEvent

from Products.CMFPlone.utils import _createObjectByType

from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, setSecurityManager
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from OFS.CopySupport import CopyError
import transaction


@grok.subscribe(IOrganizationalStructure, IObjectRemovedEvent)
def RemoveGroupInPloneSite(context, event):
    portal_membership = getToolByName(context, "portal_membership")
    user_admin = portal_membership.getMemberById('admin')

    # stash the existing security manager so we can restore it
    old_security_manager = getSecurityManager()

    # create a new context, as the owner of the folder
    newSecurityManager(context,user_admin)    
    
    portalGroup = context.portal_url.getPortalObject().portal_groups

    tipos = [{'tipo':'view' ,'name':'',              'permissao':['Reader']                                    },
             {'tipo':'edit' ,'name':' - Edição',      'permissao':['Reviewer','Reader','Contributor']           },
             {'tipo':'admin','name':' - Administração', 'permissao':['Editor','Reviewer','Reader','Contributor']}
            ]

    for tipo in tipos:
        id_grupo = context.UID() +'-'+tipo['tipo']
        try: portalGroup.removeGroup(id_grupo)
        except: pass
    
    # restore the original context
    setSecurityManager(old_security_manager)


class OrgstructureModifiedEvent(object):
    """Event to notify that Orgstructure have been saved.
    """
    implements(IOrgstructureModifiedEvent)

    def __init__(self, context):
        self.context = context


def CreatGroupInPloneSite(event):
    ctx = event.context
    portal_membership = getToolByName(ctx, "portal_membership")
    user_admin = portal_membership.getMemberById('admin')

    # stash the existing security manager so we can restore it
    old_security_manager = getSecurityManager()

    # create a new context, as the owner of the folder
    newSecurityManager(ctx,user_admin)

    ctxPai = ctx.aq_parent
    portalGroup =  ctx.portal_url.getPortalObject().portal_groups
    tipos = [{'tipo':'view' ,'name':'',              'permissao':['Reader']                                    },
             {'tipo':'edit' ,'name':' - Edição',      'permissao':['Reviewer','Reader','Contributor']           },
             {'tipo':'admin','name':' - Administração', 'permissao':['Editor','Reviewer','Reader','Contributor']}
            ]
    
    for tipo in tipos:
        id_grupo = ctx.UID() +'-'+tipo['tipo']
        
        #Limpa todos os usuarios dos grupos antes de adicinonar os novos
        if id_grupo and portalGroup.getGroupById(id_grupo):
            [portalGroup.removePrincipalFromGroup(m.getUserName(), id_grupo) for m in portalGroup.getGroupById(id_grupo).getGroupMembers() if m and m.getUserName()]

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
        
        if tipo['tipo'] == 'admin':
            admins = []
            if ctx.getManager():
                admins.append(ctx.getManager())
            if ctx.getVice_manager():
                admins.append(ctx.getVice_manager())
            if admins:
                ctx.setGroups_admin(tuple(admins))
            
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

    # restore the original context
    setSecurityManager(old_security_manager)

@grok.subscribe(IOrganizationalStructure, IObjectAddedEvent)
def CreatElemetsOrganizationalStructure(context, event):
    portal_membership = getToolByName(context, "portal_membership")
    user_admin = portal_membership.getMemberById('admin')

    # stash the existing security manager so we can restore it
    old_security_manager = getSecurityManager()

    # create a new context, as the owner of the folder
    newSecurityManager(context,user_admin)

    _cria_objeto(context, CONTEUDOS)

    homelayout = context.get('home_principal')
    if homelayout:
        context.setLayout_content(homelayout.UID())
        print 'gravado o layout principal'

    portletlayout = context.get('portlet_esquerdo')
    if portletlayout:
        context.setLayout_accessory(portletlayout.UID())
        print 'gravado o portlet direito'

    context.reindexObject()
    transaction.get().commit()

    # restore the original context
    setSecurityManager(old_security_manager)


CONTEUDOS = [{'id':'discussoes',     'titulo':u'Discussões',      'tipo':'Ploneboard'    },
             {'id':'paginas',        'titulo':u'Páginas',         'tipo':'VindulaFolder' },
             {'id':'arquivos',       'titulo':u'Arquivos',        'tipo':'VindulaFolder' },
             {'id':'blog',           'titulo':u'Blog',            'tipo':'VindulaFolder' },
             {'id':'questionarios',  'titulo':u'Questionários',   'tipo':'VindulaFolder' },
             {'id':'projetos',       'titulo':u'Projetos',        'tipo':'VindulaFolder' },
             {'id':'video-audio',    'titulo':u'Video/Audio',     'tipo':'VindulaFolder' },
             {'id':'album-de-fotos', 'titulo':u'Álbum de Fotos',  'tipo':'VindulaFolder' },
             {'id':'evento',         'titulo':u'Evento',          'tipo':'VindulaFolder' },
             {'id':'links',          'titulo':u'Links',           'tipo':'VindulaFolder' },
             {'id':'classificado',   'titulo':u'Classificados',   'tipo':'Classifieds'   },
             {'id':'reserva',        'titulo':u'Reserva',         'tipo':'ContentReserve'},
             {'id':'formulario',     'titulo':u'Formulário',      'tipo':'VindulaFolder' },
             {'id':'home_principal', 'titulo':u'Home Principal',  'tipo':'Layout'        },
             {'id':'portlet_esquerdo','titulo':u'Portlet Esquerdo','tipo':'Layout'       }
            ]


# LAYOUT_HOME_PRINCIPAL = [{'id':'banner',       'titulo':u'Banner em Destaques',  'tipo':'VindulaFolder'},
#                          {'id':'macro_abas',   'titulo':u'Áreas Principais',     'tipo':'VindulaFolder'},
#                          {'id':'informacoes',  'titulo':u'INFORMAÇÔES',          'tipo':'VindulaFolder'},
#                          {'id':'destaque',     'titulo':u'INFORME',              'tipo':'VindulaFolder'},
#                          {'id':'servicos',     'titulo':u'SERVIÇOS',             'tipo':'VindulaFolder'},
#                          {'id':'noticias',     'titulo':u'NOTÍCIAS',             'tipo':'VindulaFolder'},
#                          {'id':'links',        'titulo':u'LINKS ÚTEIS',          'tipo':'VindulaFolder'},
#                          {'id':'agenda',       'titulo':u'AGENDA',               'tipo':'VindulaFolder'},
#                          {'id':'proximo',      'titulo':u'PRÓXIMOS EVENTOS',     'tipo':'VindulaFolder'},
#                         ]

# LAYOUT_PORTLET_ESQUERDO = [{'id':'ultimos_documentos', 'titulo':u'ÚLTIMOS DOCUMENTOS',  'tipo':'VindulaFolder'},
#                            {'id':'aniversariantes',    'titulo':u'ANIVERSARIANTES',     'tipo':'VindulaFolder'},
#                           ]

def _cria_objeto(objeto, conteudos):
    """ Metodo para a criacao de conteudo
   """
    for conteudo in conteudos:
        id = conteudo['id']
        tipo = conteudo['tipo']
        titulo = conteudo['titulo']

        if tipo == 'Layout':
            _cria_componentes_layout(objeto)

        else:
            try:
                _createObjectByType(tipo, objeto, id=id, title=titulo)
            except BadRequest:
                print 'Error ao criar o objeto'
                pass


def _cria_componentes_layout(objeto):
    '''
        Criar o obejto de layout padrão no caminho /control-panel-objects/layout-default
        com os nomes de 'home_principal' e 'portlet_esquerdo'
    '''

    portal = objeto.portal_url.getPortalObject()
    catalog = portal.portal_catalog

    portal_path = '/'.join(portal.getPhysicalPath())
    path_layout = '/control-panel-objects/layout-default'

    rid = catalog.getrid(portal_path + path_layout)
    brain = catalog._catalog[rid]
    obj_folder = brain.getObject()

    if not 'home_principal' in objeto.keys() and\
       not 'portlet_esquerdo' in objeto.keys():

        objs = obj_folder.manage_copyObjects(['home_principal', 'portlet_esquerdo'])
        try:
            objeto.manage_pasteObjects(objs)
        except CopyError:
            print 'Error ao copiar o arquivo'
