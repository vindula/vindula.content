# -*- coding: utf-8 -*-
""" Liberiun Technologies Sistemas de Informação Ltda. """
""" Produto:                 """

from zope.interface import implements
from zope.formlib import form 
from zope import schema

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.component.hooks import getSite

class IVindulaCarregaPortlet(IPortletDataProvider):
      
    """A portlet
    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    title_portlet = schema.TextLine(title=unicode("Título", 'utf-8'),
                                  description=unicode("Título para do portlet.", 'utf-8'),
                                  required=True)
    
    
class Assignment(base.Assignment):
    """Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IVindulaCarregaPortlet)
    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, title_portlet=u''):
       self.title_portlet = title_portlet

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Vindula Carrega Portlet"
    
class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('carrega_portlet.pt')            
    
    def get_title(self):
        return self.data.title_portlet
    
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
