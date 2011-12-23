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

    
    form.fieldset('settings', label=u"Settings",
                  fields=['activ_comment','activ_share'])

#    activ_comment = schema.Bool(
#                title=_(u'label_activ_comment', default=u'Ativar Comentario'),
#                description=_(u'help_activ_comment', default=u'Se selecionado, Ativa a opção de comentarios deste conteudo'),
#                default=True
#                )

    activ_share = schema.Bool(
                title=_(u'label_activ_share', default=u'Ativar Compartilhamento'),
                description=_(u'help_activ_share', default=u'Se selecionado, Ativa a opção de compartilhamento entre redes sociais'),
                default=True
                )
   
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


