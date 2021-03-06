# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes.atapi import *
from collective.quickupload.portlet import quickuploadportlet as QuickUpload
from five import grok
from plone.app.folder.folder import ATFolder
from plone.contentrules.engine.interfaces import IRuleAssignable
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping 
from zope.app.container.interfaces import IObjectAddedEvent
from zope.component import adapter, getUtility, getMultiAdapter
from zope.interface import Interface, implements

from vindula.content import MessageFactory as _
from vindula.content.config import *
from vindula.content.content.interfaces import IVindulaPhotoAlbum
from vindula.content.models.content_field import ContentField


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
            description=_(u"Tamanho em pixels para a exibição do álbum. Atenção, utilize apenas números inteiros."),
            
            label_msgid='vindula_content_label_height_photoAlbum',
            description_msgid='vindula_content_help_height_photoAlbum',
            i18n_domain='vindula_content',
        ),
        default=500,
        required=True,
    ),
    
    StringField(
        name='tipo',
        searchable = True,
        widget = SelectionWidget(
            label=u"Tipologia",
            description=u"Selecione a tipologia do álbum de fotos.",
            format = 'select', 
        ),
        vocabulary='get_tipo',
    ),
                                                             
    LinesField(
        'themesNews',
        multiValued=1,
        accessor="ThemeNews",
        searchable=True,
        schemata='categorization',
        widget=KeywordWidget(
            label=_(u'Temas'),
            description=_(u'Selecione os temas da noticia.'),
            ),
    ),

    BooleanField(
        name='activ_share',
        default=True,
        widget=BooleanWidget(
            label="Ativar barra social",
            description='Caso selecionado, ativa a barra social.',
        ),
        required=False,
    ),
                                                             
))

finalizeATCTSchema(VindulaPhotoAlbum_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}
VindulaPhotoAlbum_schema.changeSchemataForField('activ_share', 'settings')
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
    
    def get_tipo(self):
        content_fields = ContentField().get_content_file_by_type(u'tipo')
        L = [('', '-- Selecione --')]
        for item in content_fields:
            L.append((item,item))
            
        return DisplayList(tuple(L))
    
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
        if self.context.getFolderContents():
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
            return var
        else:
            return ''

    def check_share(self):
        panel = self.context.restrictedTraverse('@@myvindula-conf-userpanel')
        return panel.check_share()
    
# View Comentarios
class VindulaPhotoAlbumCommentsView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('view_comments_imagens')  