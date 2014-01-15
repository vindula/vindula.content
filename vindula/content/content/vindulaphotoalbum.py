# -*- coding: utf-8 -*-
from five import grok

from vindula.content import MessageFactory as _
from AccessControl import ClassSecurityInfo
from zope.interface import Interface
from vindula.content.content.interfaces import IVindulaPhotoAlbum

from Products.CMFPlone.interfaces import INonStructuralFolder
from plone.app.folder.folder import ATFolder
from plone.contentrules.engine.interfaces import IRuleAssignable
from zope.interface import implements
from vindula.content.config import *
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from zope.component import adapter
from zope.app.container.interfaces import IObjectAddedEvent
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping 
from zope.component import getUtility, getMultiAdapter
from collective.quickupload.portlet import quickuploadportlet as QuickUpload


VindulaPhotoAlbum_schema =  ATFolder.schema.copy() + Schema((
 
 
    BooleanField(
        name='activ_portlteRight',
        default=True,
        widget=BooleanWidget(
            label="Coluna Direita",
            description='Ativa a visualização dos itens da coluna da direita. Ex: Portlets.',
        ),
        required=False,
    ),                                                       
    
    BooleanField(
        name='activ_portletLeft',
        default=True,
        widget=BooleanWidget(
            label="Coluna Esquerda",
            description='Ativa a visualização dos itens da coluna da esquerda. Ex: Portlets.',
        ),
        required=False,
    ),                                                       

    IntegerField(
        name='time_transitionsnews',
        widget=IntegerWidget(
            label=_(u"Velocidade de Rotação"),
            description=_(u"Tempo em milissegundos para mudar para a próxima imagem. Atenção, utilize apenas números inteiros."),
            
            label_msgid='vindula_content_label_time_transitionsnews',
            description_msgid='vindula_content_help_time_transitionsnews',
            i18n_domain='vindula_content',
        ),
        default=8000,
        required=True,
    ),

    IntegerField(
        name='height_photoAlbum',
        widget=IntegerWidget(
            label=_(u"Altura"),
            description=_(u"Tamanho em pixels para a exibição do album. Atenção, utilize apenas números inteiros."),
            
            label_msgid='vindula_content_label_height_photoAlbum',
            description_msgid='vindula_content_help_height_photoAlbum',
            i18n_domain='vindula_content',
        ),
        default=500,
        required=True,
    ),                                                             
                                                             
                                                             
))

finalizeATCTSchema(VindulaPhotoAlbum_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}
VindulaPhotoAlbum_schema.changeSchemataForField('time_transitionsnews', 'settings')
VindulaPhotoAlbum_schema.changeSchemataForField('height_photoAlbum', 'settings')
VindulaPhotoAlbum_schema.changeSchemataForField('activ_portlteRight', 'settings')
VindulaPhotoAlbum_schema.changeSchemataForField('activ_portletLeft', 'settings')


class VindulaPhotoAlbum(ATFolder):
    """ VindulaPhotoAlbum """
    
    security = ClassSecurityInfo()
    implements(IVindulaPhotoAlbum, IRuleAssignable) #,INonStructuralFolder)
    portal_type = 'VindulaPhotoAlbum'
    _at_rename_after_creation = True
    schema = VindulaPhotoAlbum_schema
    
registerType(VindulaPhotoAlbum, PROJECTNAME) 

@adapter(IVindulaPhotoAlbum, IObjectAddedEvent)
def CreatVindulaPhotoAlbum(context, event):
    right_manager = getUtility(IPortletManager,
                               name = u'plone.rightcolumn',
                               context = context)
    
    right_portlets = getMultiAdapter( (context, right_manager),
                                     IPortletAssignmentMapping,
                                     context = context)
    
    if not 'UploadPhoto' in right_portlets:
        right_portlets['UploadPhoto'] = QuickUpload.Assignment(header='Adicione as imagens no álbum.',
                                                               upload_media_type='image')
    
# View
class VindulaPhotoAlbumView(grok.View):
    grok.context(IVindulaPhotoAlbum)
    grok.require('zope2.View')
    grok.name('view')

    def jsGalleria(self):
        url = self.context.portal_url() + '/++resource++vindula.content/js/galleria'
        return url
     
    def jsConfigGalleria(self):
        var = '''
            Galleria.run('#galleria',{
                // Localized strings, modify these if you want tooltips in your language
                _locale: {
                    show_thumbnails: "Mostrar Miniaturas",
                    hide_thumbnails: "Esconder Miniaturas",
                    play: "Iniciar Slideshow",
                    pause: "Pausar Slideshow",
                    enter_fullscreen: "Tela Cheia",
                    exit_fullscreen: "Sair Tela Cheia",
                    popout_image: "Image em Popup",
                    showing_image: "Mostra image %s de %s"
                },
                // Initialize Galleria
                autoplay:'''+ str(self.context.getTime_transitionsnews()) +'});'
        
        if self.context.getFolderContents():
            return var
        else:
            return ''
    
# View Comentarios
class VindulaPhotoAlbumCommentsView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('view_comments_imagens')  