# -*- coding: utf-8 -*-
import transaction
from five import grok
from zope.interface import Interface
from vindula.content.content.interfaces import IOrganizationalStructure

from Products.CMFCore.utils import getToolByName
from vindula.myvindula.tools.utils import UtilMyvindula

grok.templatedir('templates')

class OrganizationalStructureView(grok.View, UtilMyvindula):
    grok.context(IOrganizationalStructure)
    grok.require('zope2.View')
    grok.name('view_organizational')


    def getDefaultValue(self,lado):
        context = self.context
        layout = context.get(lado)

        return layout

    # def get_UID(self):
    #     return IUUID(self.context)

    # def get_howareu_departament(self, departament):
    #     D={}
    #     D['visible_area'] = departament
    #     return ModelsMyvindulaHowareu().get_myvindula_howareu(**D)

    # def get_department(self, user):
    #     try:
    #         user_id = unicode(user, 'utf-8')
    #     except:
    #         user_id = user

    #     # return ModelsDepartment().get_departmentByUsername(user_id)
    #     return 'TODO MUDAR DEPOIS'

    # def get_LastContent(self):
    #     ctool = getSite().portal_catalog
    #     objs = ctool(path = {'query': '/'.join(self.context.getPhysicalPath()), 'depth': 1},
    #                   sort_on='modified', sort_order='decrescent')

    #     if objs:
    #         return objs
    #     else:
    #         return []


class FolderOrganizationalStructureView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('folder-organizational-structure')

    def getCategorias(self):
        return OrganizationalStructure(self.context).voc_categoria();

    def getOrgStruc(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        L = []

        if 'categoria' in self.request.form.keys():
            categoria = self.request.form.get('categoria')

        if categoria:
            results = catalog(portal_type='OrganizationalStructure',
                      review_state='published',
                      categoria = categoria,
                      )
            if results:
                for item in results:
                    item = item.getObject()
                    D = {}
                    D['title'] = item.Title()
                    D['url'] =   item.absolute_url()
                    L.append(D)
        return L


class NewTemplateOrgStrucView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('new-org-struc')


class NewTemplateUnidadeOrgView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('new-unidade-org')

class ImportUnidadeOrgView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('import-unidade-org')

    def importCSV(self):
        #TODO: Testar com arquivos gerados no windows
        #TODO: Consertar upload de arquivo e escolha do contexto da importação
        rows = open('/tmp/unidades.csv','ro').readlines()
        folder = self.context

        #PARTE GENERICA QUE RETORNA LISTA DE DICTS
        columns = rows[:1]
        rows = rows[1:]
        data = []

        if columns:
            columns = columns[0].replace('\n','').split(';')

        for row in rows:
            row_dict = {}
            for column in enumerate(columns):
                row_fields = row.replace('\n','').split(';')
                row_dict[columns[column[0]]] = row_fields[0]

            data.append(row_dict)
        #######################################################

        retorno = []
        for row in data:
            obj_pai = self.context.portal_catalog({'id':row['unidade_pai'].lower(),
                                                   'portal_type':'OrganizationalStructure'})

            obj_unidade = self.context.portal_catalog({'id':row['localizacao'].lower(),
                                                       'portal_type':'Unit'})

            if obj_pai:
                obj_pai = obj_pai[0].getObject().UID()
                obj_pai = self.context.portal_catalog({'UID':obj_pai})[0].getObject()
            else:
                obj_pai = ''

            if obj_unidade:
                obj_unidade = obj_unidade[0].getObject().UID()
                obj_unidade = self.context.portal_catalog({'UID':obj_unidade})[0].getObject()
            else:
                obj_unidade = ''

            objeto = {'type_name':'OrganizationalStructure',
                      'siglaunidade':row['siglaunidade'],
                      'id':row['siglaunidade'].lower(),
                      'title': row['titulo'],
                      'unidadeEspecial': True,
                      'tipounidade': u'',
                      'employees':[],
                      'manager':'administrador',
                      'vice_manager': 'administrador',
                      'tipounidade':row['tipounidade'],
                      }
            try:
                obj = folder.invokeFactory(**objeto)
                obj = self.context[obj]
                obj.setStructures(obj_pai)
                obj.setUnits(obj_unidade)

                obj.at_post_create_script()
                transaction.commit()
                result = '%s: Conteúdo criado com sucesso.<br>' % row['siglaunidade']
            except:
                result = '%s: Objeto já existe.<br>' % row['siglaunidade']

            retorno.append(result)

        return ''.join(retorno)
