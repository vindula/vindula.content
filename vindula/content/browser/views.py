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
        result = None
        if 'control-panel-objects' in getSite().keys():
            control = getSite()['control-panel-objects']
            if 'vindula_categories' in control.keys():
                confg = control['vindula_categories']
                try:
                    result =  confg.order_list
                except:
                    return result
        return result

class VindulaResultsNews(BrowserView):

    def QueryFilter(self):
        form = self.request.form
        submitted = form.get('submitted', False)
        
        if submitted:
            D = {}
            catalog_tool = getToolByName(self, 'portal_catalog')
            
            invert = form.get('invert', False)
            if invert:
                D['sort_order'] = 'descending'
            else:
                D['sort_order'] = 'ascending'
             
            text = form.get('keyword','')
            if text:
                text = text.strip()
                if '*' not in text:
                     text += '*'
                D['SearchableText'] = quote_chars(text)    
            
            D['sort_on'] = form.get('sorted','getObjPositionInParent')
            D['path'] = {'query':'/'.join(self.context.getPhysicalPath()), 'depth': 1}
            result = catalog_tool(**D)
        else:
            result = self.context.getFolderContents()
        return result

            
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
        
        itens = self.context.getFolderContents({'meta_type': ('VindulaEdital',)})
        objs = []
        for item in itens:
            objs.append(item.getObject())

        reverse = int(self.request.form.get('invert', 0))
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
            
        return sorted(objs, key=sortDataPublicacao, reverse=reverse)
            
            
            
            
            

            
            
            
            
            

    