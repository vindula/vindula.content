# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from zope.app.component.hooks import getSite 
from zope.interface import Interface
from plone.app.discussion.interfaces import IConversation
from vindula.content.content.interfaces import IVindulaNews

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.newsitem import ATNewsItemSchema
from Products.ATContentTypes.content.newsitem import ATNewsItem
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

VindulaNews_schema = ATNewsItemSchema.copy() + Schema((

   ReferenceField('imageRelac',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem "),
        relationship='Imagem',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Imagem "),
            description='Será exibido na listagem de notícias e na própria notícia. A imagem será redimensionada para um tamanho adequado.')),

    BooleanField(
        name='activ_image',
        default=True,
        widget=BooleanWidget(
            label="Ativar Visualização da imagem",
            description='Se selecionado, Ativa a opção de visualizar a imagem junto como o corpo da notícia.',
        ),
        required=False,
    ),   

    BooleanField(
        name='activ_share',
        default=True,
        widget=BooleanWidget(
            label="Ativar Compartilhamento",
            description='Se selecionado, Ativa a opção de compartilhamento entre redes sociais.',
        ),
        required=False,
    ),                                                       
                                                       

))
invisivel = {'view':'invisible','edit':'invisible',}
VindulaNews_schema['description'].widget.label = 'Sumário'
VindulaNews_schema['description'].widget.description = 'Utilizado nas listagens de itens e resultado de buscas'
VindulaNews_schema['text'].widget.label = 'Corpo do texto'
VindulaNews_schema['text'].widget.description = 'Texto da Notícia'
VindulaNews_schema['image'].widget.visible = invisivel

finalizeATCTSchema(VindulaNews_schema, folderish=False)
VindulaNews_schema.changeSchemataForField('activ_share', 'settings')
VindulaNews_schema.moveField('imageRelac', before='imageCaption')

class VindulaNews(ATNewsItem):
    """ Reserve Content for VindulaNews"""
    security = ClassSecurityInfo()    
    
    implements(IVindulaNews)    
    portal_type = 'Relacionado'
    _at_rename_after_creation = True
    schema = VindulaNews_schema

registerType(VindulaNews, PROJECTNAME) 

   

# View
class VindulaNewsView(grok.View):
    grok.context(IVindulaNews)
    grok.require('zope2.View')
    grok.name('view')
  
    def check_share(self):
        if 'control-panel-objects' in getSite().keys():
            control = getSite()['control-panel-objects']
            if 'vindula_vindulanewsconfig' in control.keys():
                config = control['vindula_vindulanewsconfig']
                return config.ativa_conpartilhamento
            else:
                return False
          
        else:
            return False
 
    
class ShareView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View') 
    grok.name('vindula-content-share')


