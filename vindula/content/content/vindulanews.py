# coding=utf-8
from five import grok
from zope import schema
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.textfield import RichText
from vindula.themedefault import MessageFactory as _
from z3c.relationfield.schema import RelationChoice

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