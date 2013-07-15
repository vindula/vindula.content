# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from zope.app.component.hooks import getSite

from Products.ATContentTypes.criteria import _criterionRegistry

from plone.app.layout.viewlets.content import ContentHistoryView

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, setSecurityManager
from five import grok
from zope.interface import Interface
from datetime import datetime

MULTISPACE = u'\u3000'.encode('utf-8')

import json

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
    def QueryFilter(self):
        form = self.request.form
        submitted = form.get('submitted', False)
        form_cookies = {}
        if not submitted and self.request.cookies.get('find-news', None):
            form_cookies = self.getCookies(self.request.cookies.get('find-news', None))

        if submitted or form_cookies:
            D = {}
            catalog_tool = getToolByName(self, 'portal_catalog')
            invert = form.get('invert', form_cookies.get('invert', False))
            sort_on = form.get('sorted',form_cookies.get('sorted', ''))

            if sort_on == 'effective':
                invert = not invert

            if invert:
                D['sort_order'] = 'reverse'
            else:
                D['sort_order'] = ''

            text = form.get('keyword',form_cookies.get('keyword', ''))
            if text:
                text = text.strip()
                if '*' not in text:
                     text += '*'
                D['SearchableText'] = quote_chars(text)

            D['sort_on'] = sort_on
            D['path'] = {'query':'/'.join(self.context.getPhysicalPath()), 'depth': 1}
            result = catalog_tool(**D)
        else:
            result = self.context.getFolderContents({'meta_type': ('ATNewsItem','VindulaNews',), 'sort_on': 'effective', 'sort_order':'reverse'})
        return result

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

        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)

        context = reference_catalog.lookupObject(uid)
        if context:
            HistoryView = ContentHistoryView(context, context.REQUEST)
            try:context_owner = context.getOwner().getUserName()
            except: context_owner = 'administrador'
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

                #print 30*'##'
                #print history
                L.append({'actor': history.get('actor',{}).get('username',''),
                          'action':  history.get('transition_title',''),
                          'type': tipo,
                          'date':date,})

            D['history'] = L

            D['details'] = {'uid': context.UID(),
                            'type': context.portal_type,
                            'title': context.Title(),
                            'description':context.Description(),
                            'owner': context_owner,
                            'date_created':context.creation_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'date_modified':context.bobobase_modification_time().strftime('%Y-%m-%d %H:%M:%S'),
                            'workflow': status,
                            'url': '/'+context.virtual_url_path(),
                            'image': image_content}

            excludeField = ['title','description']
            typesField = ['string','text']
            extra_details = {}

            for field in context.Schema().fields():
                if not field.getName() in excludeField and\
                   field.type in typesField and field.accessor:
                   accessor = getattr(context, field.accessor)

                   if isinstance(accessor(), str) or isinstance(accessor(), unicode):
                        extra_details[field.getName()] = accessor()

            D['extra_details'] = extra_details


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

        super(VindulaWebServeObjectUser,self).__init__(context, request)


    def checkPermission(self, username):
        D ={}
        user_obj = self.portal_membership.getMemberById(username)
        groups = self.groups_tool.getGroupsByUserId(username)

        D['groups'] = [g.id for g in groups ]
        D['has_manager'] =  user_obj.has_role('Manager')
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

