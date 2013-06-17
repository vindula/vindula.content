# coding: utf-8


#Imports regarding the connection of the database 'strom'
from storm.locals import *
from storm.expr import Desc, Select


from vindula.myvindula.models.base import BaseStoreMyvindula



class ContentField(Storm, BaseStoreMyvindula):
    __storm_table__ = 'vinapp_content_contentfield'

    id = Int(primary=True)
    name = Unicode()
    values = ReferenceSet(id, "ContentFieldData.field_id")

    def get_content_file_by_type(self,type):
        L = []
        data = self.store.find(ContentField, ContentField.name==type, ContentField.deleted==False).one()
        if data:
            for item in data.values:
                if not item.deleted:
                    L.append(item.value)

        return L