# -*- coding: utf-8 -*-
from five import grok

from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.interfaces.file import IATFile
from plone.app.blob.content import ATBlob
from zope.interface import implements
from Products.Archetypes.atapi import *

from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

from vindula.content import MessageFactory as _
from AccessControl import ClassSecurityInfo
from vindula.content.content.interfaces import IVindulaFile

from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget
from vindula.content.models.content_field import ContentField


from DateTime.DateTime import DateTime

from collective.documentviewer.convert import DUMP_FILENAME
from collective.documentviewer.convert import TEXT_REL_PATHNAME


from zope.component import getMultiAdapter
from collective.documentviewer import storage
from collective.documentviewer.utils import allowedDocumentType
from collective.documentviewer.settings import Settings
from collective.documentviewer.settings import GlobalSettings
from collective.documentviewer.utils import getPortal
from collective.documentviewer.convert import docsplit

import json



VindulaFile_schema =  ATFile.schema.copy() + Schema((


    ReferenceField('structures',
        multiValued=0,
        allowed_types=('OrganizationalStructure',),
        relationship='structures',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            typeview='list',
            label=_(u"Unidade Organizacional"),
            description=_(u"Selecione uma Unidade Organizacional."),
            ),
        required=False
    ),

    StringField(
        name='tipo',
        searchable = True,
        widget = SelectionWidget(
            label=u"Tipo",
            description=u"Selecione o tipo do documento.",
        ),
        vocabulary='get_tipo',
    ),

    StringField(
        name='numero',
        searchable = True,
        widget = StringWidget(
             label=u"Numero",
             description=u"Digite o numero do documento.",
        ),
    ),

    DateTimeField(
        name='vigencia',
        searchable = True,
        default_method = 'getDefaultTime',
        widget = CalendarWidget(
            label=u"Vigencia",
            description=u"Vigencia do documento",
              show_hm = False
        ),
    ),

    StringField(
        "classificacao",
        widget = SelectionWidget(
            label=u"Classificação",
            description=u"Selecione a Classificação do documento.",
        ),
        vocabulary='get_classificacao',
        required=False,
    ),

    LinesField(
        'themesNews',
        multiValued=1,
        accessor="ThemeNews",
        searchable=True,
        schemata='categorization',
        widget=KeywordWidget(
            label=_(u'Temas'),
            description=_(u'Selecione os temas do documento.'),
            ),
    ),


))

class VindulaFile(ATFile,ATBlob):
    """ VindulaFile """

    security = ClassSecurityInfo()
    implements(IVindulaFile)
    portal_type = 'VindulaFile'
    _at_rename_after_creation = True
    schema = VindulaFile_schema


    def getDefaultTime(self):
        return DateTime()

    def get_classificacao(self):
        content_fields = ContentField().get_content_file_by_type(u'classificacao')
        L = []
        for item in content_fields:
            L.append((item,item))

        return DisplayList(L)



    def get_tipo(self):
        content_fields = ContentField().get_content_file_by_type(u'tipo')
        L = []
        for item in content_fields:
            L.append((item,item))
        return DisplayList(tuple(L))


registerType(VindulaFile, PROJECTNAME)


def either(one, two):
    if one is None:
        return two
    return one

