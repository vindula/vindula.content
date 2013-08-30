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

from plone.app.discussion.interfaces import IConversation
from vindula.controlpanel.vocabularies import ControlPanelMacro


class IVindulaContentAPI(form.Schema):
    """ Vindula Contente API """
    
    action = schema.TextLine(title=_(u'Ação do Vindula Api'),
                             description=_(u'Ação do Vindula Api.'),
                             required=True,
                             default=u'')

    
    deactivate_title = schema.Bool(
        title=_(u"Desativar título"),
        description=_(u'Selecione este campo para desativar o título do Content Macro'),
        required=False,
    )
  
# View
 
class VindulaContentAPIView(grok.View):
    grok.context(IVindulaContentAPI)
    grok.require('zope2.View')
    grok.name('view')
  
    def get_action(self):
        return self.context.action