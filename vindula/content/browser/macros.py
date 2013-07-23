# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.content import ContentHistoryView
from vindula.content.models.content import ModelsContent
from vindula.content.models.content_access import ModelsContentAccess

from vindula.myvindula.models.funcdetails import FuncDetails
from vindula.myvindula.models.confgfuncdetails import ModelsConfgMyvindula
from vindula.myvindula.models.dados_funcdetail import ModelsDadosFuncdetails
from vindula.myvindula.tools.utils import UtilMyvindula

from plone.app.uuid.utils import uuidToObject

from datetime import datetime

from collections import OrderedDict

PDF = ['application/pdf', 'application/x-pdf', 'image/pdf']
DOC = ['application/msword']
PPT = ['application/vnd.ms-powerpoint', 'application/powerpoint', 'application/mspowerpoint', 'application/x-mspowerpoint']
EXCEL = ['application/vnd.ms-excel', 'application/msexcel', 'application/x-msexcel']

class Search(object):

    def __init__(self, context, query={}, rs=True):
        portal_catalog = getToolByName(context, 'portal_catalog')
        path = context.portal_url.getPortalObject().getPhysicalPath()

        if rs:
            query.update({'review_state': ['published', 'internally_published', 'external']})

        query.update({'path': {'query':'/'.join(path)},
                      'sort_on':'created',
                      'sort_order':'descending',
                     })

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

            actor = history.get('actor',{})
            if actor:
                actor = actor.get('username','')
            if actor:
                actor = self.get_prefs_user(actor)
            if actor:
                L.append({'actor': actor.get('name',''),
                          # 'action':  history.get('transition_title',''),
                          # 'type': tipo,
                          'date':date,})
        return L

class MacroListtabularView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.name('macro_tabular_file')
    grok.require('zope2.View')

    def list_files(self, subject, keywords, structures, portal_type):
        if 'list_files[]' in self.request.keys() or 'list_files' in self.request.keys():
            values = self.request.get('list_files[]', self.request.get('list_files'))
            if values:
                try:
                    if isinstance(values, str):
                        values = eval(values)
                except NameError:
                    values = [values]

                if 'Pessoas' in portal_type:
                    try:
                        return [FuncDetails(self.Convert_utf8(username)) for username in values]
                    except (SyntaxError, NameError):
                        return [FuncDetails(self.Convert_utf8(values))]
                else:
                    try:
                        return [uuidToObject(uuid) for uuid in values]
                    except (SyntaxError, NameError):
                        return [uuidToObject(values)]
            else:
                return []
                
        if 'Pessoas' in portal_type:
            itens = FuncDetails.get_AllFuncDetails(self.Convert_utf8(subject))
        else:
            itens = self.busca_catalog(subject, keywords, structures, portal_type)
        return itens

    def busca_catalog(self, subject, keywords, structures, portal_type):
        rtool = getToolByName(self.context, "reference_catalog")
        list_files = []
        review_state = True

        if isinstance(portal_type, str):
            portal_type = eval(portal_type)
        query = {'portal_type': portal_type}

        if subject:
            query['SearchableText'] = subject

        if keywords and keywords != 'null':
            query['Subject'] = keywords

        if 'File' in portal_type:
            review_state = False

        search = Search(self.context,query,rs=review_state)
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
        try:
            #Retorna o valor do metodo passado
            result = getattr(item, attr)()
        except AttributeError:
            return {'value': '',
                    'name': ''}
        except TypeError:
            #Retorna o valor do atributo passado
            result = getattr(item, attr)

        try:
            return {'value': result.Title(),
                    'name': result.Title(),
                    'type': result.portal_type,
                    'url': result.absolute_url(),}
        except AttributeError:
            try:
                return {'value': result,
                        'name': item.Title(),
                        'type': item.portal_type,
                        'url': item.absolute_url(),}
            except AttributeError:
                return {'value': result,
                        'name': result}
        except TypeError:
            return {'value': result,
                    'name': result}

    def getUIDS(self, obj_list):
        try:
            if not isinstance(obj_list, list): obj_list = [obj_list]
        except AttributeError:
             pass

        try:
            return [i.UID() for i in obj_list]
        except TypeError:
            return [i.UID for i in obj_list]
        except AttributeError:
            return obj_list
        
    def getUserName(self, obj_list):
        try:
            if not isinstance(obj_list, list): obj_list = [obj_list]
        except AttributeError:
             pass

        try:
            return [i.username for i in obj_list]
        except AttributeError:
            return obj_list

