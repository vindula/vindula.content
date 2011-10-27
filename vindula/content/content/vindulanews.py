# coding=utf-8
from five import grok
from zope import schema
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.textfield import RichText
from vindula.themedefault import MessageFactory as _
from z3c.relationfield.schema import RelationChoice

from plone.app.layout.viewlets.interfaces import IBelowContent 

from zope.interface import Interface
from plone.app.discussion.interfaces import IConversation

#from Products.CMFCore.interfaces import ISiteRoot
from zope.interface import Interface

# Interface and schema

class IVindulaNews(form.Schema):
    """ Vindula News """
    
    title = schema.TextLine(
        title=_(u"Título"),
        )
    
    summary = schema.Text(
        title=_(u"Sumário"),
        description=_(u"Utilizado nas listagens de itens e resultado de buscas"),
        required=False,
        )
    
    text = RichText(
        title=_(u"Corpo do texto"),
        required=False,
        )
    
    image = RelationChoice(
        title=_(u"Imagem"),
        description=_(u"Será exibido na listagem de notícias e na própria notícia. A imagem será redimensionada para um tamanho adequado."),
        source=ObjPathSourceBinder(
            portal_type = 'Image',
            ),
        required=False,
        )
    
    imageCaption = schema.TextLine(
        title=_(u"Título da Imagem "),
        required=False,        
        )
    
# View
    
class VindulaNewsView(grok.View):
    grok.context(IVindulaNews)
    grok.require('zope2.View')
    grok.name('view')
    
 
    
class ShareView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View') 
    grok.name('vindula-content-share')
    
class VindulaCommentsView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View') 
    grok.name('vindula-comments-view')
    
    def render(self):
        pass
    
    def cont_comments(self, context):
        conversation = IConversation(context)
        if conversation.total_comments > 0:
            return conversation.total_comments
        else:
            return 0
    