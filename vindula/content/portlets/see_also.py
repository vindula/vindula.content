# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.formlib import form
from zope import schema

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base


from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


from vindula.content.models.content import ModelsContent


class IPortletSeeAlso(IPortletDataProvider):

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

    implements(IPortletSeeAlso)
    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, title_portlet=u''):
       self.title_portlet = title_portlet

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet Veja Também"




class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('see_also.pt')

    def get_title(self):
        return self.data.title_portlet

    @property
    def available(self):
        itens = self.getItens()
        if itens:
            return True
        else:
            return False


    def getItens(self):
        context = self.context
        query = {'portal_type':(context.portal_type)}
        query['Subject'] = context.getRawSubject()

        result = ModelsContent().search_catalog_by_access(context=self.context,
                                                           **query)

        return result



class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    form_fields = form.Fields(IPortletSeeAlso)

    def create(self, data):
       return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPortletSeeAlso)