class MacroFilterView(grok.View):
    grok.context(Interface)
    grok.name('macro_filter_file')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(MacroFilterView,self).__init__(context, request)
        self.catalog_tool = getToolByName(self.context, 'portal_catalog')
        self.reference_tool = getToolByName(self.context, 'reference_catalog')
        self.portal = self.context.portal_url.getPortalObject()
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

    #Funcao que retorna o total de itens de cada vador de um determaninado indice
    #Se passar qtd=None retorna todos os itens
    def getTopIndex(self, index, qtd=5, only=[]):
        stats = {}
        index = self.catalog_tool._catalog.indexes[index]
        for key in index.uniqueValues():
            if key and (not only or str(key) in only):
                t = index._index.get(key)
                if type(t) is not int:
                    stats[str(key)] = len(t)
                else:
                    stats[str(key)] = 1

        od = OrderedDict(sorted(stats.items(), key=lambda t: t[1]))
        items = od.items()
        items.reverse()
        
        if qtd:
            items = items[:qtd]
            
        return OrderedDict(items)
        
    #Funcao que retorna o as estruturas organizacionais e seus arquivos relacionados
    def getCountFilesByStructure(self, relationship, qtd=5):
        query = {}
        query['path'] = {'query':'/'.join(self.portal.getPhysicalPath()), 'depth': 99}
        query['portal_type'] = ('OrganizationalStructure',)
        query['review_state'] = ['published', 'internally_published', 'external']
        structures = self.catalog_tool(**query)
        result_structures = {}
        for structure in structures:
            structure = structure.getObject()
            count_file = 0
            refs = self.reference_tool.getBackReferences(structure, relationship)
            for ref in refs:
                ref = ref.getSourceObject()
                if ref.portal_type == 'File':
                    count_file += 1
            if count_file:
                result_structures[structure] = count_file

        od = OrderedDict(sorted(result_structures.items(), key=lambda t: t[1]))
        items = od.items()
        items.reverse()
        return OrderedDict(items[:qtd])

    def getFormatTypes(self):
        content_types = self.getTopIndex('content_type', only=PDF+DOC+PPT+EXCEL)
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

    def getStructureSelected(self):
        context = self.context
        try:
            structure = context.getStructure()
            if structure:
                return structure.UID()
            else:
                return self.getSuperStructure(context)
        except AttributeError:
            return None

    def getPortalTypes(self):
        context = self.context
        types = ['File',]
        if context.portal_type == 'ServicosFolder':
            types = ['Servico']
        try:
            types = context.getObject_type()
            if isinstance(types, str):
                types = [types]
        except AttributeError:
            return types

        return types

    def getAllSubjects(self):
        return self.pc.uniqueValuesFor("Subject")
    
    def getSuperStructure(self, context):
        if context.portal_type == 'OrganizationalStructure':
            return context.UID()
        if context.portal_type == 'Plone Site':
            return None
        else:
            return self.getSuperStructure(context.aq_parent)
    
    #Metodo retorna as unidades/localizacoes das estruras organizacionais
    def getUnitLocations(self, qtd=5):
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
        
        od = OrderedDict(sorted(result_units.items(), key=lambda t: t[1]))
        items = od.items()
        items.reverse()
        return OrderedDict(items[:qtd])
    
    def getValuesField(self, field, qtd=5):
        field = ModelsConfgMyvindula().get_configuration_By_fields(field)
        items = []
        if field:
            items = field.choices.splitlines()
            if items:
                items = sorted(items)
        return items[:qtd]
    
    def getValuesByFieldName(self, field_name, is_object=False, qtd=5):
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
        
        od = OrderedDict(sorted(items.items(), key=lambda t: t[1]))
        items = od.items()
        items.reverse()
        return OrderedDict(items[:qtd])
    
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
        review_state = True

        try:
            portal_type = eval(portal_type)
        except TypeError:
            pass
        except NameError:
            pass

        query = {'portal_type': portal_type}
        if 'File' in portal_type:
            review_state = False

        result = ModelsContent().search_catalog_by_access(context=self.context, rs=review_state, **query)
        return result

    def get_url_typeIcone(self, obj):
        base = self.context.portal_url() + "/++resource++vindula.content/images/"
        if obj.content_type in ['application/pdf', 'application/x-pdf', 'image/pdf']:
            url = base + "icon-pdf.png"
        elif obj.content_type == 'application/msword':
            url = base + "icon-word.png"
        elif obj.content_type in ['application/vnd.ms-powerpoint', 'application/powerpoint', 'application/mspowerpoint', 'application/x-mspowerpoint']:
            url = base + "icon-ppoint.png"
        elif obj.content_type in ['application/vnd.ms-excel', 'application/msexcel', 'application/x-msexcel']:
            url = base + "icon-excel.png"
        else:
            url = base + "icon-default.png"

        return url

    def ger_mount_access(self, obj):
        result = ModelsContentAccess().getContAccess([obj.UID()])
        if result:
            result = result[0].get('count')
        return result
    
    def getExtension(self, obj):
        if obj.content_type in PDF:
            return ".PDF"
        elif obj.content_type in DOC:
            return ".DOC"
        elif obj.content_type in PPT:
            return ".PPT"
        elif obj.content_type in EXCEL:
            return ".XLS"

        return None

class MacroRecentView(MacroMoreAccessViews):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro_recent_content')


    def contaTitulo(self, titulo):
	return len(titulo())


    def list_files(self, portal_type):
        list_files = []

        query = {'portal_type': portal_type}
        search = Search(self.context, query, rs=False)
        list_files = search.result

        return list_files
    
    def getExtension(self, obj):
        if obj.content_type in PDF:
            return ".PDF"
        elif obj.content_type in DOC:
            return ".DOC"
        elif obj.content_type in PPT:
            return ".PPT"
        elif obj.content_type in EXCEL:
            return ".XLS"

        return None

class MacroComboStandard(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-comboStandard-content')

class MacroRating(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-rating-content')

class MacroShare(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-share-content')


class MacroFollow(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-follow-content')
    
    
class MacroMessage(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-message-content')


class MacroLastAccess(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-last_access-content')


class MacroSeeAlso(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-see_also-content')


    def getItens(self):
        context = self.context
        query = {'portal_type':(context.portal_type)}
        query['Subject'] = context.getRawSubject()

        result = ModelsContent().search_catalog_by_access(context=self.context,
                                                           **query)

        return result

    def getImagem(self,obj):
        if hasattr(obj, 'getImageIcone'):
            return obj.getImageIcone()
        else:
            return ''
