# -*- coding: utf-8 -*-
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements
from zope import schema

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.cache import render_cachekey
from plone.app.portlets.portlets import base


class IVindulaSocialPortlet(IPortletDataProvider):


    title_portlet = schema.TextLine(title=_(u"Título"),
                                  description=_(u"Título que aparecerá no cabeçalho do portlet."),
                                  required=True)

    action = schema.TextLine(title=_(u'Ação do Vindula api'),
                             description=_(u'Ação do vindula api.'),
                             required=True,
                             default=u'')
    
    remove_title = schema.Bool(title=_(u"Remover título"),
                            description=_(u"Se ativado remove o título inserido acima."),
                            default=False)

class Assignment(base.Assignment):
    implements(IVindulaSocialPortlet)

    def __init__(self,title_portlet=u'', action=u'', remove_title=''):

        self.title_portlet = title_portlet
        self.action = action
        self.remove_title = remove_title


    @property
    def title(self):
        return _(u"Portlet Vindula Social")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('vindulasocial.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

#    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    def get_title(self):
        return self.data.title_portlet

    def get_action(self):
        return self.data.action


class AddForm(base.AddForm):
    form_fields = form.Fields(IVindulaSocialPortlet)
    label = _(u"Adicionar Vindula Social Portlet")
    description = _(u"Este portlet mostra as aplicações do vindula api.")

    def create(self, data):
       return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IVindulaSocialPortlet)
    label = _(u"Editar Vindula Social Portlet")
    description = _(u"Este portlet mostra as aplicações do vindula api.")

