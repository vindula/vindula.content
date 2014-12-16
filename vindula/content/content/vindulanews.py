# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
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
from plone.contentrules.engine.interfaces import IRuleAssignable

from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget
from vindula.content.content.requiredreadingschema import RequiredReadingSchema

VindulaNews_schema = ATNewsItemSchema.copy() + RequiredReadingSchema.copy() + Schema((


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

    ReferenceField('imageRelac',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem "),
        relationship='Imagem',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            label=_(u"Imagem "),
            description='Será exibido na listagem de notícias e na própria notícia. A imagem será redimensionada para um tamanho adequado.')
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

    # StringField(
    #     name='sub_titulo',
    #     searchable = True,
    #     widget = StringWidget(
    #         label = 'Editoriais',
    #         description='Digite um editoriais para a notícia.',
    #     ),
    # ),

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
                                                                                      
    BooleanField(
        name='activ_print',
        default=False,
        widget=BooleanWidget(
            label="Botão impressão",
            description='Exibir o botão de impressão da página.',
        ),
        required=False,
        schemata='settings',
    ),

))
invisivel = {'view':'invisible','edit':'invisible',}
VindulaNews_schema['description'].widget.label = 'Sumário'
VindulaNews_schema['description'].widget.description = 'Utilizado nas listagens de itens e resultado de buscas'
VindulaNews_schema['text'].widget.label = 'Corpo do texto'
VindulaNews_schema['text'].widget.description = 'Texto da Notícia'
VindulaNews_schema['image'].widget.visible = invisivel

VindulaNews_schema['allowDiscussion'].widget.visible = invisivel

finalizeATCTSchema(VindulaNews_schema, folderish=False)
VindulaNews_schema.changeSchemataForField('activ_share', 'settings')
VindulaNews_schema.changeSchemataForField('activ_share_footer', 'settings')
VindulaNews_schema.changeSchemataForField('activ_discussion', 'settings')
VindulaNews_schema.changeSchemataForField('themesNews', 'categorization')
VindulaNews_schema.moveField('themesNews', before='subject')
VindulaNews_schema.moveField('imageRelac', before='imageCaption')

#Ordenação dos campos da funcionalidade de Leitura Obrigatória
VindulaNews_schema.moveField("requiredReading", after="language")
VindulaNews_schema.moveField("startDateReqRead", after="requiredReading")
VindulaNews_schema.moveField("expirationDateReqRead", after="startDateReqRead")
VindulaNews_schema.moveField("usersGroupsReqRead", after="expirationDateReqRead")


class VindulaNews(ATNewsItem):
    """ Reserve Content for VindulaNews"""
    security = ClassSecurityInfo()

    implements(IVindulaNews, IRuleAssignable)
    portal_type = 'VindulaNews'
    _at_rename_after_creation = True
    schema = VindulaNews_schema



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



registerType(VindulaNews, PROJECTNAME)


# View
class VindulaNewsView(grok.View):
    grok.context(IVindulaNews)
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

class ShareView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('vindula-content-share')
    
class PrintNewView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('print-new')


