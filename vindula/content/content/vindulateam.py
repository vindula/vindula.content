# -*- coding: utf-8 -*-
from five import grok

from vindula.content import MessageFactory as _
from AccessControl import ClassSecurityInfo
from vindula.content.content.interfaces import IVindulaTeam
from plone.contentrules.engine.interfaces import IRuleAssignable

from plone.app.folder.folder import ATFolder

from zope.interface import implements
from vindula.content.config import *
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
   

from zope.schema.interfaces import IVocabularyFactory   
from zope.component import queryUtility


VindulaTeam_schema =  ATFolder.schema.copy() + Schema((
    

))

finalizeATCTSchema(VindulaTeam_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}

class VindulaTeam(ATFolder):
    """ VindulaTeam """
    
    security = ClassSecurityInfo()
    implements(IVindulaTeam, IRuleAssignable)
    portal_type = 'VindulaTeam'
    _at_rename_after_creation = True
    schema = VindulaTeam_schema
    
registerType(VindulaTeam, PROJECTNAME) 

    
class VindulaTeamView(grok.View):
    grok.context(IVindulaTeam)
    grok.require('zope2.View')
    grok.name('view')
    

