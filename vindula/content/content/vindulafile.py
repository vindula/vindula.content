# -*- coding: utf-8 -*-
from five import grok

from Products.CMFCore.utils import getToolByName

from Products.ATContentTypes.interfaces.file import IATFile

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
        
    def creator(self):
        return self.context.Creator()
    
    def author(self):
        membership = getToolByName(self.context, 'portal_membership')
        return membership.getMemberInfo(self.creator())
    
    def authorname(self):
        author = self.author()
        return author and author['fullname'] or self.creator()
    
    def toLocalizedTime(self, time, long_format=None, time_only = None):
        """Convert time to localized time
        """
        util = getToolByName(self.context, 'translation_service')
        return util.ulocalized_time(time, long_format, time_only, self.context,
                                    domain='plonelocales')

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
        container: '#DV-container',
        zoom: %(zoom)s });
}
if(hash.search("\#(document|pages|text)\/") != -1 || (%(fullscreen)s &&
        hash != '#bypass-fullscreen')){
    window.currentDocument = DV.load(window.documentData, {
        sidebar: true,
        search: %(search)s,
        container: document.body,
        zoom: %(zoom)s });
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
    'data': json.dumps(self.dv_data()),
    'zoom': '800'
}
