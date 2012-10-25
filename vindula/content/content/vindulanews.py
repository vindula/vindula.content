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

from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget 

VindulaNews_schema = ATNewsItemSchema.copy() + Schema((
                                                       
                                                       
    LinesField(
        'themesNews',
        multiValued=1,
        accessor="ThemeNews",
        searchable=True,
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
            description='Será exibido na listagem de notícias e na própria notícia. A imagem será redimensionada para um tamanho adequado.')),

    BooleanField(
        name='activ_image',
        default=True,
        widget=BooleanWidget(
            label="Ativar Visualização da imagem",
            description='Se selecionado ativa a opção de visualizar a imagem junto como o corpo da notícia.',
        ),
        required=False,
    ),
    
    BooleanField(
        name='active_author',
        default=True,
        widget=BooleanWidget(
            label="Ativar Visualização do Autor na Notícia",
            description='Se selecionado ativa a opção de visualizar o autor na notícia.',
        ),
        required=False,
    ), 
    
    BooleanField(
        name='active_date',
        default=True,
        widget=BooleanWidget(
            label="Ativar Visualização da Data de Publicação na Notícia",
            description='Se selecionado ativa a opção de visualizar o data de criação na notícia.',
        ),
        required=False,
    ), 

    BooleanField(
        name='activ_share',
        default=True,
        widget=BooleanWidget(
            label="Ativar Compartilhamento",
            description='Se selecionado, ativa a opção de compartilhamento entre redes sociais.',
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
    portal_type = 'VindulaNews'
    _at_rename_after_creation = True
    schema = VindulaNews_schema

registerType(VindulaNews, PROJECTNAME) 


# View
class VindulaNewsView(grok.View):
    grok.context(IVindulaNews)
    grok.require('zope2.View')
    grok.name('view')
  
    def check_share(self):
        panel = self.context.restrictedTraverse('@@myvindula-conf-userpanel')
  
        if panel.check_share():
            return  self.context.getActiv_share()
        else:
            return False 

    def creator(self):
        return self.context.Creator()

    def author(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getMemberInfo(self.creator())

    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()
        
    def catalogNews(self, context=None, withKeywords=False):
        p_catalog = getSite().portal_catalog
        if not context:
            context = self.context

        query = {}
        query['portal_type'] = ['VindulaNews', 'News Item']
        query['sort_order'] = 'descending'
        if withKeywords:
            query['Subject'] = context.getRawSubject()
        query['sort_on'] = 'effective'
        query['review_state'] = ['published']
        
        return p_catalog(**query)
        
    
    def getReadMore(self):
        news = list(self.catalogNews(context=self.context, withKeywords=True))
        results = []
        [results.append(new) for new in news if new.getObject() != self.context]
        
        return results
    
    def getSeeAlso(self):
        news = list(self.catalogNews(context=self.context))
        results = []
        if self.context.ThemeNews():
            for item in news:
                obj = item.getObject()
                if obj == self.context or not obj.ThemeNews():
                   continue
                else:
                    for tema in obj.ThemeNews():
                        if tema in self.context.ThemeNews():
                            results.append(item)
        return results
    
class ShareView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View') 
    grok.name('vindula-content-share')
    
    
