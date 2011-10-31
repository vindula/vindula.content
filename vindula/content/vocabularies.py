# -*- coding: utf-8 -*-
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from Products.CMFCore.utils import getToolByName
from vindula.content import MessageFactory as _

class TypesAgenda(object):
    """ Create SimpleVocabulary for Category Field"""
    
    implements(IContextSourceBinder)
    
    def __init__(self, type):
        self.type = type

    def __call__(self, context):
        pc = getToolByName(context, 'portal_catalog')
        objetos = pc(portal_type=self.type, review_state='published')
        
        terms = []
        if objetos is not None:
            for obj in objetos:
                path = '/'.join(obj.getObject().getPhysicalPath())
                title = obj.getObject().Title()
                terms.append(SimpleTerm(path, path, _(u'opcao_agenda', default=unicode(title))))
                                
        return SimpleVocabulary(terms)