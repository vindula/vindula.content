# -*- coding: utf-8 -*-
from collections import OrderedDict

from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.uuid.utils import uuidToObject
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.interface import Interface

from vindula.content.browser.macros import Search
from vindula.content.models.content import ModelsContent


class BlibliotecaView(grok.View):
    grok.context(Interface)
    grok.name('biblioteca-view')
    grok.require('cmf.SetOwnPassword')

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

        context_biblioteca = self.context.restrictedTraverse('myvindula-conf-userpanel').check_context_biblioteca()
        if context_biblioteca:
            context_path = self.context.aq_parent.getPhysicalPath()
            query['path'] = {'query':'/'.join(context_path), 'depth':99}

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

    def getPath_biblioteca(self):
        context_biblioteca = self.context.restrictedTraverse('myvindula-conf-userpanel').check_context_biblioteca()
        if context_biblioteca:
            context_path = self.context.aq_parent.getPhysicalPath()
            return '/'.join(context_path)

        return None



class MacroListFileView(grok.View):
    grok.context(Interface)
    grok.name('macro_list_file')
    grok.require('zope2.View')

    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.rtool = getToolByName(context, 'reference_catalog')
        self.ctool = getToolByName(context, 'portal_catalog')
        super(MacroListFileView,self).__init__(context, request)

    def getRowCssClass(self):
        return '<div class=XXcolumns large-3XX>\n<div class=XXrowXX>'.replace('XX','"')

    def list_files(self, type, value, sort_on):
        list_files = []
        if type == 'theme':
            list_files = self.searchFile_byTheme([value],sort_on)
        elif type == 'structure':
            list_files = self.searchFile_byStructures(value,sort_on)

        return list_files

    def getRequestItems(self):
        request = self.request
        if 'list_files[]' in request.keys() or 'list_files' in request.keys():
            values = request.get('list_files[]', request.get('list_files'))
            type = request.get('type')
            if values:
                if type == 'structure':
                    L = []
                    try:
                        if isinstance(values, str):
                            values = eval(values)
                            
                        for uuid in values:
                            obj = uuidToObject(uuid)
                            if obj:
                                struc = obj.getStructures()
                                if struc not in L:
                                    L.append(struc)
                        return L
