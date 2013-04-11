# -*- coding: utf-8 -*-

from Products.Archetypes.atapi import *
from Products.Archetypes.public import DateTimeField, StringField
from plone.app.blob.content import ATBlob

from Products.Archetypes.utils import DisplayList
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implements

from DateTime.DateTime import DateTime
from vindula.content import MessageFactory as _
from vindula.content.models.content_field import ContentField
from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget



class _ExtensionDateTimeField(ExtensionField, DateTimeField):
    ''' Datetime '''
    
class _ExtensionStringField(ExtensionField, StringField):
    ''' String '''

class _ExtensionReferenceField(ExtensionField, ReferenceField):
    ''' ReferenceField '''

class _ExtensionLinesField(ExtensionField, LinesField):
    ''' LinesField '''


class _ExtensionTipoField(ExtensionField, StringField):
    def Vocabulary(self, content_instance):
        content_fields = ContentField().get_content_file_by_type(u'tipo')
        L = []
        for item in content_fields:
            L.append((item,item))
        return DisplayList(tuple(L))

class _ExtensionClassificacaoField(ExtensionField, StringField):
    def Vocabulary(self, content_instance):
        content_fields = ContentField().get_content_file_by_type(u'classificacao')
        L = []
        for item in content_fields:
            L.append((item,item))
            
        return DisplayList(L)

    
class ATFileExtender(object):
    adapts(ATBlob)
    implements(ISchemaExtender)

    fields = [
        _ExtensionReferenceField('structures',
                 multiValued=0,
                 allowed_types=('OrganizationalStructure',),
                 relationship='structures',
                 widget=VindulaReferenceSelectionWidget(
                            typeview='list',
                            label=_(u"Estrutura Organizacional"),
                            description=_(u"Selecione uma estrutura organizacional."),
                            ),
                 required=False
         ),              
        _ExtensionTipoField(
            "tipo",
            widget = SelectionWidget(
                label=u"Tipo",
                description=u"Selecione o tipo do documento.",
            ),
            enforceVocabulary=True,    
            required=False,                            
        ),

        _ExtensionStringField(
            "numero",
            widget = StringWidget(
                label=u"Numero",
                description=u"Digite o numero do documento.",
            ),
            required=False,                 
        ),              

        _ExtensionDateTimeField(
            "vigencia",
#            default_method = 'getDefaultTime',
            widget = CalendarWidget(
                label=u"Vigencia",
                description=u"Vigencia do documento",
                show_hm = False
            ),
        ),              
                          
        _ExtensionClassificacaoField(
            "classificacao",
            widget = SelectionWidget(
                label=u"Classificação",
                description=u"Selecione a Classificação do documento.",
            ),
            enforceVocabulary=True,
            required=False,
        ),
              
        _ExtensionLinesField(
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
                            
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


#    def getDefaultTime(self):
#        return DateTime()
    



