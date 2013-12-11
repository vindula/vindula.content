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

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget, UberMultiSelectionWidget
from vindula.content import MessageFactory as _


class IPortletListagem(IPortletDataProvider):
      
    """A portlet
    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    title_portlet = schema.TextLine(title=unicode("Título", 'utf-8'),
                                  description=unicode("Título que aparecerá no cabeçalho do portlet.", 'utf-8'),
                                  required=True)

    folder_context = schema.Choice(title=_(u"Contexto raiz"),
                               	   description=_(u"Selecione o context raiz da listagem."),
                               	   required=True,
                               	   source=SearchableTextSourceBinder({'portal_type': ['Folder','VindulaFolder']},
                             	   default_query='path:')
                                  )
    
    
class Assignment(base.Assignment):
    """Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IPortletListagem)
    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, title_portlet=u'',folder_context=None):
       self.title_portlet = title_portlet
       self.folder_context = folder_context


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet de Listagem"
    
class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('portlet_listagem.pt')            
   
    def get_title(self):
        return self.data.title_portlet

    def get_context(self):
        context = self.context
        portal = context.portal_url.getPortalObject()
        catalog = portal.portal_catalog
        portal_path = '/'.join(portal.getPhysicalPath())

        data = self.data
        rid = catalog.getrid(portal_path + data.folder_context)
        brain = catalog._catalog[rid]
        return brain.getObject()

    def get_itensMenu(self, context,wf_enable=True):
        itens = []
        if context:
            catalog = getToolByName(context, 'portal_catalog')
            local = context.getPhysicalPath()
            query={'sort_on': 'getObjPositionInParent',
                   'path':{'query':'/'.join(local), 'depth': 1},
                  }
            if wf_enable:
            	query['review_state'] = ['published','internal']

            itens = catalog(**query)
        return itens

    def get_imagem(self,item):
		context = self.context
		portal = context.portal_url()

		return "%s/%s" %(portal,item.getIcon())

       
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    
    form_fields = form.Fields(IPortletListagem)
    form_fields['folder_context'].custom_widget = UberSelectionWidget
    
    def create(self, data):
       return Assignment(**data)
   
class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPortletListagem)
    form_fields['folder_context'].custom_widget = UberSelectionWidget

    def create(self, data):
       return Assignment(**data)
