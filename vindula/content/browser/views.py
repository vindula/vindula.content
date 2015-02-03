# -*- coding: utf-8 -*-
import json, mimetypes
from datetime import datetime
from itertools import chain

import zope.event
from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, setSecurityManager
from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.PluggableAuthService.interfaces.plugins import IRolesPlugin
from collective.documentviewer.async import queueJob
from collective.quickupload.browser.uploadcapable import get_id_from_filename, MissingExtension
from collective.quickupload.interfaces import IQuickUploadFileFactory, IQuickUploadFileUpdater
from five import grok
from plone.app.layout.viewlets.content import ContentHistoryView
from vindula.myvindula.registration import ImportUser
from zope.app.component.hooks import getSite
from zope.component import getMultiAdapter
from zope.interface import Interface

from vindula.content import logger
from vindula.content.browser.utils import (normalize_id_to_file_name, create_or_set_folder_path, 
    vindula_file_factory, vindula_file_updater)
from vindula.content.content.orgstructure.subscribe import OrgstructureModifiedEvent


MULTISPACE = u'\u3000'.encode('utf-8')

def quote_chars(s):
    # We need to quote parentheses when searching text indices
    if '(' in s:
        s = s.replace('(', '"("')
    if ')' in s:
        s = s.replace(')', '")"')
    if MULTISPACE in s:
        s = s.replace(MULTISPACE, ' ')
    return s

class VindulaListNews(BrowserView):

    def getListToOrder(self):
        result = [('effective', u'Effective Date', 'The time and date an item becomes publicly available'), \
                  ('sortable_title', u'Sortable Title', u"An item's title transformed for sorting")]

        if 'control-panel-objects' in getSite().keys():
            control = getSite()['control-panel-objects']
            if 'vindula_categories' in control.keys():
                confg = control['vindula_categories']
                try:
                    for i in confg.getOrder_list():
                        result.append(i.replace('(', '').replace(')','').replace('u\'', '').replace('\'', '').split(','))
                except:
                    return result
        return result

class VindulaResultsNews(BrowserView):

    def QueryFilter(self, portal_type=('ATNewsItem','VindulaNews')):
        form = self.request.form
        submitted = form.get('submitted', False)
        form_cookies = {}

        if not submitted and self.request.cookies.get('find-news', None):
            form_cookies = self.getCookies(self.request.cookies.get('find-news', None))


        sort_on = form.get('sorted',form_cookies.get('sorted', 'created'))
        invert = form.get('invert', form_cookies.get('invert', False))

        if submitted or form_cookies:
            D = {}
            catalog_tool = getToolByName(self, 'portal_catalog')

            if sort_on == 'effective':
                invert = not invert

            if invert:
                D['sort_order'] = 'reverse'
            else:
                D['sort_order'] = 'descending'

            if sort_on == 'sortable_title':
                if invert:
                    D['sort_order'] = 'descending'
                else:
                    D['sort_order'] = 'acending'


            text = form.get('keyword',form_cookies.get('keyword', ''))
            if text:
                text = text.strip()
                if '*' not in text:
                     text += '*'
                D['SearchableText'] = quote_chars(text)

            D['review_state'] = ['published', 'internally_published', 'external']
            D['meta_type'] = portal_type
            D['sort_on'] = sort_on
            D['path'] = {'query':'/'.join(self.context.getPhysicalPath()), 'depth': 10}

            result = catalog_tool(**D)
        else:
            sort_order = "descending"
            if invert:
                sort_order = 'acending'

            result = self.context.getFolderContents({'meta_type':portal_type, 'sort_on': sort_on, 'sort_order': sort_order})
        return result


    def QueryFilterFolder(self, portal_type=('ATFolder','VindulaFolder')):
        return self.QueryFilter(portal_type)


    def QueryFilterEquipe(self,portal_type=('VindulaTeam',)):
        return self.QueryFilter(portal_type)


    def getCookies(self, cookies=None):
        form_cookies = {}
        if not cookies:
            cookies = self.request.cookies.get('find-news', None)

        if cookies:
            all_cookies = self.request.cookies.get('find-news', None).split('|')
            for cookie in all_cookies:
                if cookie:
                    cookie = cookie.split('=')
                    form_cookies[cookie[0]] = cookie[1]

        return form_cookies


def sortDataPublicacao(item):
    return item.getDataPublicacao()
