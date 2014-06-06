# -*- coding: utf-8 -*-

from vindula.content import MessageFactory as _
from Products.Archetypes.atapi import *

from Products.SmartColorWidget.Widget import SmartColorWidget
from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget

OSInf_schema =  Schema((

    StringField(
        name = 'email',
        widget=StringWidget(
            label= 'Email da Unidade',
            description= 'Digite o email de contato da unidade.',
        ),
        schemata = 'Informações'
    ),
    
    StringField(
        name = 'phone_number',
        widget=StringWidget(
            label= 'Telefone da Unidade',
            description= 'Digite o telefone de contato.',
        ),
        schemata = 'Informações'
    ),

    StringField(
        name = 'phone_alternative',
        widget=StringWidget(
            label= 'Telefone Alternativo da Unidade',
            description= 'Digite o telefone alternativo de contato.',
        ),
        schemata = 'Informações'
    ),
    
    StringField(
        name='wsId',
        widget=StringWidget(
            label=_(u"Id do Web Service"),
            description=_(u"Id relacionado com essa mesma UO no banco de dados. (Campo utilizado na atualização automática, cuidado ao altera-lo)"),
        ),
        schemata = 'Informações',
    ),

    BooleanField(
        name='is_unidade_negocio',
        default=False,
        widget=BooleanWidget(
            label="Unidade de Negocio",
            description='Se selecionado, Marca essa unidade como uma unidade de Negocio.',
        ),
        schemata = 'Informações'
    ),
    
    StringField(
        name = 'codigo',
        widget=StringWidget(
            label= 'Código',
            description= 'Digite o codigo dessa unidade.',
        ),
        required=False,
        schemata = 'Informações'
    ),    

))