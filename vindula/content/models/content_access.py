# coding: utf-8

from operator import itemgetter

#Imports regarding the connection of the database 'strom'
from storm.locals import *
from storm.expr import Desc, Select


from vindula.myvindula.models.base import BaseStore




class ModelsContentAccess(Storm, BaseStore):
    __storm_table__ = 'vinapp_social_access'

    #Campos de edição
    id = Int(primary=True)
    hash = Unicode()
    content_id = Int()
    username = Unicode()

    date_created = DateTime()
    date_modified = DateTime()



    def getContAccess(self, UIDs):
        #TODO: Melhorar este metodo
        from vindula.content.models.content import ModelsContent
        result = []

        itens = tuple(UIDs)
        if len(itens) == 1:
            itens = str(itens)[:-2] + ')'
        else:
            itens = str(itens)

        sql ='SELECT vc.hash,count(vc.hash) as contagem\
              FROM vinapp_social_access va, vinapp_social_content vc\
              where va.content_id = vc.id\
              and vc.uid in %s group by vc.hash order by contagem' %(itens)

        data = self.store.execute(sql)
        if data.rowcount != 0:
            for obj in data.get_all():
                result.append({'content' : ModelsContent().getContent_by_hash(obj[0]),
                               'count': obj[1]})

            result = sorted(result, key=itemgetter('count'), reverse=True)

        return result