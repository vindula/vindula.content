# -*- coding: utf-8 -*-
""" Liberiun Technologies Sistemas de Informação Ltda. """
""" Produto:                 """

from zope.interface import implements
from zope.formlib import form 
from zope import schema

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.CMFCore.utils import getToolByName

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IPortletEstruturaHierarquica(IPortletDataProvider):
      
    """A portlet
    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    title_portlet = schema.TextLine(title=unicode("Título", 'utf-8'),
                                  description=unicode("Título que aparecerá no cabeçalho do portlet.", 'utf-8'),
                                  required=True)
    
    
class Assignment(base.Assignment):
    """Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPortletEstruturaHierarquica)
    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, title_portlet=u''):
       self.title_portlet = title_portlet

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet Estrutura Hierarquica"
    
class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('portlet_estrutura_hierarquica.pt')            
    
    def get_title(self):
        return self.data.title_portlet

    def get_OrgStructureRelationship(self, obj):
        pc = getToolByName(self.context, 'portal_catalog')
        objs = pc(portal_type='OrganizationalStructure',
                review_state='published',
                path={'query':'/'})
        L =[]
        for item in objs:
            i = item .getObject()
            if i.getStructures:
                if obj == i.getStructures():
                    L.append(i)
        return L
    
    def get_RelationshipContext(self):
        ctx = self.context
        L =[]
        if ctx.getStructures():
            L.append(ctx)
            ctx = ctx.getStructures()
            while ctx.getStructures():
                L.append(ctx)
                ctx = ctx.getStructures()
            else:
                L.append(ctx)
        else:
            L.append(ctx)
        L.reverse()        
        return L

#    def get_NavigationContext(self):
#        relacionado = self.get_RelationshipContext()
#        L=[]
#        for item in relacionado:
#            D={}
#            objetos = self.get_OrgStructureRelationship(item)
#            D['objeto'] = item
#            D['relacionado'] = objetos
#            L.append(D)
#
#        cont = 1
#        for i in L:
#            quant = len(L)-1
#            if cont <= quant:
#                relacionado = i['relacionado']
#                item = L[cont]['objeto']
#                if item in relacionado:
#                    i['relacionado'].remove(item)
#                    L[cont]['nivelDown'] = True
#                cont += 1
#                
#        return L       
        
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    
    form_fields = form.Fields(IPortletEstruturaHierarquica)
    
    def create(self, data):
       return Assignment(**data)
   
class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPortletEstruturaHierarquica)
