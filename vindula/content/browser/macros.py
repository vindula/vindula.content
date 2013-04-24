# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.content import ContentHistoryView
from vindula.content.models.content import ModelsContent

from vindula.myvindula.tools.utils import UtilMyvindula

from datetime import datetime


class Search(object):

    def __init__(self, context, query={}, rs=True):
        portal_catalog = getToolByName(context, 'portal_catalog')
        path = context.portal_url.getPortalObject().getPhysicalPath()

        if rs:
            query.update({'review_state': ['published', 'internally_published', 'external']})

        query.update({'path': {'query':'/'.join(path)},
                     'sort_on':'effective',
                     'sort_order':'descending',})

        self.result = portal_catalog(**query)




class MacroPropertiesView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-propertis-content')


    def __init__(self,context,request):
        super(MacroPropertiesView,self).__init__(context,request)
        owner = context.getOwner()
        username = owner.getUserName()
        self.dadosUser = self.get_prefs_user(username)

        self.creator = self.dadosUser.get('name')
        self.creation_date = context.creation_date.strftime('%d/%m/%Y')
        self.responsible = self.dadosUser.get('email')


    def gethistory(self):
        context = self.context
        HistoryView = ContentHistoryView(context, context.REQUEST)

        content_history = HistoryView.fullHistory() or []
        L = []
        for history in content_history:
            tipo = history.get('type','')
            if tipo == 'workflow':
                date = history.get('time','').strftime('%d/%m/%Y')
            else:
                date = datetime.fromtimestamp(history.get('time','')).strftime('%d/%m/%Y')

            actor = self.get_prefs_user(history.get('actor',{}).get('username',''))

            L.append({'actor': actor.get('name',''),
                      # 'action':  history.get('transition_title',''),
                      # 'type': tipo,
                      'date':date,})

        return L

class MacroListtabularView(grok.View):
    grok.context(Interface)
    grok.name('macro_tabular_file')
    grok.require('zope2.View')

    def list_files(self, subject, keywords, structures, portal_type):
        rtool = getToolByName(self.context, "reference_catalog")
        list_files = []
        if isinstance(portal_type, str):
            portal_type = eval(portal_type)
        query = {'portal_type': portal_type}

        if subject:
            query['SearchableText'] = subject

        if keywords and keywords != 'null':
            query['Subject'] = keywords

        search = Search(self.context,query,rs=False)
        list_files = search.result

        if structures and structures != 'null':

            if not isinstance(structures,list):
                structures = [structures]

            result = []
            for structure in structures:
                object = rtool.lookupObject(structure)

                refs = rtool.getBackReferences(object, 'structures', targetObject=None)
                for ref in refs:
                    obj = ref.getSourceObject()
                    if obj.portal_type in portal_type:
                        result.append(obj)

            list_files = result

        return list_files
    def getValueField(self, item, attr):
        result = getattr(item, attr)()
        try:
            return {'value': result.Title(),
                    'name': result.Title(),
                    'url': result.absolute_url(),}
        except AttributeError:
            return {'value': result,
                    'name': item.Title(),
                    'url': item.absolute_url(),}

class MacroFilterView(grok.View):
    grok.context(Interface)
    grok.name('macro_filter_file')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(MacroFilterView,self).__init__(context, request)
        self.request = request
        self.context = context
        self.pc = getToolByName(context, 'portal_catalog')


    def list_filter(self, is_theme,is_structures):
        result = []
        if is_theme:
            result = self.pc.uniqueValuesFor("ThemeNews")

        elif is_structures:
            query = {'portal_type':('OrganizationalStructure',)}

            search = Search(self.context,query)
            result = search.result

        return result

    def tabular_filter(self, ):

        search = Search(self.context,{'portal_type':('OrganizationalStructure',)})

        return {'tags': self.pc.uniqueValuesFor("Subject"),
                'structures' :search.result}




class MacroCommentsView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-comments-content')


class MacroRelatedItems(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-relateditens-content')


class MacroKeywords(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-keywords-content')


class MacroMoreAccessViews(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro_more_access_content')


    def list_files(self, portal_type):
        list_files = []
        rs = True

        query = {'portal_type': portal_type}
        if 'File' in portal_type:
            rs=False

        result = ModelsContent().search_catalog_by_access(context=self.context,
                                                          rs=rs,
                                                          **query)
        return result

class MacroComboStandard(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-comboStandard-content')


class MacroRating(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-rating-content')
