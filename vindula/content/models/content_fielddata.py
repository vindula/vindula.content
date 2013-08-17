# coding: utf-8


#Imports regarding the connection of the database 'strom'
from storm.locals import *
from storm.expr import Desc, Select


from vindula.myvindula.models.base import BaseStoreMyvindula


class ContentFieldData(Storm, BaseStoreMyvindula):
    __storm_table__ = 'vinapp_content_contentfielddata'


    id = Int(primary=True)
    value = Unicode()
    field_id = Int()

    field = ReferenceSet(field_id, "ContentField.id")

