# -*- coding: utf-8 -*-
from zope.interface import implements        
from Products.validation.interfaces.IValidator import IValidator
from zope.app.component.hooks import getSite
from vindula.myvindula.user import ModelsDepartment

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

        if not instance.isTemporary():
            # Procesamento Funcionario
            id_grupo_employees = instance.UID() +'-view'
            employees_old = list(instance.__getattribute__('employees'))
            employees_new = form.get('employees')
            
            if employees_new == employees_old: #entra aqui quando nao mudou nada ou quando está criando o objeto
                for user in employees_new:
                    ModelsDepartment().del_department(user=unicode(user), depUID=unicode(instance.UID()))
                    
                    D = {'UID' : unicode(instance.UID()), 'funcdetails_id': unicode(user)}
                    ModelsDepartment().set_department(**D)
                    
                    if user not in form['Groups_view']:
                        form['Groups_view'].append(user)
    
            elif employees_old and employees_new:
                removido = set(employees_old) - set(employees_new)
                adicionado = set(employees_new) - set(employees_old)
                
                #campo de usuario com privilegio de visualizar
                permission_view = form.get('Groups_view')
                
                for user in adicionado:
                    try:
                        #adicionando na tabela de departamentos
                        D = {'UID' : unicode(instance.UID()), 'funcdetails_id': unicode(user)}
                        ModelsDepartment().set_department(**D)
                        
                        #adicionando no grupo da estrutura
                        portalGroup.getGroupById(id_grupo_employees).addMember(user)

                        if permission_view.count(user) == 0:
                            permission_view.append(user)
                    except:
                        print 'Erro adicionando departamento'
                        pass

                for user in removido:
                    try:
                        ModelsDepartment().del_department(user=unicode(user), depUID=unicode(instance.UID()))
                        
                        #removendo no grupo da estrutura
                        portalGroup.getGroupById(id_grupo_employees).removeMember(user)
                        
                        if permission_view.count(user) > 0:
                            permission_view.remove(user)
                        
                    except:
                        print 'Erro removendo departamento'
                        pass
                
                form['Groups_view'] = permission_view
                        
            # Procesamento Gestores
            gestor_old = instance.__getattribute__('manager')
            gestor_new = form.get('manager')
            id_grupo_Manage = instance.UID() +'-admin'
            
            
            tuple_admin = form.get('Groups_admin')
            if tuple_admin.count(gestor_old) != 0:
                tuple_admin.remove(gestor_old)
            tuple_admin.append(gestor_new)
            instance.Groups_admin = tuple(tuple_admin)
            
            if gestor_old == gestor_new:
                ModelsDepartment().del_department(user=unicode(gestor_new), depUID=unicode(instance.UID()))
                D = {'UID' : unicode(instance.UID()), 'funcdetails_id': unicode(gestor_new)}
                ModelsDepartment().set_department(**D)
                
                portalGroup.getGroupById(id_grupo_Manage).addMember(gestor_new)
            elif gestor_old != gestor_new:
                D = {'UID' : unicode(instance.UID()), 'funcdetails_id': unicode(gestor_new)}
                ModelsDepartment().set_department(**D)
                ModelsDepartment().del_department(user=unicode(gestor_old), depUID=unicode(instance.UID()))
                
                portalGroup.getGroupById(id_grupo_Manage).removeMember(gestor_old)
                portalGroup.getGroupById(id_grupo_Manage).addMember(gestor_new)
