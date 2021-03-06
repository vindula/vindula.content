# -*- coding: utf-8 -*-
import hashlib
import json

from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.uuid.utils import uuidToObject
from vindula.myvindula.cache import *
from vindula.myvindula.models.confgfuncdetails import ModelsConfgMyvindula
from vindula.myvindula.models.dados_funcdetail import ModelsDadosFuncdetails
from zope.interface import Interface

from vindula.content.browser.macros import PDF, DOC, PPT, EXCEL


#from redis_cache import cache_it

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
                #TODO:
                #Ver como passar o portal_type atraves do JS para fazer a pesquisa somente pelos tipos de conteudos certos
                #Nesse momento foi removido a cantagem de arquivos ex: 'Tipo 1 (12)'
                for tipo in tipos.keys():
                    if term.lower() in tipo.lower():
                        self.result.append({'id':tipo,
                                             'name': '%s' % (tipo) })
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
            elif action == 'unit-type':
                tipos_unidade = self.getIndexesValue('tipounidade')
                for tipo in tipos_unidade.keys():
                    if term.lower() in tipo.lower():
                        self.result.append({'id':tipo,
                                             'name': '%s' % (tipo) })
            elif action == 'unit-location':
                units = self.getUnitLocations()
                for uid in units.keys():
                    if term.lower() in units[uid].lower():
                        self.result.append({'id':uid,
                                            'name': '%s' % (units[uid]) })
            elif action == 'cargo':
                cargos = self.getValuesField('cargo')
                for cargo in cargos:
                    if term.lower() in cargo.lower():
                        self.result.append({'id':cargo,
                                            'name': '%s' % (cargo) })
            elif action == 'activity':
                atividades = self.getValuesField('atividades')
                for atividade in atividades:
                    if term.lower() in atividade.lower():
                        self.result.append({'id':atividade,
                                            'name': '%s' % (atividade) })
            elif action == 'main-structure':
                structures = self.getValuesByFieldName('unidadeprincipal', True)
                for structure in structures.keys():
                    if structure and (term.lower() in structure.Title().lower() or term.lower() in structure.getSiglaOrTitle().lower()):
                        self.result.append({'id':structure.UID(),
                                            'name': '%s (%s)' % (structure.getSiglaOrTitle(), structures[structure]) })
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
        return self.getTopIndexByPortalType('tipo')
    
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
    
    def getTopIndexByPortalType(self, name_index, portal_types=[]):
        key = hashlib.md5('%s:%s' %(name_index,portal_types)).hexdigest()
        key = 'Biblioteca:getTopIndexByPortalType::%s' % key
        data = get_redis_cache(key)
        if not data:
            stats = {}
            query = {'path': {'query':'/'.join(self.portal.getPhysicalPath()), 'depth': 99}}
            
            if portal_types:
                query['portal_type'] = portal_types
            
            index = self.catalog_tool._catalog.indexes[name_index]
            for index_key in index.uniqueValues():
                if index_key:
                    query[name_index] = index_key
                    items = self.catalog_tool(query)
                    if items:
                        stats[index_key] = len(items)

            data = stats
            set_redis_cache(key,'Biblioteca:getTopIndexByPortalType:keys',data,3600)
        return data
    
    def getUnitLocations(self):
        query = {}
        query['path'] = {'query':'/'.join(self.portal.getPhysicalPath()), 'depth': 99}
        query['portal_type'] = ('Unit',)
        query['review_state'] = ['published', 'internally_published', 'external']
        units = self.catalog_tool(**query)
        result_units = {}
        
        for unit in units:
            unit = unit.getObject()
            if self.reference_tool.getBackReferences(unit, 'units'):
                result_units[unit.UID()] = unit.Title()
        
        return result_units
    
    def getValuesField(self, field, qtd=5):
        field = ModelsConfgMyvindula().get_configuration_By_fields(field)
        items = []
        if field:
            items = field.choices.splitlines()
            if items:
                items = sorted(items)
        return items
    
    def getValuesByFieldName(self, field_name, is_object=False):
        values = ModelsDadosFuncdetails.get_DadosFuncdetails_byFieldName(field_name)
        items = {}
        for value in values:
            if is_object:
                try:
                    value = eval(value.value)
                    value = value[0]
                except(SyntaxError, NameError):
                    value = value.value
                value = uuidToObject(value)
            else:
                value = value.value
                
            if items.get(value):
                items[value] += 1
            else:
                items[value] = 1
        
        return items