# -*- coding: utf-8 -*-
import hashlib
from collections import OrderedDict
from datetime import datetime

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from five import grok
from plone.app.layout.viewlets.content import ContentHistoryView
from plone.app.uuid.utils import uuidToObject
from vindula.myvindula.cache import *
from vindula.myvindula.models.confgfuncdetails import ModelsConfgMyvindula
from vindula.myvindula.models.dados_funcdetail import ModelsDadosFuncdetails
from vindula.myvindula.models.funcdetails import FuncDetails
from vindula.myvindula.tools.utils import UtilMyvindula
from zope.interface import Interface

from vindula.content.models.content import ModelsContent
from vindula.content.models.content_access import ModelsContentAccess


#from redis_cache import cache_it


PDF = ['application/pdf', 'application/x-pdf', 'image/pdf']
DOC = ['application/msword']
PPT = ['application/vnd.ms-powerpoint', 'application/powerpoint', 'application/mspowerpoint', 'application/x-mspowerpoint']
EXCEL = ['application/vnd.ms-excel', 'application/msexcel', 'application/x-msexcel']

class Search(object):

    def __init__(self, context, query={}, rs=True,):
        portal_catalog = getToolByName(context, 'portal_catalog')

        if not 'path' in query.keys():
            portal_path = context.portal_url.getPortalObject().getPhysicalPath()
            query.update({'path': {'query':'/'.join(portal_path)}})

        if rs:
            query.update({'review_state': ['published', 'internally_published', 'external']})

        query.update({'sort_on':'created',
                      'sort_order':'descending',
                     })

        self.result = portal_catalog(**query)

