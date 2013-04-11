# coding: utf-8


#Imports regarding the connection of the database 'strom'
from storm.locals import *
from storm.expr import Desc, Select


from vindula.myvindula.models.base import BaseStore


class ContentFieldData(Storm, BaseStore):
    __storm_table__ = 'vinapp_content_contentfielddata'
    
    
    id = Int(primary=True)
    value = Unicode()
    field_id = Int()
    
    date_created = DateTime()
    date_modified = DateTime()
    date_excluded = DateTime()
    
    field = ReferenceSet(field_id, "ContentField.id")        

