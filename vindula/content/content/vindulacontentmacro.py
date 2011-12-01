# coding=utf-8
from five import grok
from zope import schema
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.textfield import RichText
from vindula.content import MessageFactory as _
from z3c.relationfield.schema import RelationChoice

from plone.app.layout.viewlets.interfaces import IBelowContent
from zope.app.component.hooks import getSite 

from zope.interface import Interface
from plone.app.discussion.interfaces import IConversation

#from Products.CMFCore.interfaces import ISiteRoot
from zope.interface import Interface

# Interface and schema

class IVindulaContentMacro(form.Schema):
    """ Vindula Contente Macro """
    
    page = schema.TextLine(
        title=_(u"Página"),
        description=_(u"Utilizado para inserir o nome da pagina para visualização do conteudo"),
        required=True,
        )
    
    macro = schema.TextLine(
        title=_(u"Macro"),
        description=_(u"Utilizado para inserir a macro de visualização do conteudo"),
        required=True,
        )
        
  
# View
  
class VindulaContentMacroView(grok.View):
    grok.context(IVindulaContentMacro)
    grok.require('zope2.View')
    grok.name('view')
  
    

