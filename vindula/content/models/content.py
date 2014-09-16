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
    deleted = Bool(default=False)

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

    def getContent_by_uid(self,uid,is_user_object=False):
        if uid:
            if isinstance(uid, str):
                uid = uid.decode('utf-8')
            
            data = self.store.find(ModelsContent, ModelsContent.uid==uid)
            if data and not is_user_object:
                    data = data[0]
            return data
        return None
    
    def getContent_by_id(self,id):
        data = self.store.find(ModelsContent, ModelsContent.id==id).one()
        return data

    def orderBy_access(self, result_query, limit=None):
        UIDs = []
        contentAccess = []
        result = []
        for item in result_query:
            try:
                obj = item.getObject()
            except AttributeError:
                obj = item
            UIDs.append(obj.UID())

        if UIDs:
            #Acesso dirreto ao models do vindulaapp
            result = ModelsContentAccess().getContAccess(UIDs, limit)

        # for content in contentAccess:
        #     uid = content.get('content').uid
        #     for item in result_query:
        #         if item.UID == uid:
        #             result.append(item)
        #             break

        return result

    def search_catalog_by_access(self, context, rs=True, limit=None, **query):
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
        
        return self.orderBy_access(result, limit)
    
    @staticmethod
    def getAllByContentType(type, deleted=False):
        if isinstance(type, str):
            type = type.decode('utf-8')
        
        if isinstance(type, unicode):
            return ModelsContent().store.find(ModelsContent,
                                              ModelsContent.type==type,
                                              ModelsContent.deleted==deleted)

        return None
        
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    