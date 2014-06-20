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
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from vindula.content.config import *
import urlparse
from urllib import quote

from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget 

InternalLink_schema = ATLinkSchema.copy() + Schema((

   ReferenceField('internal_link',
        multiValued=0,
        label=_(u"Link Interno"),
        relationship='internal_link',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            typeview='list',
            label=_(u"Link Interno"),
            description=_(u'Selecione um conteudo interno para fazer referencia.'))),
                                                    
    BooleanField(
        name='new_tab',
        widget=BooleanWidget(
            label=_(u"Abrir em uma nova aba"),
            description=_(u"Selecione para abrir o link em uma nova aba"),
            label_msgid='vindula_themedefault_label_recurrent',
            description_msgid='vindula_themedefault_help_recurrent',
            i18n_domain='vindula_themedefault',
        ),
        default=False         
    ),                                                  

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
    meta_type = "InternalLink"
    _at_rename_after_creation = True
    schema = InternalLink_schema
    
    security.declareProtected(ModifyPortalContent, 'setRemoteUrl')
    
    def get_NewTab(self):
        newtab = self.getNew_tab()
        if newtab:
            str_url = '_blank'
            return str_url

    
    def setRemoteUrl(self, value, **kwargs):
        """remute url mutator

        Use urlparse to sanify the url
        Also see http://dev.plone.org/plone/ticket/3296
        """
        if value:
            value = urlparse.urlunparse(urlparse.urlparse(value))
        self.getField('remoteUrl').set(self, value, **kwargs)

    security.declareProtected(View, 'remote_url')
    def remote_url(self):
        """CMF compatibility method
        """
        return self.getRemoteUrl()

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, remote_url=None, **kwargs):
        if not remote_url:
            remote_url = kwargs.get('remote_url', None)
        self.update(remoteUrl = remote_url, **kwargs)

    security.declareProtected(View, 'getRemoteUrl')
    def getRemoteUrl(self):
        """Sanitize output
        """
        if self.getInternal_link():
            try:
                value = self.getInternal_link().absolute_url()
            except Exception as e:
                print 'Erro retornando a URL do link interno: %s' % (e)
                value = self.Schema()['remoteUrl'].get(self) 
        else:
            value = self.Schema()['remoteUrl'].get(self)
        if not value: value = '' # ensure we have a string
        return quote(value, safe='?$#@/:=+;$,&%')

registerType(InternalLink, PROJECTNAME)