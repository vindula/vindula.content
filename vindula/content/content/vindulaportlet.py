# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from zope.app.component.hooks import getSite 
from zope.interface import Interface
from vindula.content.content.interfaces import IVindulaPortlet

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.ATContentTypes.content.document import ATDocumentBase
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

VindulaPortlet_schema = ATDocumentSchema.copy() + Schema((

   ReferenceField('imageRelac',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem "),
        relationship='Imagem',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Imagem "),
            description='Imagem para destaque no portlet. A imagem será redimensionada para um tamanho adequado.')),

    TextField(
            name='title_image',
            widget=StringWidget(
                label=_(u"Título da Imagem"),
                description=_(u"Título para a imagem de destaque no portlet."),
            ),
        required=False,
    ),

   ReferenceField('linkRelac',
        multiValued=0,
        allowed_types=(),
        label=_(u"Link de detalhes"),
        relationship='linkRelac',
        widget=ReferenceBrowserWidget(
            default_search_index='SearchableText',
            label=_(u"Link de detalhes"),
            description='Caso fornecido, rodapé terão link para esta URL.')),

    TextField(
            name='title_link',
            widget=StringWidget(
                label=_(u"Título do link"),
                description=_(u"Título para o link do rodape do portlet."),
                
            ),
        required=False,
        default=u'Saíba Mais'
    ),  

    BooleanField(
        name='activ_recurcividade',
        default=False,
        widget=BooleanWidget(
            label="Ativar Recursividade",
            description='Se selecionado, Ativa a opção de recursividade do portlet em níveis inferiores.',
        ),
        required=False,
    ),

    BooleanField(
        name='bloquea_portlet',
        default=False,
        widget=BooleanWidget(
            label="Bloquea Portlets dos níveis superiores",
            description='Se selecionado, Ira bloquear todos os portlets dos níveis superiores do portal.(Cautela para usar esta opção)',
        ),
        required=False,
    ),
    

))
invisivel = {'view':'invisible','edit':'invisible',}

VindulaPortlet_schema['description'].widget.visible = invisivel
finalizeATCTSchema(VindulaPortlet_schema, folderish=False)

class VindulaPortlet(ATDocumentBase):
    """ Reserve Content for VindulaPortlet"""
    security = ClassSecurityInfo()    
    
    implements(IVindulaPortlet)    
    portal_type = 'VindulaPortlet'
    _at_rename_after_creation = True
    schema = VindulaPortlet_schema

registerType(VindulaPortlet, PROJECTNAME) 

   

# View
class VindulaportletView(grok.View):
    grok.context(IVindulaPortlet)
    grok.require('zope2.View')
    grok.name('view')
  


