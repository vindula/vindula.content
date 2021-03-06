# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.document import ATDocumentSchema, ATDocumentBase
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes.atapi import *
from five import grok
from plone.app.blob.field import FileField, ImageField
from plone.contentrules.engine.interfaces import IRuleAssignable
from zope.interface import implements

from vindula.content import MessageFactory as _
from vindula.content.config import *
from vindula.content.content.interfaces import IVindulaVideo
from vindula.content.models.content_field import ContentField


VindulaVideo_schema =  ATDocumentSchema.copy() + Schema((
 
 
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
    
    FileField('file_video',
        widget= FileWidget(label='Vídeo',
                           description='Insira um vídeo'),
        required=True,
    ),
    
    
    ImageField('image_preview',
        max_size = (200, 200),
        widget= ImageWidget(label='Imagem do vídeo',
                           description='Insira uma imagem para aparecer na capa da Biblioteca'),
        required=True,
    ),
    
    LinesField(
        'themesNews',
        multiValued=1,
        accessor="ThemeNews",
        searchable=True,
        schemata='categorization',
        widget=KeywordWidget(
            label=_(u'Temas'),
            description=_(u'Selecione os temas.'),
        ),
    ),  
                                                         
    StringField(
        name='tipo',
        searchable = True,
        widget = SelectionWidget(
            label=u"Tipologia",
            description=u"Selecione a tipologia do vídeo.",
            format = 'select', 
        ),
        vocabulary='get_tipo',
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

finalizeATCTSchema(VindulaVideo_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}

VindulaVideo_schema['text'].widget.visible = invisivel 
VindulaVideo_schema.changeSchemataForField('activ_share', 'settings')
VindulaVideo_schema.changeSchemataForField('activ_portlteRight', 'settings')
VindulaVideo_schema.changeSchemataForField('activ_portletLeft', 'settings')


class VindulaVideo(ATDocumentBase):
    """ VindulaVideo """
    
    security = ClassSecurityInfo()
    implements(IVindulaVideo, IRuleAssignable)
    portal_type = 'VindulaVideo'
    _at_rename_after_creation = True
    schema = VindulaVideo_schema
    
    def get_tipo(self):
        content_fields = ContentField().get_content_file_by_type(u'tipo')
        L = [('', '-- Selecione --')]
        for item in content_fields:
            L.append((item,item))
            
        return DisplayList(tuple(L))
    
registerType(VindulaVideo, PROJECTNAME) 
    
# View
class VindulaVideoView(grok.View):
    grok.context(IVindulaVideo)
    grok.require('zope2.View')
    grok.name('view')

    def check_share(self):
        panel = self.context.restrictedTraverse('@@myvindula-conf-userpanel')
        return panel.check_share()