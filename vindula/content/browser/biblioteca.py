# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot
from AccessControl import ClassSecurityInfo

from vindula.content.models.content_access import ModelsContentAccess

from Products.CMFCore.utils import getToolByName


class BlibliotecaView(grok.View):
    grok.context(Interface)
    grok.name('biblioteca-view')
    grok.require('zope2.View')
    
    themes = []
    
    def update(self):
        portal_catalog = getToolByName(self.context, 'portal_catalog')
         
        self.themes = portal_catalog.uniqueValuesFor("ThemeNews")
        
        path = self.context.portal_url.getPortalObject().getPhysicalPath()
        query = {'portal_type':('OrganizationalStructure',),
                 'path': {'query':'/'.join(path)},
                 'review_state': ['published', 'internally_published', 'external'],
                 'sort_on':'effective',
                 'sort_order':'descending',}
        
        self.structures = portal_catalog(**query)
        
        



class MacroListFileView(grok.View):
    grok.context(Interface)
    grok.name('macro_list_file')
    grok.require('zope2.View')
    
    def __init__(self, context, request):
        self.request = request
        self.context = context
        self.pc = getToolByName(context, 'portal_catalog')
        self.rtool = getToolByName(context, 'reference_catalog')
    
    
    
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
        #keywords = [i for i in keywords if i != '']
        
        path = self.context.portal_url.getPortalObject().getPhysicalPath()
        
        query['portal_type'] = ('File',)
        #query['review_state'] = ['published', 'internally_published', 'external']
        query['path'] = {'query':'/'.join(path)}
        
        if sort_on != 'access':
            query['sort_on'] = sort_on #'effective'
        
        query['sort_order'] = 'descending'
        if keywords:
            query['ThemeNews'] = keywords

        result_query = self.pc(**query)
        if sort_on == 'access':
            result = self.orderBy_access(result_query)
        else:
            result = result_query            
                
        return result


    def orderBy_access(self,result_query ):
        hashs = []
        contentAccess = []
        result = []
        for item in result_query:
            obj = item.getObject()
            hashs.append(obj.UID())
        
        if hashs:
            #Acesso dirreto ao models do vindulaapp 
            contentAccess = ModelsContentAccess().getContAccess(hashs)
        
        for content in contentAccess:
            uid = content.get('content').uid 
            for item in result_query:
                if item.UID == uid:
                    result.append(item)
                    break
        return result


    
class MacroListtabularView(grok.View):
    grok.context(Interface)
    grok.name('macro_tabular_file')
    grok.require('zope2.View')        
    
    
    def list_files(self, theme, structures, sort_on):
        list_files = []
        search = MacroListFileView(self.context,self.request)
    
        
        list_files = search.searchFile()
         
        return list_files
    
    
    