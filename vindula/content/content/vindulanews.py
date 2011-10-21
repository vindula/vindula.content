# coding=utf-8
from five import grok
from zope import schema
from plone.directives import dexterity, form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.textfield import RichText
from plone.namedfile.field import NamedFile
from vindula.themedefault import MessageFactory as _
from z3c.relationfield.schema import RelationList, RelationChoice

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
#            navigation_tree_query = {'path': {'query':'/banco-de-imagens'}},
        ),
        required=False,
        )
    
    imageCaption = schema.TextLine(
        title=_(u"Título da Imagem "),
        required=False,        
        )
    
# Methods   
    
class VindulaNews(dexterity.Item):        
    grok.implements(IVindulaNews)
    
    def getNews(self):
        return 'news'

# View
    
class SampleView(grok.View):
    grok.context(IVindulaNews)
    grok.require('zope2.View')
    grok.name('view')