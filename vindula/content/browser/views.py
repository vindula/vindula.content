# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View

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
    
    security = ClassSecurityInfo()
    
    security.declareProtected(View, 'criteriaByIndexId')
    def criteriaByIndexId(self, indexId):
        catalog_tool = getToolByName(self, 'portal_catalog')
        indexObj = catalog_tool.Indexes[indexId]
        results = _criterionRegistry.criteriaByIndex(indexObj.meta_type)
        return results
    
    security.declareProtected(View, 'validateAddCriterion')
    def validateAddCriterion(self, indexId, criteriaType):
        """Is criteriaType acceptable criteria for indexId
        """
        return criteriaType in self.criteriaByIndexId(indexId)
    
    
    security.declareProtected(View, 'listSortFields')
    def listSortFields(self):
        """Return a list of available fields for sorting."""
        tool = getToolByName(self, 'portal_atct')
        
        listFields = tool.getEnabledFields() 
        fields = [ field
                    for field in listFields
                    if self.validateAddCriterion(field[0], 'ATSortCriterion') ]
        return fields
    

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
            D['path'] = {'query':'/'.join(self.context.getPhysicalPath())}
            D['meta_type'] =  ['ATNewsItem','VindulaNews']
            
            result = catalog_tool(**D)
        
        else:
            result = self.context.getFolderContents({'meta_type': ('ATNewsItem','VindulaNews',)})
        
        return result

    