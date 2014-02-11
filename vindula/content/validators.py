# -*- coding: utf-8 -*-
from zope.interface import implements
from Products.validation.interfaces.IValidator import IValidator
from zope.app.component.hooks import getSite
# from vindula.myvindula.user import ModelsDepartment

from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, setSecurityManager
from Products.CMFCore.utils import getToolByName

class SameUserValidator:
    implements(IValidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        context = getSite()
        portal_membership = getToolByName(context, "portal_membership")
        user_admin = portal_membership.getMemberById('admin')

        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        # create a new context, as the owner of the folder
        newSecurityManager(context,user_admin)            
        
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

        # restore the original context
        setSecurityManager(old_security_manager)

class UpdateUserManageEmployeesValidator:
    implements(IValidator)

    def __init__(self, name):
        self.name = name

    def __call__(self, value, *args, **kwargs):
        #TODO AJUTAR OS DEPARTAMENTOS DOS USUARIOS NA UNIDADE ORGANIZACIONAL
        context =  getSite()
        portal_membership = getToolByName(context, "portal_membership")
        user_admin = portal_membership.getMemberById('admin')

        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        # create a new context, as the owner of the folder
        newSecurityManager(context,user_admin)       

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
                    # ModelsDepartment().del_department(user=unicode(user), depUID=unicode(instance.UID()))

                    D = {'UID' : unicode(instance.UID()), 'funcdetails_id': unicode(user)}
                    # ModelsDepartment().set_department(**D)

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
                        # ModelsDepartment().set_department(**D)

                        #adicionando no grupo da estrutura
                        portalGroup.getGroupById(id_grupo_employees).addMember(user)

                        if permission_view.count(user) == 0:
                            permission_view.append(user)
                    except:
                        print 'Erro adicionando departamento'
                        pass

                for user in removido:
                    try:
                        # ModelsDepartment().del_department(user=unicode(user), depUID=unicode(instance.UID()))

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
            
            group_manager = portalGroup.getGroupById(id_grupo_Manage)
            
            
            #TODO: Arrumar essa logica, sempre que esta salvando estou removendo os usarios do grupo de admin e adicionando o gestor novamente
            #      isso está sendo feito pois a atualizaçao dinamica nao removia os usuarios antigos do campo de Grupo da UO
            
            #Limpa os usuarios de admin
            if group_manager:
                for old_user in group_manager.getGroupMembers():
                    group_manager.removeMember(old_user.getUserName())
                    
            D = {'UID' : unicode(instance.UID()), 'funcdetails_id': unicode(gestor_new)}
            group_manager.addMember(gestor_new)
            
        # restore the original context
        setSecurityManager(old_security_manager)