class MacroPropertiesView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-propertis-content')


    def __init__(self,context,request):
        super(MacroPropertiesView,self).__init__(context,request)
        # import pdb; pdb.set_trace()
        #TODO: ver porque não está funcionando isso quando o usuário que cria o conteúdo é o admin
        try:
            owner = context.getOwner()
            username = owner.getUserName()
            self.dadosUser = self.get_prefs_user(username)

            self.creator = self.dadosUser.get('name')
            self.creation_date = context.creation_date.strftime('%d/%m/%Y')
            self.responsible = self.dadosUser.get('email')
        except:
            pass


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
    
    def print_text(self,text):
        print text

    def getItem(self,username):
        return FuncDetails(username)

    #@cache_it(limit=1000, expire=60 * 60 * 24, db_connection=get_redis_connection())
    def list_files(self, subject, keywords, structures, theme, portal_type, fields=None, list_files=[], path=None):
        p_membership = getToolByName(self.context, 'portal_membership')
        current_user = p_membership.getAuthenticatedMember()
        current_username = current_user.getUserName()
        if 'list_files[]' in self.request.keys() or 'list_files' in self.request.keys():
            values = self.request.get('list_files[]', self.request.get('list_files'))
            if values:
                try:
                    if isinstance(values, str):
                        values = eval(values)
                except (SyntaxError, NameError):
                    values = [values]
                
                if 'Pessoas' in portal_type:
                    #Retorna a lista de usernames para a template trabalhar
                    return values
                else:
                    try:
                        objs = [uuidToObject(uuid) for uuid in values]
                    except (SyntaxError, NameError):
                        objs = [uuidToObject(values)]
                    
                    return self.geraDicForFields(objs, fields)
            else:
                return []
        else:
            #TODO: Solucao temporaria, fazer funcionar o decorator

            #Adciono o usuario logado a chave do redis, pois cada usuario pode ter privilégios diferentes de ver o conteudo
            key = hashlib.md5('%s:%s:%s:%s:%s:%s:%s:%s' %(subject,keywords,structures,theme,portal_type,fields,path,current_username)).hexdigest()
            key = 'Biblioteca:list_files::%s' % key
            cached_data = get_redis_cache(key)
            if 'Pessoas' in portal_type:
                return FuncDetails.get_AllFuncUsernameList(self.Convert_utf8(subject))
            elif not cached_data:
                itens = self.busca_catalog(subject, keywords, structures, theme, portal_type, path, current_user)
                itens_dict = self.geraDicForFields(itens, fields)
                set_redis_cache(key,'Biblioteca:list_files:keys',itens_dict,600)
                return itens_dict
            else:
                return cached_data
    
    def geraDicForFields(self, object_list, fields):
        result = []
        for i in object_list:
            item_fields = []
            for f in fields:
                field_dic = {}
                for att in f.items():
                    if att[1]:
                        if att[0] == 'attribute':
                            field_dic['data_value'] = self.getValueField(i, att[1])
                        else:
                            field_dic[att[0]]=att[1]
                item_fields.append(field_dic)
            item_UID = i.UID
            if not isinstance(item_UID,str):
                item_UID = i.UID()
            result.append({'UID':item_UID,
                           'portal_type':i.portal_type,
                           'fields':item_fields})
        return result
    
    def busca_catalog(self, subject, keywords, structures, theme, portal_type, path, current_user):
        rtool = getToolByName(self.context, "reference_catalog")
        p_workflow = getToolByName(self.context, "portal_workflow")
        
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
            
        if theme:
            query['ThemeNews'] = theme

        
        if path:
            query['path'] = {'query': path }


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
                        if path \
                           and path not in '/'.join(obj.getPhysicalPath()):
                            continue
                        
                        if obj.portal_type == 'Servico':
                            #Verifico se o objeto do tipo SERVICO é publico, se não for verifico de o usuario que está acessando tem permissão de ver o conteúdo se sim adiciona o obj na listagem
                            if p_workflow.getInfoFor(obj, 'review_state') in ['published', 'internally_published', 'external'] \
                                or self.hasPermission(current_user, obj):
                                result.append(obj)
                            else:
                                continue
                        else:
                            result.append(obj)
            list_files = result
        return list_files
    
    #Verifica se o usuario tem permissao de ver o objeto ou se é manager 
    def hasPermission(self, user, obj):
        user_roles = user.getRolesInContext(obj)
        if 'Reader' in user_roles or \
            'Manager' in user_roles:
            return True
        
        return False
    
    def getValueField(self, item, attr):
        data_object = {} 
        
        try:
            item = item.getObject()
        except AttributeError:
            pass
        
        try:
            #Retorna o valor do metodo passado
            result = getattr(item, attr)()
        except AttributeError:
            return  {'value': '',
                     'name': ''}
        except TypeError:
            #Retorna o valor do atributo passado
            result = getattr(item, attr)

        try:
            data_object = {'value': result.Title(),
                           'name': result.Title(),
                           'type': result.portal_type,
                           'url': result.absolute_url(),}
        except AttributeError:
            try:
                data_object = {'value': result,
                               'name': item.Title(),
                               'type': item.portal_type,
                               'url': item.absolute_url(),}
            except:
                try:
                    data_object = {'value': result,
                                   'name': item.Title,
                                   'type': item.portal_type,
                                   'url': item.getObject().absolute_url(),}
                except AttributeError:
                    data_object = {'value': result,
                                   'name': result}
        except TypeError:
            data_object = {'value': result,
                           'name': result}

        if isinstance(data_object.get('value', ''), DateTime):
            data_object['value'] = data_object['value'].strftime('%d/%m/%Y as %H:%M')
            
        return data_object

