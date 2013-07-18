# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.CMFCore.interfaces import ISiteRoot
from AccessControl import ClassSecurityInfo
from plone.app.uuid.utils import uuidToObject

from vindula.content.models.content import ModelsContent
from vindula.content.browser.macros import Search, PDF, DOC, PPT, EXCEL

from Products.CMFCore.utils import getToolByName
from vindula.content.models.content_field import ContentField

from datetime import datetime
import json

class SearchFileterView(grok.View):
    grok.context(Interface)
    grok.name('searchfilter-view')
    grok.require('zope2.View')

    result = []
    
    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.result,ensure_ascii=False)
    
    def update(self):
        context = self.context
        form = self.request.form
        self.portal = context.portal_url.getPortalObject()
        self.catalog_tool = getToolByName(context, 'portal_catalog')
        self.reference_tool = getToolByName(context, 'reference_catalog')
        self.all_structures = []
        
        query = {}
        references = {}
        unit_locations = []
        self.result = []
        has_searchable_text = False
        
        query['path'] = {'query':'/'.join(self.portal.getPhysicalPath()), 'depth': 99}
        query['portal_type'] = ['File',]
        start = False
        end = False

        for item in form.items():
            field, values = item[0], item[1]
            field = field.replace('[', '').replace(']', '')
            if values:
                if field == 'document-type':
                    if 'all' in values:
                        values = self.getAllKeyword('tipo')
                        values = values.keys()
                    query['tipo'] = values
                elif field == 'document-classification':
                    if 'all' in values:
                        values = self.getAllKeyword('classificacao')
                        values = values.keys()
                    query['classificacao'] = values
                elif field == 'date-start':
                    start = datetime.strptime(values, '%d/%m/%Y')
                elif field == 'date-end':
                    end = datetime.strptime(values, '%d/%m/%Y')
                elif field == 'SearchableText':
                    query['SearchableText'] = '*%s*' % values
                elif field == 'document-theme':
                    query['ThemeNews'] = values
                elif field == 'document-format':
                    query['content_type'] = eval(values)
                elif field == 'document-subject': 
                    query['Subject'] = values
                elif field == 'unit-type':
                    if(values.find(',') != -1):
                        values = values.split(',')
                    if 'all' in values:
                        values = self.getAllKeyword('tipounidade')
                        values = values.keys()
                    query['tipounidade'] = values
                elif field == 'structure-owner':
                    if not isinstance(values, list): values = [values]
                    if 'all' in values:
                        if self.all_structures:
                            objs = self.all_structures
                        else:
                            self.all_structures = self.getAllStructures()
                            objs = self.all_structures
                    else:
                        objs = [uuidToObject(uuid) for uuid in values if uuid]
                    references['structures'] = objs
                elif field == 'structure-client':
                    if not isinstance(values, list): values = [values]
                    if 'all' in values:
                        if self.all_structures:
                            objs = self.all_structures
                        else:
                            self.all_structures = self.getAllStructures()
                            objs = self.all_structures
                    else:
                        objs = [uuidToObject(uuid) for uuid in values if uuid]
                    references['structuresClient'] = objs
                elif field == 'unit-location':
                    if not isinstance(values, list): values = [values]
                    if 'all' in values:
                        unit_locations = self.getAllUnits()
                    else:
                        unit_locations = [uuidToObject(uuid) for uuid in values if uuid]
                elif field == 'structure-selected':
                    query['path']['query'] = '/'.join(uuidToObject(values).getPhysicalPath())
                elif field == 'portal-types':
                    try:
                        if isinstance(values, str):
                            values = eval(values)
                    except NameError:
                        values = [values]
                    query['portal_type'] = values

        if start or end:
            if not start:
                query['effective'] = {'query':end, 'range': 'max'}
            elif not end:
                query['effective'] = {'query':start, 'range': 'min'}
            else:
                query['effective'] = {'query':(start, end), 'range': 'min:max'}
        
        if not 'File' in query.get('portal_type'):
            query['review_state'] = ['published', 'internally_published', 'external']
        
        
        files = self.catalog_tool(**query)
        files = [i.UID for i in files]
        if query.get('tipo') or \
           query.get('classificacao') or \
           query.get('effective') or \
           query.get('SearchableText') or \
           query.get('tipounidade'):
            self.result = files
        
        aux_list_structures = []
        for reference in references.items():
            relationship, objs = reference[0], reference[1]
            for obj in objs:
                refs = self.reference_tool.getBackReferences(obj, relationship)
                for ref in refs:
                    ref_obj = ref.getSourceObject()
                    if query.get('SearchableText'):
                        has_searchable_text = True
                        if ref_obj.UID() in self.result and \
                           ref_obj.portal_type in query.get('portal_type'):
                            aux_list_structures.append(ref_obj.UID())
                    else:
                        if ref_obj.UID() not in self.result and \
                           ref_obj.portal_type in query.get('portal_type'):
                            self.result.append(ref_obj.UID())
            
        if has_searchable_text and references: 
            self.result = aux_list_structures
            return
        
        aux_list_units = []
        for location in unit_locations:
            refs = self.reference_tool.getBackReferences(location, 'units')
            for ref in refs:
                ref_obj = ref.getSourceObject()
                if query.get('SearchableText'):
                    if ref_obj.UID() in self.result and \
                       ref_obj.portal_type in query.get('portal_type'):
                        aux_list_units.append(ref_obj.UID())
                else:
                    if ref_obj.UID() not in self.result and \
                       ref_obj.portal_type in query.get('portal_type'):
                        self.result.append(ref_obj.UID())
                        
        if has_searchable_text and unit_locations: 
            self.result = aux_list_structures
            return

        #verificar a logica disso
        if not self.result and \
           not unit_locations and \
           not references:
            self.result = files
            
        return
    
    def getAllStructures(self):
        structures = self.catalog_tool({'path': {'query':'/'.join(self.portal.getPhysicalPath()), 'depth': 99},
                                        'portal_type': ('OrganizationalStructure',),
                                        })
        if structures:
            return [i.getObject() for i in structures]
        
    def getAllUnits(self):
        units = self.catalog_tool({'path': {'query':'/'.join(self.portal.getPhysicalPath()), 'depth': 99},
                                        'portal_type': ('Unit',),
                                        })
        if units:
            return [i.getObject() for i in units]
        
    
    def getAllKeyword(self, name_index):
        stats = {}
        index = self.catalog_tool._catalog.indexes[name_index]

        for key in index.uniqueValues():
            if key:
                t = index._index.get(key)
                if type(t) is not int:
                    stats[str(key)] = len(t)
                else:
                    stats[str(key)] = 1
        return stats