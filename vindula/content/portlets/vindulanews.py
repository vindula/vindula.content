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


class IVindulaNewsPortlet(IPortletDataProvider):
    
    
    title_portlet = schema.TextLine(title=_(u"Título"),
                                  description=_(u"Título que aparecerá no cabeçalho do portlet."),
                                  required=True)

    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)

    state = schema.Tuple(title=_(u"Workflow state"),
                         description=_(u"Items in which workflow state to show."),
                         default=('published', ),
                         required=True,
                         value_type=schema.Choice(
                             vocabulary="plone.app.vocabularies.WorkflowStates")
                         )
    
    folder_news = schema.Choice(title=_(u"Local das Notícias"),
                                description=_(u"Selecione o local das notícias. \
                                                Se nada for selecionado, o sistema irá buscar notícias em todo o portal."),
                                required=False,
                                source=SearchableTextSourceBinder({'portal_type': ('Folder','VindulaFolder')},
                                                                  default_query='path:')
                                )

    show_data = schema.Bool(title=_(u'Exibir Data e Hora da criação'),
                            description=_(u'Se selecionado, mostrará a data e horário de criação da notícia.'),
                            default=True)
    
    show_autor = schema.Bool(title=_(u'Exibir Autor'),
                            description=_(u'Se selecionado, mostrará o autor da notícia.'),
                            default=True)
    

class Assignment(base.Assignment):
    implements(IVindulaNewsPortlet)

    def __init__(self,title_portlet=u'', count=5, state=('published', ),folder_news=None,
                      show_data=True,show_autor=True):
        
        self.title_portlet = title_portlet
        self.count = count
        self.state = state
        
        self.folder_news = folder_news
        
        self.show_data = show_data
        self.show_autor = show_autor

    @property
    def title(self):
        return _(u"Portlet Vindula News")


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('vindulanews.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

#    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return self.data.count > 0 and len(self._data())

    def published_news_items(self):
        return self._data()

    def all_news_link(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request),
            name=u'plone_portal_state')
        portal = portal_state.portal()
        if 'news' in getNavigationRootObject(context, portal).objectIds():
            return '%s/news' % portal_state.navigation_root_url()
        return None

    @memoize
    def _data(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        
        if self.data.folder_news:
            path = portal_state.navigation_root_path() + self.data.folder_news
        else:
            path = portal_state.navigation_root_path()
        
        limit = self.data.count
        state = self.data.state
        return catalog(portal_type='VindulaNews',
                       review_state=state,
                       path=path,
                       sort_on='Date',
                       sort_order='reverse',
                       sort_limit=limit)[:limit]


class AddForm(base.AddForm):
    form_fields = form.Fields(IVindulaNewsPortlet)
    label = _(u"Adicionar Vindula News Portlet")
    description = _(u"Este portlet mostra as notícias mais recentes.")

    form_fields['folder_news'].custom_widget = UberSelectionWidget

    def create(self, data):
       return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IVindulaNewsPortlet)
    label = _(u"Editar Vindula News Portlet")
    description = _(u"Este portlet mostra as notícias mais recentes.")
    
    form_fields['folder_news'].custom_widget = UberSelectionWidget
    
