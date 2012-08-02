# -*- coding: utf-8 -*-
from zope.interface import implements        
from Products.validation.interfaces.IValidator import IValidator
from zope.app.component.hooks import getSite

class SameUserValidator:
    implements(IValidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        portalGroup = getSite().portal_groups
        instance    = kwargs.get('instance', None)
        req = kwargs['REQUEST']
        form = req.form 
        fields = ['Groups_view','Groups_edit','Groups_admin']
        for item in fields:
            
            id_grupo = instance.UID() +'-'+item.split('_')[1]    
            atual = instance.__getattribute__(item)
            news = form.get(item)
            
            alterado = set(atual) - set(news)

            for j in alterado:
                portalGroup.getGroupById(id_grupo).removeMember(j)
            
class UpdateUserManageEmployeesValidator:
    implements(IValidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        portalGroup = getSite().portal_groups
        instance = kwargs.get('instance', None)
        req = kwargs['REQUEST']
        form = req.form
        
        # Procesamento Funcionario
        id_grupo_employees = instance.UID() +'-view'
        atual = instance.__getattribute__('employees')
        news = form.get('employees')        
        alterado = set(atual) - set(news)
        
        for j in alterado:
            try:
                portalGroup.getGroupById(id_grupo_employees).removeMember(j)
            except:
                pass
