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
from vindula.myvindula.user import BaseFunc
from vindula.myvindula.models.department import ModelsDepartment

from vindula.myvindula.tools.utils import UtilMyvindula

class IPortletEO_Gestor(IPortletDataProvider):
      
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

    implements(IPortletEO_Gestor)
    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, title_portlet=u''):
       self.title_portlet = title_portlet

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet Estrutura Hierarquica - Gestor"
    
class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('eo_Gestor.pt')            
    
    def check_content(self):
        ctx = self.context.restrictedTraverse('OrgStruct_view')(False)
        if ctx.portal_type == 'OrganizationalStructure':
            return True
        else:
            return False  
   
    def get_title(self):
        return self.data.title_portlet

#    def get_prefs_user(self, user):
#         try:
#             user_id = unicode(user, 'utf-8')    
#         except:
#             user_id = user 
#    
#         return ModelsFuncDetails().get_FuncDetails(user_id)
    
    def get_department(self, user):
        try:
            user_id = unicode(user, 'utf-8')    
        except:
            user_id = user
        
        return ModelsDepartment().get_departmentByUsername(user_id)    


    def get_EO_Context(self):
        ctx = self.context.restrictedTraverse('OrgStruct_view')(False)
        return ctx.getManager()
            
        
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    
    form_fields = form.Fields(IPortletEO_Gestor)
    
    def create(self, data):
       return Assignment(**data)
   
class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPortletEO_Gestor)
