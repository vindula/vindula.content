# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot
from AccessControl import ClassSecurityInfo

from vindula.content.models.content import ModelsContent
from vindula.content.browser.macros import Search

from Products.CMFCore.utils import getToolByName


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

    def getStructures(self):
        self.update()
        return self.structures

    def getThemes(self):
        self.update()
        return self.themes





class MacroListFileView(grok.View):
    grok.context(Interface)
    grok.name('macro_list_file')
    grok.require('zope2.View')

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.rtool = getToolByName(context, 'reference_catalog')
        super(MacroListFileView,self).__init__(context, request)

    def getRowCssClass(self,):
        return '<div class=XXcolumns large-3XX><div class=XXrowXX>'.replace('XX','"')

    def list_files(self, theme, structures, sort_on):
        list_files = []

        if theme:
            list_files = self.searchFile_byTheme([theme],sort_on)
        elif structures:
            list_files = self.searchFile_byStructures(structures,sort_on)
        
        return list_files

    def getStructures_byUID(self,UID):
        if UID:
            object = self.rtool.lookupObject(UID)
            return object.Title()
        else:
            return None


    def searchFile_byStructures(self, structures=None, sort_on='access'):
        result = []

        if structures:
            if isinstance(structures, str):
                object = self.rtool.lookupObject(structures)
            else:
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