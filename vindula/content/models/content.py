# coding: utf-8


#Imports regarding the connection of the database 'strom'
from storm.locals import *
from storm.expr import Desc, Select


from vindula.myvindula.models.base import BaseStore
from vindula.content.models.content_access import ModelsContentAccess

from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

class ModelsContent(Storm, BaseStore):
    __storm_table__ = 'vinapp_social_content'

    #Campos de edição
    id = Int(primary=True)
    hash = Unicode()
    type = Unicode()
    uid = Unicode()
    username = Unicode()

    date_created = DateTime()
    date_modified = DateTime()

    def getObject(self):
        reference_catalog = getToolByName(getSite(), "reference_catalog")

        return reference_catalog.lookupObject(self.uid)


    def getContent_by_hash(self,hash):
        data = self.store.find(ModelsContent, ModelsContent.hash==hash).one()
        if data:
            return data
        else:
            return None

    def getContent_by_uid(self,uid):
        data = self.store.find(ModelsContent, ModelsContent.uid==uid).one()
        return data


    def orderBy_access(self,result_query ):
        UIDs = []
        contentAccess = []
        result = []
        for item in result_query:
            obj = item.getObject()
            UIDs.append(obj.UID())

        if UIDs:
            #Acesso dirreto ao models do vindulaapp
            result = ModelsContentAccess().getContAccess(UIDs)

        # for content in contentAccess:
        #     uid = content.get('content').uid
        #     for item in result_query:
        #         if item.UID == uid:
        #             result.append(item)
        #             break

        return result


    def search_catalog_by_access(self, context, rs=True, **query):
        portal_catalog = getToolByName(context, 'portal_catalog')
        path = query.get('path')

        if not path:
            path = context.portal_url.getPortalObject().getPhysicalPath()

        if rs and 'File' not in query.get('portal_type'):
            query.update({'review_state': ['published', 'internally_published', 'external']})
        
        query.update({'path': {'query':'/'.join(path)},
                     'sort_on':'effective',
                     'sort_order':'descending',})
        
        result = portal_catalog(**query)
        
        return self.orderBy_access(result)