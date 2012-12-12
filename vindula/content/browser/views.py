# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from zope.app.component.hooks import getSite

from Products.ATContentTypes.criteria import _criterionRegistry

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

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
            sort_on = form.get('sorted',form_cookies.get('sorted', 'getObjPositionInParent'))

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
            result = self.context.getFolderContents({'meta_type': ('ATNewsItem','VindulaNews',), 'sort_order': 'descending', 'sort_on': 'effective'})
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