def sortNumEdital(item):
    return item.getNumeroEdital()
def sortOrgao(item):
    return item.getOrgao()
def sortModalidade(item):
    return item.getModalidade()
def sortTitle(item):
    return item.Title()

class VindulaListEditais(BrowserView):
    def getListOfEditais(self):
        if self.request.form.get('keyword', None):
            keyword= self.request.form.get('keyword',None)
            pc = getToolByName(self, 'portal_catalog')
            query = {}

            if keyword:
                keyword = keyword.strip()
                if '*' not in keyword:
                     keyword += '*'
                query['SearchableText'] = quote_chars(keyword)
            query['path'] = {'query':'/'.join(self.context.getPhysicalPath()), 'depth': 1}
            query['meta_type'] = ('VindulaEdital',)
            itens = pc(**query)
        else:
            itens = self.context.getFolderContents({'meta_type': ('VindulaEdital',)})

        objs = []
        for item in itens:
            objs.append(item.getObject())

        reverse = bool(self.request.form.get('invert', False))
        sort = self.request.form.get('sort-edital', None)

        if sort:
            if sort == 'edital':
                return sorted(objs, key=sortNumEdital, reverse=reverse)
            elif sort == 'orgao':
                return sorted(objs, key=sortOrgao, reverse=reverse)
            elif sort == 'madalidade':
                return sorted(objs, key=sortModalidade, reverse=reverse)
            elif sort == 'assunto':
                return sorted(objs, key=sortTitle, reverse=reverse)

        return sorted(objs, key=sortDataPublicacao, reverse=not reverse)


class VindulaWebServeObjectContent(grok.View):
    grok.context(Interface)
    grok.name('vindula-object-content')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        D = {}
        portal_workflow = getToolByName(self.context, "portal_workflow")
        reference_catalog = getToolByName(self.context, "reference_catalog")
        portal_membership = getToolByName(self.context, "portal_membership")

        uid = self.request.form.get('uid','')

        user_admin = portal_membership.getMemberById('admin')

        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        #usuario temporario para o tipo de conteudo ATFILE, que não tem History
        username_logged = "XXusertmpXX"

        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)

        context = reference_catalog.lookupObject(uid)
        if context:
            HistoryView = ContentHistoryView(context, context.REQUEST)
            try:context_owner = context.getOwner().getUserName()
            except:context_owner = 'administrador'
            image_content = ''
            if hasattr(context, 'getImageIcone'):
                img = context.getImageIcone()
                image_content = img.replace(self.context.absolute_url(),'')

            try:
                status = portal_workflow.getInfoFor(context, 'review_state')
            except WorkflowException:
                status = 'no workflow'

            content_history = HistoryView.fullHistory() or []
            L = []
            for history in content_history:
                tipo = history.get('type','')
                if tipo == 'workflow':
                    date = history.get('time','').strftime('%Y-%m-%d %H:%M:%S')
                else:
                    date = datetime.fromtimestamp(history.get('time','')).strftime('%Y-%m-%d %H:%M:%S')

                actor = history.get('actor',{})
                if not actor:
                    actor = ''

                L.append({'actor': actor,
                          'action':  history.get('transition_title',''),
                          'type': tipo,
                          'date':date,})

            if context.portal_type == 'File':
                D['history'] = [{'actor': username_logged,
                                 'action':  'Edited',
                                 'type': context.portal_type,
                                 'date':context.bobobase_modification_time().strftime('%Y-%m-%d %H:%M:%S'),}]
            else:
                D['history'] = L

            D['details'] = {'uid': context.UID(),
                            'type': context.portal_type,
                            'title': context.Title(),
                            'description':context.Description(),
                            'owner': context_owner,
                            'date_created':context.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'date_modified':context.bobobase_modification_time().strftime('%Y-%m-%d %H:%M:%S'),
                            'workflow': status,
                            'url': '/'+'/'.join(context.getPhysicalPath()[2:]),
                            'image': image_content}

            excludeField = ['title','description','blogger_bio','blogger_name','blog_entry', 'location', 'language']
            typesField = ['string','text','lines','boolean','datetime','reference']

            extra_details = {}

            for field in context.Schema().fields():
                if not field.getName() in excludeField and\
                   field.type in typesField and\
                   field.accessor:

                    accessor = getattr(context, field.accessor)

                    if accessor:
                        accessor = accessor()

                        if isinstance(accessor, (tuple, list)):
                            accessor = str(list(accessor))
                        elif isinstance(accessor, bool):
                            accessor = str(accessor)
                        elif isinstance(accessor, (datetime, DateTime)):
                            accessor = accessor.strftime('%d/%m/%Y %H:%M:%S')
                        elif field.type == 'reference':
                            if accessor:
                                accessor = accessor.UID()

                        if isinstance(accessor, str) or isinstance(accessor, unicode):
                            extra_details[field.getName()] = accessor


            D['extra_details'] = extra_details
        else:
            D['deleted'] = True

        # restore the original context
        setSecurityManager(old_security_manager)

        self.retorno = D

