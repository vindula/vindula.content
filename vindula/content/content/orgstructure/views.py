# -*- coding: utf-8 -*-
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