#    def getUIDS(self, obj_list):
#        try:
#            if not isinstance(obj_list, list) and \
#               not isinstance(obj_list, LazyMap): 
#                obj_list = [obj_list]
#        except AttributeError:
#             pass
#
#        try:
#            return [i.UID() for i in obj_list]
#        except TypeError:
#            return [i.UID for i in obj_list]
#        except AttributeError:
#            return obj_list
    
    def getUIDS(self, dict_obj_list):
        return [i.get('UID') for i in dict_obj_list]
    
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
        key = hashlib.md5('%s:%s:%s' %(index,qtd,only)).hexdigest()
        key = 'Biblioteca:getTopIndex::%s' % key

        data = get_redis_cache(key)
        if not data:
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
            
            data = OrderedDict(items)
            set_redis_cache(key,'Biblioteca:getTopIndex:keys',data,3600)

        return data
    
    def getTopIndexByPortalType(self, name_index, portal_types=[], qtd=5,):
        key = hashlib.md5('%s:%s:%s' %(name_index,portal_types,qtd)).hexdigest()
        key = 'Biblioteca:getTopIndexByPortalType::%s' % key

        data = get_redis_cache(key)
        if not data:
            stats = {}
            query = {'path': {'query':'/'.join(self.portal.getPhysicalPath()), 'depth': 99}}
            
            if portal_types:
                query['portal_type'] = portal_types
            
            index = self.catalog_tool._catalog.indexes[name_index]
            for key_index in index.uniqueValues():
                if key_index:
                    query[name_index] = key_index
                    items = self.catalog_tool(query)
                    if items:
                        stats[key_index] = len(items)

            od = OrderedDict(sorted(stats.items(), key=lambda t: t[1]))
            items = od.items()
            items.reverse()
            
            if qtd:
                items = items[:qtd]
            
            data = OrderedDict(items)
            set_redis_cache(key,'Biblioteca:getTopIndexByPortalType:keys',data,3600)

        return data
    
    #Funcao que retorna os status dos documentos
    def getDocsStatus(self):
        data = {'True': 'Vigente',
                'False': 'Vencido'}  

        return data
        
    #Funcao que retorna o as estruturas organizacionais e seus arquivos relacionados
    def getCountFilesByStructure(self, relationship, qtd=5):
        key = hashlib.md5('%s:%s' % (relationship,qtd)).hexdigest()
        key = 'Biblioteca:getCountFilesByStructure::%s' % key

        data = get_redis_cache(key)
        if not data:
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
            items = OrderedDict(items[:qtd])
            data = []
            for i in items.keys():
                item = {'UID':i.UID(),
                        'title':i.getSiglaOrTitle(),
                        'qtd':items.get(i)}
                data.append(item)

            set_redis_cache(key,'Biblioteca:getTopIndex:keys',data,3600)

        return data

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
        key = generate_cache_key('vindula.content:Macros:getValuesField',field=field,qtd=str(qtd))
        items = get_redis_cache(key)
        if not items:
            field = ModelsConfgMyvindula().get_configuration_By_fields(field)
            items = []
            if field:
                items = field.choices.splitlines()
                if items:
                    items = sorted(items)

            items = items[:qtd]
            set_redis_cache(key,'vindula.content:Macros:getValuesField:keys',items,7200)
        return items

    def getFiltroUnidade(self, field_name, is_object=False, qtd=5):
        key = generate_cache_key('vindula.content:Macros:getFiltroUnidade',
                                 field_name=field_name,
                                 is_object=str(is_object),
                                 qtd=str(qtd))
        L =  get_redis_cache(key)
        if not L:
            items = self.getValuesByFieldName(field_name, is_object, qtd)
            L = []
            for item in items:
                if item:
                    item_dict = {'UID':item.UID(),
                                 'sigla':item.getSiglaOrTitle(),
                                 'qtd':items.get(item)}
                    L.append(item_dict)
            set_redis_cache(key,'vindula.content:Macros:getFiltroUnidade:keys',L,7200)
        return L

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
        items = OrderedDict(items[:qtd])
        return items
    
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

    def list_files(self, portal_type, path=None):
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

        if path:
            query['path'] = path.split('/')

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
    
    def limitTextSize(self, text, size=100):
        if len(text) > size:
            i = size
            try:
                while text[i] != " ":
                    i += 1
                return text[:i]+'...'
            except IndexError:
                return text
        else:
            return text

class MacroRecentView(MacroMoreAccessViews):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro_recent_content')


    def contaTitulo(self, titulo):
           return len(titulo())

    def list_files(self, portal_type, path=None):
        list_files = []
        if isinstance(portal_type, str):
            try:
                portal_type = eval(portal_type)
            except NameError:
                pass
            except TypeError:
                pass
        
        query = {'portal_type': portal_type}

        if path:
            query['path'] = {'query': path }
        
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
        query = {'portal_type': (context.portal_type),
                 'Subject': context.getRawSubject()}

        result = ModelsContent().search_catalog_by_access(context=context, **query)
        items = [brain for brain in result if brain.get('content').uid != context.UID()]
        
        return items

    def getImagem(self,obj):
        if hasattr(obj, 'getImageIcone'):
            return obj.getImageIcone()
        else:
            return ''
        
class StructureModal(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('modal-structure')
    
    def convertUIDToStructure(self, UID):
        return uuidToObject(UID);
    
    
    
    
    
    
    
    