class VindulaWebServeObjectUser(grok.View):
    grok.context(Interface)
    grok.name('vindula-object-user')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def __init__(self, context, request):
        self.request = request
        self.context = context

        self.portal_membership = getToolByName(self.context, "portal_membership")
        self.groups_tool = getToolByName(self, 'portal_groups')
        self.reference_catalog = getToolByName(self.context, "reference_catalog")

        super(VindulaWebServeObjectUser,self).__init__(context, request)


    def checkPermission(self, username):
        D ={}
        user_obj = self.portal_membership.getMemberById(username)
        groups = self.groups_tool.getGroupsByUserId(username)

        if user_obj:
            D['has_manager'] =  user_obj.has_role('Manager')
        else:
            D['has_manager'] = False

        if groups:
            D['groups'] = [g.id for g in groups ]
        else:
            D['groups'] = []

        return D


    def update(self):
        user_admin = self.portal_membership.getMemberById('admin')

        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)

        username = self.request.form.get('username','')
        D = {}
        D.update(self.checkPermission(username))

        # restore the original context
        setSecurityManager(old_security_manager)

        self.retorno = D


class VindulaWebServeContentPermission(VindulaWebServeObjectUser):
    grok.context(Interface)
    grok.name('vindula-content-permission')
    grok.require('zope2.View')

    retorno = {}

    def checkContentPermission(self, username,UID):
        D ={}
        D['has_permission'] =  False
        user_obj = self.portal_membership.getMemberById(username)

        context = self.reference_catalog.lookupObject(UID)
        if context:
            if getSecurityManager().checkPermission(ModifyPortalContent, context):
                D['has_permission'] =  True

        return D


    def update(self):
        user_admin = self.portal_membership.getMemberById('admin')

        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)

        username = self.request.form.get('username','')
        D = {}
        D.update(self.checkPermission(username))

        UID = self.request.form.get('uid','')
        D.update(self.checkContentPermission(username,UID))

        # restore the original context
        setSecurityManager(old_security_manager)

        self.retorno = D




class VindulaWebServeObjectGroup(grok.View):
    grok.context(Interface)
    grok.name('vindula-object-group')
    grok.require('zope2.View')

    retorno = []

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        portal_membership = getToolByName(self.context, "portal_membership")
        user_admin = portal_membership.getMemberById('admin')

        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)

        group = self.request.form.get('group','')
        groups_tool = getToolByName(self.context, 'portal_groups')

        group_obj = groups_tool.getGroupById(group)
        members = group_obj.getGroupMembers()

        L = []
        for member in members:
            L.append({'username':member.getUserName(),
                       'email':member.getProperty('email'),
                       'fullname': member.getProperty('fullname')
                     })

        # restore the original context
        setSecurityManager(old_security_manager)

        self.retorno = L


# Metodo que retorna todos os usuarios do plone e do ad ou ldap que estiver plugado
class VindulaWebServeAllUsersPlone(grok.View):
    grok.context(Interface)
    grok.name('vindula-all-users-plone')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
#         searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

