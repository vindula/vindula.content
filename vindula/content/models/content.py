# coding: utf-8


#Imports regarding the connection of the database 'strom'
from storm.locals import *
from storm.expr import Desc, Select


from vindula.myvindula.models.base import BaseStore


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


    def getContent_by_hash(self,hash):
        data = self.store.find(ModelsContent, ModelsContent.hash==hash).one()
        if data:
            return data
        else:
            return None