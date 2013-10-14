# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from plone.app.discussion.interfaces import IConversation
from vindula.content.content.interfaces import IVindulaRevista

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.newsitem import ATNewsItemSchema
from Products.ATContentTypes.content.newsitem import ATNewsItem
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget

VindulaRevista_schema = ATNewsItemSchema.copy() + Schema((


    FileField('file',
        widget= FileWidget(label='Arquivo da Publicação',
            description='Insira um arquivo da publicação'),
        required=True,
    ),

    ImageField('image',
        label=_(u"Imagem "),
        sizes= {'large'   : (768, 768),
                'preview' : (400, 400),
                'mini'    : (200, 200),
                'thumb'   : (128, 128),
                'tile'    :  (64, 64),
                'icon'    :  (32, 32),
                'listing' :  (16, 16),
                },
        widget=ImageWidget(
            #default_search_index='SearchableText',
            label=_(u"Imagem "),
            description='Será exibido na listagem de conteúdo e na própria publicação. A imagem será redimensionada para um tamanho adequado.')
    ),

    BooleanField(
        name='activ_image',
        default=True,
        widget=BooleanWidget(
            label="Ativar Visualização da imagem",
            description='Caso selecionado, ativa a opção de visualizar a imagem junto com o corpo da notícia.',
        ),
        required=False,
    ),

    ReferenceField('structures',
        multiValued=0,
        allowed_types=('OrganizationalStructure',),
        relationship='structures',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            typeview='list',
            label=_(u"Unidade Organizacional"),
            description=_(u"Selecione a Unidade Organizacional da página."),
            ),
        required=False
    ),


    BooleanField(
        name='active_author',
        default=True,
        widget=BooleanWidget(
            label="Ativar Visualização do Autor na Notícia",
            description='Caso selecionado, ativa a opção de visualizar o autor na notícia.',
        ),
        required=False,
    ),

    BooleanField(
        name='active_date',
        default=True,
        widget=BooleanWidget(
            label="Ativar Visualização da Data de Publicação na Notícia",
            description='Caso selecionado, ativa a opção de visualizar o data de criação na notícia.',
        ),
        required=False,
    ),

    BooleanField(
        name='activ_share',
        default=True,
        widget=BooleanWidget(
            label="Ativar Barra Social - Superior",
            description='Caso selecionado, ativa a barra social na área superior da página.',
        ),
        required=False,
    ),

    BooleanField(
        name='activ_share_footer',
        default=True,
        widget=BooleanWidget(
            label="Ativar Barra Social - Inferior",
            description='Caso selecionado, ativa a barra social na área inferior da página.',
        ),
        required=False,
    ),

    BooleanField(
        name='activ_discussion',
        default=True,
        widget=BooleanWidget(
            label="Ativar Comentários",
            description='Caso selecionado, ativa a opção de comentários.',
        ),
        required=False,
    ),

))
invisivel = {'view':'invisible','edit':'invisible',}
VindulaRevista_schema['description'].widget.label = 'Sumário'
VindulaRevista_schema['description'].widget.description = 'Utilizado nas listagens de itens e resultado de buscas'
VindulaRevista_schema['text'].widget.label = 'Corpo do texto'
VindulaRevista_schema['text'].widget.description = 'Texto da publicação'

VindulaRevista_schema['allowDiscussion'].widget.visible = invisivel

finalizeATCTSchema(VindulaRevista_schema, folderish=False)
VindulaRevista_schema.changeSchemataForField('activ_share', 'settings')
VindulaRevista_schema.changeSchemataForField('activ_share_footer', 'settings')
VindulaRevista_schema.changeSchemataForField('activ_discussion', 'settings')


class VindulaRevista(ATNewsItem):
    """ Reserve Content for VindulaNews"""
    security = ClassSecurityInfo()

    implements(IVindulaRevista)
    portal_type = 'VindulaRevista'
    _at_rename_after_creation = True
    schema = VindulaRevista_schema



    def getImageIcone(self):
        image = self.getImageRelac()

        if image:
            return image.absolute_url() +'/image_tile'
        else:
            return ''
        
    def getImageSize(self, size='mini'):
        image = self.getImageRelac()

        if image:
            return image.absolute_url() +'/image_' + size
        else:
            return ''

    def getFormattedStringTags(self):
        return (' / ').join(self.Subject())



registerType(VindulaRevista, PROJECTNAME)


# View
class VindulaRevistaView(grok.View):
    grok.context(IVindulaRevista)
    grok.require('zope2.View')
    grok.name('view')

    def check_share(self):
        panel = self.context.restrictedTraverse('@@myvindula-conf-userpanel')
        return panel.check_share()

    def creator(self):
        return self.context.Creator()

    def author(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getMemberInfo(self.creator())

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()

#class ShareView(grok.View):
#    grok.context(Interface)
#    grok.require('zope2.View')
#    grok.name('vindula-content-share')
