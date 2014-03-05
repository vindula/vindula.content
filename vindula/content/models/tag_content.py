# coding: utf-8

#Imports regarding the connection of the database 'storm'
from storm.locals import *
from zope.component.hooks import getSite


from vindula.myvindula.models.base import BaseStoreMyvindula


class TagContent(Storm, BaseStoreMyvindula):
    __storm_table__ = 'vinapp_content_tagcontent'

    id = Int(primary=True)
    type =Unicode()
    value = Unicode()
    description = Unicode()
    
    
    def getUrlIcon(self):
        site_obj = getSite()
        if site_obj:
            return '%s/vindula-api/content/tag-picture/%s' % (site_obj.absolute_url(), self.id)
    
    @staticmethod
    def getTagById(id, deleted=False):
        if not isinstance(id, int):
            try:
                id = int(id)
            except:
                return None
        
        data = TagContent().store.find(TagContent, 
                                       TagContent.id==id, 
                                       TagContent.deleted==deleted)
        
        if data.count():
            return data.one()
        
        return None
    
    @staticmethod
    def getAllTagsByType(type, deleted=False):
        
        if not isinstance(type, unicode):
            type = unicode(type)
        
        data = TagContent().store.find(TagContent, 
                                       TagContent.type==type,
                                       TagContent.deleted==deleted).order_by(TagContent.value)
        
        if data.count():
            return data
        
        return []