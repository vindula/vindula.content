# coding: utf-8


#Imports regarding the connection of the database 'strom'
from storm.locals import *
from storm.expr import Desc, Select


from vindula.myvindula.models.base import BaseStore

    

class ContentField(Storm, BaseStore):
    __storm_table__ = 'vinapp_content_contentfield'
    
    id = Int(primary=True)
    name = Unicode()
    
    date_created = DateTime()
    date_modified = DateTime()
    date_excluded = DateTime()
    
    values = ReferenceSet(id, "ContentFieldData.field_id")
        
    def get_content_file_by_type(self,type):
        L = []
        data = self.store.find(ContentField, ContentField.name==type).one()
        if data:
            for item in data.values:
                L.append(item.value)
            
        return L