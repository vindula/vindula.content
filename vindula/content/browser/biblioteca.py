# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface

from AccessControl import ClassSecurityInfo



from Products.CMFCore.utils import getToolByName


class BlibliotecaView(grok.View):
    grok.context(Interface)
    grok.name('biblioteca-view')
    grok.require('zope2.View')
    
    def update(self):
        print 'hsdhdhdhdhdhdhdhdhdh'
        
        self.file = []
        x = self.searchFile()
        for i in range(5):
            self.file.append(x)

        print self.file

    def searchFile(self, path=None, limit=5, keywords=[]):
        if limit:
            query = {}
            keywords = [i for i in keywords if i != '']
            
            if path is None:
                path = self.context.portal_url.getPortalObject().getPhysicalPath()
            else:
                path = path.getPhysicalPath()
    
            self.pc = getToolByName(self.context, 'portal_catalog')
            query['portal_type'] = ('File',)
            #query['review_state'] = ['published', 'internally_published', 'external']
            query['path'] = {'query':'/'.join(path)}
            query['sort_on'] = 'effective'
            query['sort_order'] = 'descending'
#            if keywords:
#                query['Subject'] = keywords
    
            result = self.pc(**query)
            return result[:limit]
            
            
        return []        