# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from vindula.content.content.interfaces import IProcedure

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *

from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.config import ICONMAP
from Products.Archetypes.BaseContent import BaseContent
from Products.MimetypesRegistry.common import MimeTypeException
from Products.ATContentTypes.content.schemata import ATContentTypeSchema

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *
from DateTime.DateTime import *
from zope.interface import implements
from Products.Archetypes.public import registerType

from urllib import quote


from Products.CMFCore.permissions import View
from Products.CMFCore.permissions import ModifyPortalContent

from Products.ATContentTypes.configuration import zconf

from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation.config import validation
from Products.validation import V_REQUIRED

validation.register(MaxSizeValidator('checkFileMaxSize',
                                     maxsize=zconf.ATFile.max_file_size))

Procedure_schema = ATContentTypeSchema.copy() + Schema((
                                                        
    FileField('file',
              required=True,
              primary=True,
              searchable=True,
              languageIndependent=True,
              storage = AnnotationStorage(migrate=True),
              validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkFileMaxSize', V_REQUIRED)),
              widget = FileWidget(
                        description = '',
                        label=_(u'label_file', default=u'Arquivo'),
                        show_content_type = False,)),

    StringField(
        name = 'refNumber',
        searchable = True,
        widget=StringWidget(
            label='Número de referência',
            description="Insira o número de referência.",
        ),
    ),
    
    StringField(
        name = 'revisionNumber',
        searchable = True,
        widget=StringWidget(
            label='Número da revisão',
            description="Insira o número da revisão.",
        ),
    ),
    
    DateTimeField(
        'uploadDate',
        searchable = True,
        default_method = 'getDefaultTime',
        widget=CalendarWidget(
            show_hm=False,
            label=_(u'label_uploadDate', u'Data de upload'),
            description=_(u'help_uploadDate',
                          default=u"Data do upload do procedimento"),
        ),
    ),                 

))

#invisivel = {'view':'invisible','edit':'invisible',}

finalizeATCTSchema(Procedure_schema, folderish=False)

class Procedure(ATCTFileContent):
    """ Reserve Content for VindulaNews"""
    schema         =  Procedure_schema

    portal_type    = 'Procedure'
    archetype_name = 'Procedure'
    _atct_newTypeFor = {'portal_type' : 'Procedure', 'meta_type' : 'Procedure'}
    assocMimetypes = ('application/*', 'audio/*', 'video/*', )
    assocFileExt   = ()
    cmf_edit_kws   = ()
    inlineMimetypes= ('application/msword',
                      'application/x-msexcel', # ?
                      'application/vnd.ms-excel',
                      'application/vnd.ms-powerpoint',
                      'application/pdf',
                      'application/x-shockwave-flash',)

    implements(IProcedure)

    security       = ClassSecurityInfo()
    
    def getDefaultTime(self):
        return DateTime()
    
    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Download the file
        """
        field = self.getPrimaryField()

        if field.getContentType(self) in self.inlineMimetypes:
            # return the PDF and Office file formats inline
            return ATCTFileContent.index_html(self, REQUEST, RESPONSE)
        # otherwise return the content as an attachment 
        # Please note that text/* cannot be returned inline as
        # this is a security risk (IE renders anything as HTML).
        return field.download(self)

    security.declareProtected(ModifyPortalContent, 'setFile')
    def setFile(self, value, **kwargs):
        """Set id to uploaded id
        """
        self._setATCTFileContent(value, **kwargs)

    def __str__(self):
        """cmf compatibility
        """
        return self.get_data()

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=0):
        """Calculate the icon using the mime type of the file
        """
        field = self.getField('file')
        if not field or not self.get_size():
            # field is empty
            return BaseContent.getIcon(self, relative_to_portal)

        contenttype       = field.getContentType(self)
        contenttype_major = contenttype and contenttype.split('/')[0] or ''

        mtr   = getToolByName(self, 'mimetypes_registry', None)
        utool = getToolByName( self, 'portal_url' )

        if ICONMAP.has_key(contenttype):
            icon = quote(ICONMAP[contenttype])
        elif ICONMAP.has_key(contenttype_major):
            icon = quote(ICONMAP[contenttype_major])
        else:
            mimetypeitem = None
            try:
                mimetypeitem = mtr.lookup(contenttype)
            except MimeTypeException, msg:
                LOG.error('MimeTypeException for %s. Error is: %s' % (self.absolute_url(), str(msg)))
            if not mimetypeitem:
                return BaseContent.getIcon(self, relative_to_portal)
            icon = mimetypeitem[0].icon_path

        if relative_to_portal:
            return icon
        else:
            # Relative to REQUEST['BASEPATH1']
            res = utool(relative=1) + '/' + icon
            while res[:1] == '/':
                res = res[1:]
            return res

    security.declareProtected(View, 'icon')
    def icon(self):
        """for ZMI
        """
        return self.getIcon()

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, precondition='', file=None):
        if file is not None:
            self.setFile(file)
    
    
registerType(Procedure, PROJECTNAME) 


class ListProceduresView(grok.View):
    grok.context(Interface)
    grok.require('cmf.SetOwnPassword') 
    grok.name('list-procedures')
    
    
    def getContext(self, context):
        if context:
            if context.portal_type in ['Plone Site', 'Folder', 'VindulaFolder']:
                return context
            else:
                return self.getContext(context.aq_parent)
        else:
            return None
    
    
    def getProcedures(self, context=None):
        p_catalog = getToolByName(self.context, 'portal_catalog')
        
        query = {#'review_state': ['published', 'external'],
                 'portal_type': 'File',
                 'sort_on': 'getObjPositionInParent',}
        
        if not context:
            context = self.context.portal_url.getPortalObject()
            
        query['path'] = {'query': '/'.join(context.getPhysicalPath()), 'depth': 99}
        
        result = p_catalog(**query)
        items = []
        for item in result:
            items.append(item.getObject())
        
        return items
        
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