# View
class VindulaFileView(grok.View):
    grok.context(IATFile)
    grok.require('zope2.View')
    grok.name('file_view')

    installed = docsplit is not None
    enabled = docsplit is not None

    def update(self):
        self.site = getPortal(self.context)
        self.settings = Settings(self.context)
        self.global_settings = GlobalSettings(self.site)

        self.portal_url = getMultiAdapter((self.context, self.request),
            name="plone_portal_state").portal_url()
        self.dvstatic = "%s/++resource++dv.resources" % (
            self.portal_url)
        resource_url = self.global_settings.override_base_resource_url
        rel_url = storage.getResourceRelURL(gsettings=self.global_settings,
                                            settings=self.settings)
        if resource_url:
            self.dvpdffiles = '%s/%s' % (resource_url.rstrip('/'), rel_url)
        else:
            self.dvpdffiles = '%s/%s' % (self.portal_url, rel_url)

        utils = getToolByName(self.context, 'plone_utils')
        msg = None

        if allowedDocumentType(self.context,
                self.global_settings.auto_layout_file_types):
            if not self.installed:
                msg = "Since you do not have docsplit installed on this " + \
                      "system, we can not render the pages of this document."
            elif self.settings.converting is not None and \
                    self.settings.converting:
                msg = "The document is currently being converted to the " + \
                      "Document Viewer view."
                self.enabled = False
            elif self.settings.successfully_converted is not None and \
                    not self.settings.successfully_converted:
                msg = "There was an error trying to convert the document. " +\
                      "Maybe the document is encrypted, corrupt or " +\
                      "malformed? Check log for details."
                self.enabled = False
            elif self.settings.successfully_converted is None:
                # must have just switched to this view
                msg = "This document is not yet converted to document " +\
                      "viewer. Please click the `Document Viewer Convert` " +\
                      "button to convert."
                self.enabled = False
        else:
            self.enabled = False
            msg = "The file is not a supported document type. " + \
                  "Your type may be supported. Check out the document " + \
                  "viewer configuration settings."
        mtool = getToolByName(self.context, 'portal_membership')
        self.can_modify = mtool.checkPermission('cmf.ModifyPortalContent',
                                                self.context)
        if msg and self.can_modify:
            utils.addPortalMessage(msg)

        #return self.index()

    def annotations(self):
        data = []
        annotations = self.settings.annotations
        if annotations is None:
            return data
        for page, anns in annotations.items():
            for idx, ann in enumerate(anns):
                data.append({
                    "location": {"image": ann['coord']},
                    "title": ann['title'],
                    "id": ann['id'],
                    "page": page,
                    "access": "public",
                    "content": ann['content']})
        return data

    def sections(self):
        sections = self.settings.sections
        if sections is None:
            return []
        return sections

    def dv_data(self):
        dump_path = DUMP_FILENAME.rsplit('.', 1)[0]
        if self.global_settings.override_contributor:
            contributor = self.global_settings.override_contributor
        else:
            contributor = self.context.Creator()
        if self.global_settings.override_organization:
            organization = self.global_settings.override_organization
        else:
            organization = self.site.title
        image_format = self.settings.pdf_image_format
        if not image_format:
            # oops, this wasn't set like it should have been
            # on alpha release. We'll default back to global
            # setting.
            image_format = self.global_settings.pdf_image_format
        return {
            'access': 'public',
            'annotations': self.annotations(),
            'sections': list(self.sections()),
            'canonical_url': self.context.absolute_url() + '/view',
            'created_at': DateTime(self.context.CreationDate()).aCommonZ(),
            'data': {},
            'description': self.context.Description(),
            'id': self.context.UID(),
            'pages': self.settings.num_pages,
            'updated_at': DateTime(self.context.ModificationDate()).aCommonZ(),
            'title': self.context.Title(),
            'source': '',
            "contributor": contributor,
            "contributor_organization": organization,
            'resources': {
                'page': {
                    'image': '%s/{size}/%s_{page}.%s' % (
                        self.dvpdffiles, dump_path,
                        image_format),
                    'text': '%s/%s/%s_{page}.txt' % (
                        self.dvpdffiles, TEXT_REL_PATHNAME, dump_path)
                },
                'pdf': self.context.absolute_url(),
                'thumbnail': '%s/small/%s_1.%s' % (
                    self.dvpdffiles, dump_path,
                    image_format),
                'search': '%s/dv-search.json?q={query}' % (
                        self.context.absolute_url())
            }
        }

    def javascript(self):
        fullscreen = self.settings.fullscreen
        height = 'height: %i,' % either(self.settings.height,
                                       self.global_settings.height)
        width = either(self.settings.width,
                       self.global_settings.width)
        if width is None:
            width = "jQuery('#DV-container').width()"
        else:
            width = str(width)
        sidebar = either(self.settings.show_sidebar,
                         self.global_settings.show_sidebar)
        search = either(self.settings.show_search,
                        self.global_settings.show_search)
        return """
window.documentData = %(data)s;
var hash = window.location.hash;
window.initializeDV = function(){
/* We do this so we can reload it later when managing annotations */
    window.currentDocument = DV.load(window.documentData, { %(height)s
        sidebar: %(sidebar)s,
        width: %(width)s,
        search: %(search)s,
        container: '#DV-container' });
}
if(hash.search("\#(document|pages|text)\/") != -1 || (%(fullscreen)s &&
        hash != '#bypass-fullscreen')){
    window.currentDocument = DV.load(window.documentData, {
        sidebar: true,
        search: %(search)s,
        container: document.body });
    jQuery('body').addClass('fullscreen');
}else{
    window.initializeDV();
    jQuery('body').addClass('not-fullscreen');
}
""" % {
    'portal_url': self.portal_url,
    'height': height,
    'fullscreen': str(fullscreen).lower(),
    'sidebar': str(sidebar).lower(),
    'search': str(search).lower(),
    'width': width,
    'data': json.dumps(self.dv_data())
}