# #        plone_ad_user = searchView.merge(chain(*[searchView.searchUsers(**{field: ''}) for field in ['login', 'fullname', 'email']]), 'userid')
#         plone_ad_user = searchView.searchUsers()
#         plone_ad_user = [i.get('login') for i in plone_ad_user]
#         self.retorno = plone_ad_user
#         return self.retorno

        searchString=''
        searchUsers=True
        searchGroups=True
        ignore=[]

        acl = getToolByName(self, 'acl_users')
        rolemakers = acl.plugins.listPlugins(IRolesPlugin)

        mtool = getToolByName(self, 'portal_membership')
        searchView = getMultiAdapter((aq_inner(self.context), self.request), name='pas_search')

        # First, search for all inherited roles assigned to each group.
        # We push this in the request so that IRoles plugins are told provide
        # the roles inherited from the groups to which the principal belongs.
        # self.request.set('__ignore_group_roles__', False)
        # self.request.set('__ignore_direct_roles__', True)
        # inheritance_enabled_users = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')
        # allInheritedRoles = {}
        # for user_info in inheritance_enabled_users:
        #     userId = user_info['id']
        #     user = acl.getUserById(userId)
        #     # play safe, though this should never happen
        #     if user is None:
        #         logger.warn('Skipped user without principal object: %s' % userId)
        #         continue
        #     # allAssignedRoles = []
        #     # for rolemaker_id, rolemaker in rolemakers:
        #     #     # getRolesForPrincipal can return None
        #     #     roles = rolemaker.getRolesForPrincipal(user) or ()
        #     #     allAssignedRoles.extend(roles)
        #     # allInheritedRoles[userId] = allAssignedRoles

        # We push this in the request such IRoles plugins don't provide
        # the roles from the groups the principal belongs.
        self.request.set('__ignore_group_roles__', True)
        self.request.set('__ignore_direct_roles__', False)
        explicit_users = searchView.merge(chain(*[searchView.searchUsers(**{field: searchString}) for field in ['login', 'fullname', 'email']]), 'userid')


        # Tack on some extra data, including whether each role is explicitly
        # assigned ('explicit'), inherited ('inherited'), or not assigned at all (None).
        results = []
        for user_info in explicit_users:
            userId = user_info['id']
            user = mtool.getMemberById(userId)
            # play safe, though this should never happen
            if user is None:
                logger.warn('Skipped user without principal object: %s' % userId)
                continue
            # explicitlyAssignedRoles = []
            # for rolemaker_id, rolemaker in rolemakers:
            #     # getRolesForPrincipal can return None
            #     roles = rolemaker.getRolesForPrincipal(user) or ()
            #     explicitlyAssignedRoles.extend(roles)

            # roleList = {}
            # for role in self.portal_roles:
            #     canAssign = user.canAssignRole(role)
            #     if role == 'Manager' and not self.is_zope_manager:
            #         canAssign = False
            #     roleList[role]={'canAssign': canAssign,
            #                     'explicit': role in explicitlyAssignedRoles,
            #                     'inherited': role in allInheritedRoles[userId]}

            # canDelete = user.canDelete()
            # canPasswordSet = user.canPasswordSet()
            # if roleList['Manager']['explicit'] or roleList['Manager']['inherited']:
            #     if not self.is_zope_manager:
            #         canDelete = False
            #         canPasswordSet = False

            # user_info['roles'] = roleList
            # user_info['fullname'] = user.getProperty('fullname', '')
            # user_info['email'] = user.getProperty('email', '')
            # user_info['username'] = user.getUserName()
            # user_info['can_delete'] = canDelete
            # user_info['can_set_email'] = user.canWriteProperty('email')
            # user_info['can_set_password'] = canPasswordSet
            # results.append(user_info)
            results.append(user.getUserName())

        # Sort the users by fullname
        # results.sort(key=lambda x: x is not None and x['fullname'] is not None and normalizeString(x['fullname']) or '')

        # import pdb;pdb.set_trace()


        # Reset the request variable, just in case.
        self.request.set('__ignore_group_roles__', False)
        self.retorno = results
        return results



    # @property
    # def is_zope_manager(self):
    #     return getSecurityManager().checkPermission(ManagePortal, self.context)


# Metodo que criar o usuario no acl_user do plone
class VindulaWebServeCreateUserPlone(grok.View):
    grok.context(Interface)
    grok.name('vindula-create-user-plone')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        dados = {}
        username = self.request.form.get('username','')

        dados['username'] = username
        dados['name'] = self.request.form.get('name', username)
        dados['email'] = self.request.form.get('email', '')
        dados['password'] = self.request.form.get('password', '')

        if username:
            portal_membership = getToolByName(self.context, "portal_membership")
            user_admin = portal_membership.getMemberById('admin')

            # stash the existing security manager so we can restore it
            old_security_manager = getSecurityManager()

            # create a new context, as the owner of the folder
            newSecurityManager(self.request,user_admin)


            result = ImportUser().importUser(self,{},user=dados)

            # restore the original context
            setSecurityManager(old_security_manager)

            if result:
                self.retorno['response'] = 'Usuario criado com sucesso'
            else:
                self.retorno['response'] = 'Usuario não criado, dados invalidos'
        else:
            self.retorno['response'] = 'Usuario não criado, dados invalidos'

