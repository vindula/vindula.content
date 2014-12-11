# -*- coding: utf-8 -*-

from vindula.content import MessageFactory as _
from Products.Archetypes.atapi import *

from Products.SmartColorWidget.Widget import SmartColorWidget
from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget

OSTheme_schema =  Schema((

    ReferenceField('layout_content',
        multiValued=0,
        allowed_types=('Layout'),
        relationship='layout_content',
        label=_(u"Conteúdo principal da unidade"),
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Conteúdo principal da unidade"),
            description='Conteúdo do layout que irá aaparacer no portlet lateral da unidade'),
        schemata = 'Layout'
    ),

    ReferenceField('layout_accessory',
        multiValued=0,
        allowed_types=('Layout'),
        relationship='layout_accessory',
        label=_(u"Conteúdo do portlet acessório da unidade"),
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Conteúdo do portlet acessório da unidade"),
            description='Conteúdo do layout que irá aaparacer no portlet acessorio lateral da unidade'),
        schemata = 'Layout'
    ),

))