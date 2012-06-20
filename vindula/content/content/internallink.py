# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from interfaces import IInternalLink

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.link import ATLinkSchema
from Products.ATContentTypes.content.link import ATLink
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

InternalLink_schema = ATLinkSchema.copy() + Schema((

   ReferenceField('internal_link',
        multiValued=0,
        label=_(u"Link Interno"),
        relationship='internal_link',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Link Interno"),
            description=_(u'Selecione um conteudo interno para fazer referencia.'))),                                                  

))
invisivel = {'view':'invisible','edit':'invisible',}
InternalLink_schema['remoteUrl'].required = False
# Dates
L = ['effectiveDate','expirationDate','creation_date','modification_date']   
# Categorization
L += ['subject','relatedItems','location','language']
# Ownership
L += ['creators','contributors','rights']
# Settings
L += ['allowDiscussion','excludeFromNav']
for i in L:
    InternalLink_schema[i].widget.visible = invisivel

finalizeATCTSchema(InternalLink_schema, folderish=False)

class InternalLink(ATLink):
    """ Reserve Content for InternalLink"""
    security = ClassSecurityInfo()    
    
    implements(IInternalLink)    
    portal_type = 'InternalLink'
    _at_rename_after_creation = True
    schema = InternalLink_schema

registerType(InternalLink, PROJECTNAME)