#Método para a atualização das unidades organizacionais vindas do Web Service
class VindulaWebServeUpdateOrgStructure(grok.View):
    grok.context(Interface)
    grok.name('vindula-update-org-structures')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        try:
            dados = {}
            uid_object = self.request.form.get('uid','')
            field = self.request.form.get('field','')
            if field:
                field = field[0].upper() + field[1:]
            value = self.request.form.get('value','')

            if uid_object:
                p_catalog = getToolByName(self.context, 'portal_catalog')
                p_membership = getToolByName(self.context, "portal_membership")
                p_groups = getToolByName(self, 'portal_groups')
                user_admin = p_membership.getMemberById('admin')

                # stash the existing security manager so we can restore it
                old_security_manager = getSecurityManager()

                # create a new context, as the owner of the folder
                newSecurityManager(self.request,user_admin)

                item = p_catalog(UID = uid_object)

                if item:
                    item = item[0]
                    item = item.getObject()
                    if field == 'Structures':
                        uo_pai = p_catalog(portal_type='OrganizationalStructure', wsId=value)
                        if uo_pai:
                            uo_pai = uo_pai[0].getObject()
                            item.setStructures(uo_pai)
                    elif field in ['Manager', 'Vice_manager', 'Employees']:
                        try:
                            value = eval(value)
                        except NameError:
                            value = str(value)
                        except SyntaxError:
                            pass

                        if isinstance(value, list):
                            value = tuple(value)

                        old_members = eval('item.get%s()' % (field))

                        if isinstance(old_members, str):
                            old_members = [old_members]
                        elif isinstance(old_members, int):
                            old_members = [str(old_members)]

                        for member in old_members:
                            id_group_view = uid_object+'-view'
                            p_groups.removePrincipalFromGroup(member, id_group_view)
                            if field in ['Manager', 'Vice_manager']:
                                id_group_admin = uid_object+'-admin'
                                p_groups.removePrincipalFromGroup(member, id_group_admin)

                        if field in ['Manager', 'Vice_manager']:
                            eval('item.set%s("%s")' % (field, value))
                        else:
                            eval('item.set%s(%s)' % (field, value))

                        new_members = eval('item.get%s()' % (field))

                        if isinstance(new_members, str):
                            new_members = [new_members]

                        for member in new_members:
                            id_group_view = uid_object+'-view'
                            p_groups.addPrincipalToGroup(member, id_group_view)
                            if field in ['Manager', 'Vice_manager']:
                                id_group_admin = uid_object+'-admin'
                                p_groups.addPrincipalToGroup(member, id_group_admin)

                        item.setGroups_view([])
                        item.setGroups_edit([])
                        item.setGroups_admin([])

                        zope.event.notify(OrgstructureModifiedEvent(item))
                    else:
                        eval('item.set%s("%s")' % (field, value))

                    item.reindexObject()



                # restore the original context
                setSecurityManager(old_security_manager)

                self.retorno['response'] = 'OK'

            else:
                self.retorno['response'] = 'NOUID'
        except:
            self.retorno['response'] = 'Ocorreu um erro ao atualizar o content type'


#Método para a atualização das unidades organizacionais vindas do Web Service
class VindulaWebServeUpdateStructuresTypes(grok.View):
    grok.context(Interface)
    grok.name('vindula-update-structures-types')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        try:
            list_types = self.request.form.get('list_types','')
            if list_types:
                p_catalog = getToolByName(self.context, 'portal_catalog')
                p_membership = getToolByName(self.context, "portal_membership")
                user_admin = p_membership.getMemberById('admin')

                # stash the existing security manager so we can restore it
                old_security_manager = getSecurityManager()

                # create a new context, as the owner of the folder
                newSecurityManager(self.request,user_admin)

                try:
                    list_types = eval(list_types)
                except:
                    self.retorno['response'] = 'Ocorreu um erro atualizando o tipos, a variavel enviada para o Plone esta incorreta'
                new_list = ''

                for type in list_types:
                    new_list += type+'\n'

                if new_list[-1:] == '\n':
                    new_list = new_list[:-1]

                obj_control = getSite().get('control-panel-objects')
                vindula_categories = obj_control.get('vindula_categories')
                vindula_categories.setTipoUnidade(new_list)

                vindula_categories.reindexObject()

                # restore the original context
                setSecurityManager(old_security_manager)

                self.retorno['response'] = 'OK'

            else:
                self.retorno['response'] = 'NOLIST'
        except:
            self.retorno['response'] = 'Ocorreu um erro atualizando o tipos de unidades'

