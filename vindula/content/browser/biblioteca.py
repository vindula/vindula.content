# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot
from AccessControl import ClassSecurityInfo

from vindula.content.models.content import ModelsContent


from Products.CMFCore.utils import getToolByName

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




class BlibliotecaView(grok.View):
    grok.context(Interface)
    grok.name('biblioteca-view')
    grok.require('zope2.View')

    themes = []

    def update(self):
        form = self.request.form
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        self.themes = form.get('themes[]',[])
        structures = form.get('structures[]',[])

        if not isinstance(self.themes,list):
            self.themes = [self.themes]

        if not isinstance(structures,list):
            structures = [structures]

        if not self.themes:
            self.themes = portal_catalog.uniqueValuesFor("ThemeNews")

        query = {'portal_type':('OrganizationalStructure',)}

        if structures:
            query['UID'] = structures

        search = Search(self.context,query)
        self.structures = search.result




class MacroListFileView(grok.View):
    grok.context(Interface)
    grok.name('macro_list_file')
    grok.require('zope2.View')

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.rtool = getToolByName(context, 'reference_catalog')
        super(MacroListFileView,self).__init__(context, request)



    def list_files(self, theme, structures, sort_on):
        list_files = []

        if theme:
            list_files = self.searchFile_byTheme([theme],sort_on)
        elif structures:
            list_files = self.searchFile_byStructures(structures,sort_on)


        return list_files


    def searchFile_byStructures(self, structures=None, sort_on='access'):
        result = []

        if structures:
            object = structures.getObject()
            refs = self.rtool.getBackReferences(object, 'structures', targetObject=None)
            for ref in refs:
                obj = ref.getSourceObject()
                if obj.portal_type == 'File':
                    result.append(obj)

        return result

    def searchFile_byTheme(self, keywords=[], sort_on='access'):
        query = {}
        result = []

        query['portal_type'] = ('File',)

        if keywords:
            query['ThemeNews'] = keywords

        search = Search(self.context,query,rs=False)
        result_query = search.result

        if sort_on == 'access':
            for item in ModelsContent().orderBy_access(result_query):
                result.append(item.get('content').getObject())
        else:
            result = result_query

        return result



class MacroListtabularView(grok.View):
    grok.context(Interface)
    grok.name('macro_tabular_file')
    grok.require('zope2.View')

    def list_files(self, keywords, portal_type):
        list_files = []

        query = {'portal_type': ('File',)}
        if keywords:
            query['SearchableText'] = keywords

        search = Search(self.context,query,rs=False)
        list_files = search.result

        return list_files


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
            result = seacrh.result

        return result

    def tabular_filter(self, ):
        pass