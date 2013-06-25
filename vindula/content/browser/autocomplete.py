# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot
from AccessControl import ClassSecurityInfo

from vindula.content.models.content import ModelsContent
from vindula.content.browser.macros import Search, PDF, DOC, PPT, EXCEL

from Products.CMFCore.utils import getToolByName
from vindula.content.models.content_field import ContentField

import json

class AutocompleteView(grok.View):
    grok.context(Interface)
    grok.name('autocomplete-view')
    grok.require('zope2.View')

    result = []
    
    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.result,ensure_ascii=False)
    
    def update(self):
        form = self.request.form
        self.catalog_tool = getToolByName(self.context, 'portal_catalog')
        self.reference_tool = getToolByName(self.context, 'reference_catalog')
        self.portal = self.context.portal_url.getPortalObject()
        action = form.get('action', None)
        term = form.get('term', None)
        self.result = [] # zero a variavel com os resultados
        
        if term:
            if action == 'document-type':
                tipos = self.getTipo()
                for tipo in tipos.keys():
                    if term.lower() in tipo.lower():
                        self.result.append({'id':tipo,
                                             'name': '%s (%s)' % (tipo,tipos.get(tipo)) })
            elif action == 'structure-owner':
                self.result = self.getStructuresAndCountFile(self.portal, 'structures')
            elif action =='structure-client':
                self.result = self.getStructuresAndCountFile(self.portal, 'structuresClient')
            elif action == 'document-format':
                tipos = self.getFormatTypes()
                for tipo in tipos.keys():
                    if term.lower() in tipo.lower():
                        self.result.append({'id':tipo,
                                             'name': '%s (%s)' % (tipo,tipos.get(tipo)) })
            
            return
        
    def getStructuresAndCountFile(self, context, relationship):
        query = {}
        query['path'] = {'query':'/'.join(context.getPhysicalPath()), 'depth': 99}
        query['portal_type'] = ('OrganizationalStructure',)
        structures = self.catalog_tool(**query)
        result_structures = []
        for structure in structures:
            structure = structure.getObject()
            count_file = 0
            refs = self.reference_tool.getBackReferences(structure, relationship)
            for ref in refs:
                ref = ref.getSourceObject()
                if ref.portal_type == 'File':
                    count_file += 1
            if count_file:
                result_structures.append({'id':structure.UID(),
                                          'name': '%s (%s)' % (structure.Title(),count_file) })
        return result_structures
    
    def getTipo(self):
        return self.getIndexesValue('tipo')
    
    def getFormatTypes(self):
        content_types = self.getIndexesValue('content_type', only=PDF+DOC+PPT+EXCEL)
        checkbox = {}

        for index in content_types.keys():
            if index in PDF:
                checkbox['PDF'] = content_types.get(index)
            elif index in DOC:
                checkbox['DOC'] = content_types.get(index)
            elif index in PPT:
                checkbox['PPT'] = content_types.get(index)
            elif index in EXCEL:
                checkbox['EXCEL'] = content_types.get(index)
        return checkbox
    
    def getIndexesValue(self, index, only=[]):
        stats = {}
        index = self.catalog_tool._catalog.indexes[index]

        for key in index.uniqueValues():
            if key and (not only or str(key) in only):
                t = index._index.get(key)
                if type(t) is not int:
                    stats[str(key)] = len(t)
                else:
                    stats[str(key)] = 1
        
        return stats