#Método para a atualização das unidades organizacionais vindas do Web Service
class VindulaUpdateContentTags(grok.View):
    grok.context(Interface)
    grok.name('vindula-update-content-tags')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        try:
            uid_content = self.request.form.get('uid_content','')
            if uid_content:
                p_catalog = getToolByName(self.context, 'portal_catalog')
                p_membership = getToolByName(self.context, "portal_membership")
                user_admin = p_membership.getMemberById('admin')

                # stash the existing security manager so we can restore it
                old_security_manager = getSecurityManager()

                # create a new context, as the owner of the folder
                newSecurityManager(self.request,user_admin)

                results = p_catalog(UID=uid_content)
                if results:
                    content = results[0]
                    content = content.getObject()

                    themes = self.request.form.get('themes','')
                    subjects = self.request.form.get('subjects','')
                    typology = self.request.form.get('typology','')

                    if themes:
                        themes = eval(themes)
                        themes = tuple(themes)
                        try:
                            content.setThemesNews(themes)
                        except AttributeError:
                            # self.retorno['response'] = 'ERROR'
                            # return
                            pass

                    if subjects:
                        subjects = eval(subjects)
                        subjects = tuple(subjects)
                        content.setSubject(subjects)

                    if typology:
                        try:
                            content.setTipo(typology)
                        except AttributeError:
                            # self.retorno['response'] = 'ERROR'
                            # return
                            pass

                    content.reindexObject()
                else:
                    self.retorno['response'] = 'NO-OBJECT'
                    return

                # restore the original context
                setSecurityManager(old_security_manager)

                self.retorno['response'] = 'OK'
            else:
                self.retorno['response'] = 'NOUID'
        except:
            self.retorno['response'] = 'ERROR'

#Método para a atualização das unidades organizacionais vindas do Web Service
class VindulaUpdateTag(grok.View):
    grok.context(Interface)
    grok.name('vindula-update-tag')
    grok.require('zope2.View')

    retorno = {}
    dict_field_index = {'subject': 'Subject',
                        'themesNews': 'ThemeNews',
                        'typology': 'tipo',}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        try:
            type = self.request.form.get('type', '')
            old_value = self.request.form.get('old_value', '')
            new_value = self.request.form.get('new_value', '')
            delete_tag = self.request.form.get('delete_tag', False)

            if (new_value or old_value) and type:
                p_catalog = getToolByName(self.context, 'portal_catalog')
                p_membership = getToolByName(self.context, "portal_membership")
                user_admin = p_membership.getMemberById('admin')
                dict_field_index = {'subject': 'Subject',
                                    'themesNews': 'ThemeNews',
                                    'typology': 'tipo',}

                # stash the existing security manager so we can restore it
                old_security_manager = getSecurityManager()

                # create a new context, as the owner of the folder
                newSecurityManager(self.request,user_admin)
                if old_value:
                    querySet = p_catalog({dict_field_index[type]: old_value})
                    if querySet:
                        for item in querySet:
                            obj = item.getObject()
                            if delete_tag:
                                self.removeTag(obj, type, old_value, new_value)
                            else:
                                self.updateTag(obj, type, old_value, new_value)

                setSecurityManager(old_security_manager)
                self.retorno['response'] = 'OK'
            else:
                self.retorno['response'] = 'NOUID'
        except:
            self.retorno['response'] = 'ERROR'


    def updateTag(self, obj, type, old_tag, new_tag):
        method = getattr(obj, self.dict_field_index[type])

        if method:
            if type == 'typology':
                indexList = new_tag
            else:
                indexList = list(method())
                while (old_tag in indexList) and (old_tag <> new_tag):
                    indexList[indexList.index(old_tag)] = new_tag

            if type == 'themesNews':
                set_attr = 'setThemesNews'
            else:
                set_attr = 'set%s' % (self. dict_field_index[type][0].upper() + self. dict_field_index[type][1:])

            exec('obj.'+set_attr+'(indexList)')
            obj.reindexObject()

    def removeTag(self, obj, type, old_tag, new_tag):
        method = getattr(obj, self.dict_field_index[type])

        if method:
            if type == 'typology':
                indexList = ''
            else:
                indexList = list(method())
                while old_tag in indexList:
                    indexList.remove(old_tag)

            if type == 'themesNews':
                set_attr = 'setThemesNews'
            else:
                set_attr = 'set%s' % (self. dict_field_index[type][0].upper() + self. dict_field_index[type][1:])

            exec('obj.'+set_attr+'(indexList)')
            obj.reindexObject()



