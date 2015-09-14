#-*- coding: utf-8 -*-
from logging import getLogger
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.event import notify

from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from ZODB.POSException import ConflictError
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ATFieldProperty
from Products.Archetypes.atapi import *

try:
    from Products.LinguaPlone.public import registerType
# registerType
# make pyflakes happy...
except ImportError:
    from Products.Archetypes.atapi import registerType

from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.configuration import zconf
from Products.MimetypesRegistry.common import MimeTypeException
from Products.validation import V_REQUIRED

from plone.app.imaging.interfaces import IImageScaleHandler
from plone.app.blob.interfaces import IATBlob, IATBlobFile, IATBlobImage
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobMarshaller
from plone.app.blob.mixins import ImageMixin
from plone.app.blob.markings import markAs

from DateTime.DateTime import DateTime
from vindula.content import MessageFactory as _


from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget
from vindula.content.models.content_field import ContentField
from vindula.myvindula.tools.utils import UtilMyvindula


ATBlobSchema = ATContentTypeSchema.copy()

ATBlobSchema += Schema((

    ImageField('image_capa',
        required=True,
        languageIndependent=True,
        storage=AnnotationStorage(migrate=True),
        swallowResizeExceptions=zconf.swallowImageResizeExceptions.enable,
        pil_quality=zconf.pil_config.quality,
        pil_resize_algo=zconf.pil_config.resize_algo,
        max_size=zconf.ATImage.max_image_dimension,
        sizes={'large': (768, 768),
               'preview': (400, 400),
               'mini': (200, 200),
               'thumb': (128, 128),
               'tile': (64, 64),
               'icon': (32, 32),
               'listing': (16, 16),
               },
        validators=(('isNonEmptyFile', V_REQUIRED),
                    ('checkImageMaxSize', V_REQUIRED)),
        widget=ImageWidget(
            description='',
            label=_(u'Imagem da capa'),
            show_content_type=False,
        ),
    ),


    ReferenceField('structures',
        multiValued=0,
        allowed_types=('OrganizationalStructure',),
        relationship='structures',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            typeview='list',
            label=_(u"Unidade Organizacional Elaboradora"),
            description=_(u"Selecione a Unidade Organizacional Elaboradora do documento."),
            ),
        required=False
    ),

    ReferenceField('structuresClient',
        multiValued=1,
        allowed_types=('OrganizationalStructure',),
        relationship='structuresClient',
        widget=VindulaReferenceSelectionWidget(
            #default_search_index='SearchableText',
            typeview='list',
            label=_(u"Unidades Organizacionas Cliente"),
            description=_(u"Selecione as Unidades Organizacionais Cliente do documento ."),
            ),
        required=False
    ),

    StringField(
        name='tipo',
        searchable = True,
        widget = SelectionWidget(
            label=u"Tipologia",
            description=u"Selecione a tipologia do documento.",
            format = 'select', 
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
    
    IntegerField(
        name='revisao',
        widget=IntegerWidget(
            label=_(u"Revisão"),
            description=_(u"Número de revisão do documento."),
        ),
        default=0,
    ),

    DateTimeField(
        name='vigencia',
        searchable = True,
#        default_method = 'getDefaultTime',
        widget = CalendarWidget(
            label=u"Vigencia",
            description=u"Vigencia do documento",
            show_hm = False
        ),
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

    BooleanField(
        name='activ_portletRight',
        default=True,
        widget=BooleanWidget(
            label=_(u'Portlet Direita'),
            description=_(u'Se selecionado, ativa a visualização dos portet na coluna da direita.'),
        ),
        required=False,
    ),

    BooleanField(
        name='activ_portletLeft',
        default=False,
        widget=BooleanWidget(
            label=_(u'Portlet Esquerda'),
            description=_(u'Se selecionado, ativa a visualização dos portet na coluna da esquerda.'),
        ),
        required=False,
    ),

    BooleanField(
        name='activ_portletAccessory',
        default=True,
        widget=BooleanWidget(
            label=_(u'Portlet Acessório'),
            description=_(u'Se selecionado, ativa a visualização dos portet na coluna  acessória.'),
        ),
        required=False,
    ),

    BooleanField(
        name='activ_portletRelated',
        default=True,
        widget=BooleanWidget(
            label=_(u'Portlet Relacionado'),
            description=_(u'Se selecionado, ativa a visualização do portlet de conteúdos relacionados.'),
        ),
        required=False,
    ),

     BooleanField(
        name='activ_download',
        default=True,
        widget=BooleanWidget(
            label=_(u'Download do Arquivo?'),
            description=_(u'Caso selecionado, permite que seja feito download do arquivo.'),
        ),
        required=False,
    ),

    BooleanField(
        name='activ_discussion',
        default=True,
        widget=BooleanWidget(
            label="Ativar Comentarios",
            description='Caso selecionado, ativa a opção de comentarios.',
        ),
        required=False,
    ),


))


ATBlobSchema['title'].storage = AnnotationStorage()
# titles not required for blobs, because we'll use the filename if missing
ATBlobSchema['title'].required = False

finalizeATCTSchema(ATBlobSchema, folderish=False, moveDiscussion=False)
ATBlobSchema.registerLayer('marshall', BlobMarshaller())

invisivel = {'view':'invisible','edit':'invisible',}
ATBlobSchema['allowDiscussion'].widget.visible = invisivel
ATBlobSchema.changeSchemataForField('activ_discussion', 'settings')


try:
    from Products.CMFCore.CMFCatalogAware import WorkflowAware
    WorkflowAware       # make pyflakes happy...
    # CMF 2.2 takes care of raising object events for old-style factories
    hasCMF22 = True
except ImportError:
    hasCMF22 = False

def addATBlob(container, id, subtype='Blob', **kwargs):
    """ extended at-constructor copied from ClassGen.py """
    obj = ATBlob(id)
    if subtype is not None:
        markAs(obj, subtype)    # mark with interfaces needed for subtype
    if not hasCMF22:
        notify(ObjectCreatedEvent(obj))
    container._setObject(id, obj, suppress_events=hasCMF22)
    obj = container._getOb(id)
    if hasCMF22:
        obj.manage_afterAdd(obj, container)
    obj.initializeArchetype(**kwargs)
    if not hasCMF22:
        notify(ObjectModifiedEvent(obj))
    return obj.getId()

def addATBlobFile(container, id, **kwargs):
    return addATBlob(container, id, subtype='File', **kwargs)

def addATBlobImage(container, id, **kwargs):
    return addATBlob(container, id, subtype='Image', **kwargs)


class ATBlob(ATCTFileContent, ImageMixin):
    """ a chunk of binary data """
    implements(IATBlob)

    portal_type = 'Blob'
    _at_rename_after_creation = True
    schema = ATBlobSchema

    title = ATFieldProperty('title')
    summary = ATFieldProperty('description')

    security = ClassSecurityInfo()
    cmf_edit_kws = ('file',)

    def getDefaultTime(self):
        return DateTime()

    def get_tipo(self):
        content_fields = ContentField().get_content_file_by_type(u'tipo')
        L = [('', '-- Selecione --')]
        for item in content_fields:
            L.append((item,item))
            
        return DisplayList(tuple(L))


    security.declareProtected(View, 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the file (use default index_html)
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE

        if self.activ_download:
            field = self.getPrimaryField()
            return field.download(self, REQUEST, RESPONSE)
        else:
            url = self.aq_parent.absolute_url()
            UtilMyvindula().setStatusMessage('error','Este arquivo não está autorizado para download')
            self.REQUEST.RESPONSE.redirect(url)




    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline or as an attachment """

        field = self.getPrimaryField()
        if IATBlobImage.providedBy(self):
            return field.index_html(self, REQUEST, RESPONSE)
        elif field.getContentType(self) in ATFile.inlineMimetypes:
            if self.activ_download:
                return field.index_html(self, REQUEST, RESPONSE)
            else:
                url = self.aq_parent.absolute_url()
                UtilMyvindula().setStatusMessage('error','Este arquivo não está autorizado para download')
                self.REQUEST.RESPONSE.redirect(url)
        else:
            if self.activ_download:
                return field.download(self, REQUEST, RESPONSE)
            else:
                url = self.aq_parent.absolute_url()
                UtilMyvindula().setStatusMessage('error','Este arquivo não está autorizado para download')
                self.REQUEST.RESPONSE.redirect(url)

    security.declarePrivate('getBlobWrapper')
    def getBlobWrapper(self):
        """ return wrapper class containing the actual blob """
        accessor = self.getPrimaryField().getAccessor(self)
        return accessor()

    security.declareProtected(View, 'getFile')
    def getFile(self, **kwargs):
        """ archetypes.schemaextender (wisely) doesn't mess with classes,
            so we have to provide our own accessor """
        return self.getBlobWrapper()

    security.declareProtected(ModifyPortalContent, 'setFile')
    def setFile(self, value, **kwargs):
        """ set the file contents and possibly also the id """
        mutator = self.getField('file').getMutator(self)
        mutator(value, **kwargs)

    def _should_set_id_to_filename(self, filename, title):
        """ If title is blank, have the caller set my ID to the
            uploaded file's name. """
        # When the title is blank, sometimes the filename is returned
        return filename == title or not title

    # index accessor using portal transforms to provide index data

    security.declarePrivate('getIndexValue')
    def getIndexValue(self, mimetype='text/plain'):
        """ an accessor method used for indexing the field's value
            XXX: the implementation is mostly based on archetype's
            `FileField.getIndexable` and rather naive as all data gets
            loaded into memory if a suitable transform was found.
            this should probably use `plone.transforms` in the future """

        field = self.getPrimaryField()
        source = field.getContentType(self)
        transforms = getToolByName(self, 'portal_transforms')
        if transforms._findPath(source, mimetype) is None:
            return ''
        value = str(field.get(self))
        filename = field.getFilename(self)
        try:
            return str(transforms.convertTo(mimetype, value,
                mimetype=source, filename=filename))
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            getLogger(__name__).exception('exception while trying to convert '
               'blob contents to "text/plain" for %r', self)

    # compatibility methods when used as ATFile replacement

    security.declareProtected(View, 'get_data')
    def get_data(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        return str(self.getBlobWrapper())

    data = ComputedAttribute(get_data, 1)

    def __str__(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        if IATBlobImage.providedBy(self):
            return self.getPrimaryField().tag(self)
        else:
            return self.get_data()

    def __repr__(self):
        """ try to mimic the the old file and image types from ATCT
            for improved test compatibility """
        res = super(ATBlob, self).__repr__()
        if IATBlobFile.providedBy(self):
            res = res.replace(ATBlob.__name__, 'ATFile', 1)
        elif IATBlobImage.providedBy(self):
            res = res.replace(ATBlob.__name__, 'ATImage', 1)
        return res

    security.declareProtected(ModifyPortalContent, 'setFilename')
    def setFilename(self, value, key=None):
        """ convenience method to set the file name on the field """
        self.getBlobWrapper().setFilename(value)

    security.declareProtected(ModifyPortalContent, 'setFormat')
    def setFormat(self, value):
        """ convenience method to set the mime-type """
        self.getBlobWrapper().setContentType(value)

    security.declarePublic('getIcon')
    def getIcon(self, relative_to_portal=False):
        """ calculate an icon based on mime-type """
        contenttype = self.getBlobWrapper().getContentType()
        mtr = getToolByName(self, 'mimetypes_registry', None)
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException:
            mimetypeitem = None
        if mimetypeitem is None or mimetypeitem == ():
            return super(ATBlob, self).getIcon(relative_to_portal)
        icon = mimetypeitem[0].icon_path
        if not relative_to_portal:
            utool = getToolByName(self, 'portal_url')
            icon = utool(relative=1) + '/' + icon
            while icon[:1] == '/':
                icon = icon[1:]
        return icon

    security.declarePrivate('cmf_edit')
    def cmf_edit(self, precondition='', file=None, title=None, **kwargs):
        # implement cmf_edit for image and file distinctly
        primary_field_name = self.getPrimaryField().getName()
        if file is not None and primary_field_name == 'image':
            self.setImage(file)
        elif file is not None and primary_field_name == 'file':
            self.setFile(file)
        if title is not None:
            self.setTitle(title)
        if kwargs:
            self.edit(**kwargs)
        else:
            self.reindexObject()

    # compatibility methods when used as ATImage replacement

    def __bobo_traverse__(self, REQUEST, name):
        """ helper to access image scales the old way during
            `unrestrictedTraverse` calls """
        if isinstance(REQUEST, dict):
            if '_' in name:
                fieldname, scale = name.split('_', 1)
            else:
                fieldname, scale = name, None
            field = self.getField(fieldname)
            handler = IImageScaleHandler(field, None)
            if handler is not None:
                image = handler.getScale(self, scale)
                if image is not None:
                    return image
        return super(ATBlob, self).__bobo_traverse__(REQUEST, name)


    def getImageIcone(self):
        obj = self
        base = self.portal_url() + "/++resource++vindula.content/images/"

        if obj.content_type in ['application/pdf', 'application/x-pdf', 'image/pdf']:
            url = base + "icon-pdf.png"
        elif obj.content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',\
                                  'application/vnd.openxmlformats-officedocument.wordprocessingml.template']:
            url = base + "icon-word.png"
        elif obj.content_type in ['application/vnd.ms-powerpoint', 'application/powerpoint', 'application/mspowerpoint', 'application/x-mspowerpoint',\
                                  'application/vnd.openxmlformats-officedocument.presentationml.presentation', 'application/vnd.openxmlformats-officedocument.presentationml.slideshow']:
            url = base + "icon-ppoint.png"
        elif obj.content_type in ['application/vnd.ms-excel', 'application/msexcel', 'application/x-msexcel',\
                                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.openxmlformats-officedocument.spreadsheetml.template']:
            url = base + "icon-excel.png"
        else:
            url = base + "icon-default.png"

        return url
    
    def getStatus(self):
        dt_vigencia = self.getVigencia()
        if (not dt_vigencia or dt_vigencia > DateTime()):
            return True
        else:
            return False

registerType(ATBlob, packageName)
