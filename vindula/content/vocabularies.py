# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from vindula.content import MessageFactory as _

class Categories(object):
    """ Create SimpleVocabulary for Category Field"""
    
    implements(IContextSourceBinder)
    
    def __init__(self, type):
        self.type = type

    def __call__(self, context):
        terms = []
        terms.append(SimpleTerm('', '--NOVALUE--', _(u'option_category', default=unicode('Selecione'))))
        
        try:
            obj = context['control-panel-objects']['vindula_categories']
        except:
            obj = None
        
        if obj:
            D = {'orgstructure' : obj.orgstructure.splitlines() if obj.orgstructure is not None else None}
            
            categories = D[self.type]
   
            if categories is not None:
                for item in categories:
                    id = item.lower().replace(' ', '-')
                    terms.append(SimpleTerm(id, id, _(u'option_category', default=unicode(item))))
                                    
        return SimpleVocabulary(terms)