#                        return [uuidToObject(uuid).getStructures() for uuid in values if uuidToObject(uuid)]
                    except (NameError, SyntaxError):
                        return [uuidToObject(values).getStructures()]
                else:
                    themes = self.request.get('document-theme[]', self.request.get('document-theme'))
                    if themes:
                        try:
                            if isinstance(themes, str):
                                themes = eval(themes)
                            return themes
                        except (SyntaxError, NameError):
                            return [themes]
                    else:
                        return self.getAllKeyword('ThemeNews').keys()

    def getStructures_byUID(self,UID):
        if UID:
            object = self.rtool.lookupObject(UID)
            return object #.Title()
        else:
            return self.context


    def searchFile_byStructures(self, structures=None, sort_on='access'):
        result = []

        if structures:
            if isinstance(structures, str):
                object = self.rtool.lookupObject(structures)
            else:
                try:
                    object = structures.getObject()
                except AttributeError:
                    #O objeto já veio como Objeto nao como Brain
                    object = structures

            refs = self.rtool.getBackReferences(object, 'structures', targetObject=None)
            result_query = []
            for ref in refs:
                obj = ref.getSourceObject()
                if obj.portal_type == 'File':
                    result_query.append(obj)
            
            if result_query:
                if sort_on == 'access':
                    for item in ModelsContent().orderBy_access(result_query):
                        result.append(item.get('content').getObject())
                else:
                    result = sorted(result_query, key=lambda res: res.created(), reverse=True)
                    
        return result

    def searchFile_byTheme(self, keywords=[], sort_on='access'):
        query = {}
        result = []

        query['portal_type'] = ('File',)
        
        context_biblioteca = self.context.restrictedTraverse('myvindula-conf-userpanel').check_context_biblioteca()
        if context_biblioteca:
            if "context_path" in self.request.keys():
                context_path = self.request['context_path']
                query['path'] = {'query': context_path, 'depth':99}    
            else:
                context_path = self.context.aq_parent.getPhysicalPath()
                query['path'] = {'query':'/'.join(context_path), 'depth':99}

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

    def get_url_typeIcone(self, obj):
        base = self.context.portal_url() + "/++resource++vindula.content/images/"
        if obj.content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',\
                                  'application/vnd.openxmlformats-officedocument.wordprocessingml.template']:
            url = base + "icon-word.png"
        elif obj.content_type in ['application/vnd.ms-powerpoint', 'application/powerpoint', 'application/mspowerpoint', 'application/x-mspowerpoint',\
                                  'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.openxmlformats-officedocument.presentationml.slideshow']:
            url = base + "icon-ppoint.png"
        elif obj.content_type in ['application/vnd.ms-excel', 'application/msexcel', 'application/x-msexcel',\
                                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.template']:
            url = base + "icon-excel.png"
        elif obj.portal_type in ['VindulaPhotoAlbum']:
            photos = obj.contentValues()
            if photos:
                url = photos[0].absolute_url()+'/image_preview'
            else:
                url = base + "icon-default.png"
        
        elif obj.portal_type in ['VindulaVideo']:
            photo = obj.getImage_preview()
            if photo:
                url = photo.absolute_url()+'/image_preview'
            else:
                url = base + "icon-default.png"
        else:
            url = base + "icon-default.png"

        return url

    def getUIDS(self, obj_list):
        try:
            obj_list.count
            if not isinstance(obj_list, list): obj_list = [obj_list]
        except AttributeError:
             pass

        try:
            return [i.UID() for i in obj_list]
        except TypeError:
            return [i.UID for i in obj_list]
        except AttributeError:
            return obj_list

    def getAllKeyword(self, name_index):
        stats = {}
        index = self.ctool._catalog.indexes[name_index]

        for key in index.uniqueValues():
            if key:
                t = index._index.get(key)
                if type(t) is not int:
                    stats[str(key)] = len(t)
                else:
                    stats[str(key)] = 1
        return stats
    
    def sortItems(self, type, items):
        D = {}
        for item in items:
            if type =='structure':
                objects = self.searchFile_byStructures(item)
            else:
                objects = self.searchFile_byTheme(item)
            
            D[item] = len(objects)
        
        od = OrderedDict(sorted(D.items(), key=lambda t: t[1]))
        items = od.items()
        items.reverse()
        
        return OrderedDict(items)
    
    def normalizeString(self, string=''):
        if string:
            normalizer = getUtility(IIDNormalizer)
            return normalizer.normalize(string) 
        return ''
            

class FilterItensView(grok.View):
    grok.context(Interface)
    grok.name('list-filter')
    grok.require('zope2.View')


    def getItems(self):
        request = self.request
        self.catalog_tool = getToolByName(self.context, 'portal_catalog')
        self.reference_tool = getToolByName(self.context, 'reference_catalog')
        items = []
        theme = request.form.get('theme')
        structure = request.form.get('structures')

        if theme:
            portal = self.context.portal_url.getPortalObject()
            items = self.catalog_tool({'portal_type': ['File',],
                                       'path': {'query': '/'.join(portal.getPhysicalPath()), 'depth': 99},
                                       # 'review_state': ['published', 'internally_published', 'external'],
                                       'ThemeNews': theme,
                                       })
            items = [i.getObject() for i in items]

        elif structure:
            structure = uuidToObject(structure)
            refs = self.reference_tool.getBackReferences(structure, 'structures')
            for ref in refs:
                ref = ref.getSourceObject()
                if ref.portal_type == 'File':
                    items.append(ref)

        return items