class VindulaSyncFile(grok.View):
    grok.context(Interface)
    grok.name('vindula-sync-file')
    grok.require('zope2.View')

    retorno = {}

    def render(self):
        self.request.response.setHeader("Content-type","application/json")
        self.request.response.setHeader("charset", "UTF-8")
        return json.dumps(self.retorno,ensure_ascii=False)

    def update(self):
        try:
            # import pdb; pdb.set_trace()
            context = aq_inner(self.context)

            #TODO: Alterar os nomes das variaveis
            file_data = self.request.form.get('file', '')
            new_file = self.request.form.get('new_file', '')
            try:
                new_file = eval(new_file)
            except:
                new_file = False

            folder_path = self.request.form.get('folder_path', '')

            p_membership = getToolByName(context, "portal_membership")
            user_admin = p_membership.getMemberById('admin')

            # stash the existing security manager so we can restore it
            old_security_manager = getSecurityManager()
            # create a new context, as the owner of the folder
            newSecurityManager(self.request,user_admin)

            if file_data:

                #Mudando de contexto de acordo com o meu folder_path
                if folder_path and folder_path != '/':
                    context = create_or_set_folder_path(folder_path.split('/'), context)

                title = file_name = file_data.filename

                id_file_name = normalize_id_to_file_name(title, context)

                description = ''
                mime_type = mimetypes.guess_type(file_name)[0]
                portal_type = 'File'
                upload_with = "CLASSIC FORM POST"

                #Verifico aqui se existe o arquivo no meu contexto
                try:
                    newid = get_id_from_filename(file_name, context)
                except MissingExtension:
                    raise 'missingExtensionFile'

                if newid in context or id_file_name in context:
                    updated_object = context.get(newid, False) or context[id_file_name]
                    mtool = getToolByName(context, 'portal_membership')
                    if mtool.checkPermission(ModifyPortalContent, updated_object):
                        can_overwrite = True
                    else:
                        can_overwrite = False

                    if not can_overwrite:
                        logger.debug("The file id for %s already exists, upload rejected" % file_name)
                        raise 'serverErrorAlreadyExists'

                    overwritten_file = updated_object
                else:
                    overwritten_file = None

                if overwritten_file is not None:
                    logger.info("reuploading %s file with %s : title=%s, description=%s, mime_type=%s" % \
                            (overwritten_file.absolute_url(), upload_with, title, description, mime_type))
                    try :
                        f = vindula_file_updater(overwritten_file, file_name, title, description, mime_type, file_data)
                        if f['success'] is not None:
                            queueJob(f['success'])
                    except Exception, e:
                        logger.error("Error updating %s file : %s", file_name, str(e))
                        raise "Error updating %s file : %s" % (file_name, str(e))
                else:
                    logger.info("uploading file with %s : filename=%s, title=%s, description=%s, mime_type=%s, portal_type=%s" % \
                            (upload_with, file_name, title, description, mime_type, portal_type))
                    try :
                        f = vindula_file_factory(context, file_name, title, description, mime_type, file_data, portal_type)
                    except Exception, e:
                        logger.error("Error creating %s file : %s", file_name, str(e))
                        raise  "Error updating %s file : %s" % (file_name, str(e))

                if f['success'] is not None :
                    o = f['success']
                    self.retorno['uid'] = o.UID()
                    logger.info("file url: %s" % o.absolute_url())
            
            setSecurityManager(old_security_manager)
            self.retorno['status'] = 'success'
        except Exception, e:
            self.retorno['status'] = u'error'
            self.retorno['message'] = u'serverError: %s' % (str(e))