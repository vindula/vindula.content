# -*- coding: utf-8 -*-
""" Liberiun Technologies Sistemas de Informação Ltda. """
""" Produto:                 """

from zope.interface import implements
from zope.formlib import form 
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from vindula.content import MessageFactory as _

class IVindulaCarregaPortlet(IPortletDataProvider):
      
    """A portlet
    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    field_portlet = schema.TextLine(title=_(u'label_field_portlet', default=u'Nome do campo'),
                             description=_(u'description_campo', default=u'Defina o nome do campo do conteúdo que será carregado neste portlet.'),
                             default=u'coluna',
                             required=True)
    
    value_portlet = schema.TextLine(title=_(u'label_value_portlet', default=u'Valor do campo'),
                             description=_(u'description_value', default=u'Defina o valor que será colocado no campo do conteúdo para carregar o portlet.'),
                             required=True)
    
    
    value_portlet = schema.Choice(title=_(u'label_value_portlet', default=u'Valor do campo'),
                                  description=_(u'description_value', default=u'Defina o valor que será colocado no campo do conteúdo para carregar o portlet.'),
                                  required=True,
                                  vocabulary=SimpleVocabulary([SimpleTerm(u'direita', u'direita', _(u'option_category', default=u'Coluna da Direita')),
                                                               SimpleTerm(u'esquerda', u'esquerda', _(u'option_category', default=u'Coluna da Esquerda'))])
                                  )
    


class Assignment(base.Assignment):
    """Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IVindulaCarregaPortlet)
    title = _(u'Vindula Carrega Portlet')
    
    def __init__(self, field_portlet=u'coluna',
                       value_portlet=u''):
        
        self.field_portlet = field_portlet
        self.value_portlet = value_portlet
    
    
class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('carrega_portlet.pt')            
    
    @property
    def available(self):
        if self.getPortlets():
            return True
        else:
            return False
    
    def getPortlets(self):
        context = self.context
        portal  = context.portal_url.getPortalObject()
        aq_parent = context.aq_inner
        L = []
        if aq_parent.restrictedTraverse('@@plone').isStructuralFolder():
            ctx = aq_parent
        else:
            ctx = context.aq_inner.aq_parent
        
        portlets = self.findContextualPortlet(aq_parent,[])
        recurviso = True
        
        for portlet in portlets:
            field = self.data.field_portlet
            value = self.data.value_portlet
            
            if hasattr(portlet,field):
               if portlet.__getattribute__(field) == value:
                    if portlet in ctx.objectValues():  
                        L.append(portlet)
                        if portlet.bloquea_portlet:
                            recurviso = False
                            
                    else:
                        if portlet.getActiv_recurcividade() and recurviso:
                            L.append(portlet)
        
       
        return L

    def findContextualPortlet(self,
                              context,
                              portlets):
        """ Apenas faz a busca recursiva de portlets. """
        portal = context.portal_url.getPortalObject()

        if context.restrictedTraverse('@@plone').isStructuralFolder():
            caminho = {'query': '/'.join(context.getPhysicalPath()), 'depth': 1}
            ctool = getSite().portal_catalog
            items = ctool(portal_type=('VindulaPortlet'),
                             path=caminho,
                             review_state = ['published','internal','external'],
                             sort_on='getObjPositionInParent')    
            
            #items = context.objectValues('VindulaPortlet')
            tmp = []
            for item in items:
                #if self.checaEstado(context,item):
                i = item.getObject()
                tmp.append(i) 
            
            items = tmp
        else:
            """ Nao é folderish."""
            items = []
        
        if context != portal:    
            portlets = portlets + items + self.findContextualPortlet(context.aq_inner.aq_parent,portlets)
            return portlets
        
        else:
            return portlets + items
        
    
    def checaEstado(self,context,obj,estado='published'):
        pw = context.portal_workflow
        if pw.getInfoFor(obj,'review_state') == estado:
            return True
        else:
            return False
    def can_manage_portlets(self, obj):
        mtool = getToolByName(obj, 'portal_membership')
        return mtool.checkPermission("Modify portal content", obj)        
        
        
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    
    form_fields = form.Fields(IVindulaCarregaPortlet)
    
    def create(self, data):
       return Assignment(**data)
   
class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IVindulaCarregaPortlet)
