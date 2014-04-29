# -*- coding: utf-8 -*-
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.UserAndGroupSelectionWidget.at import widget

from vindula.content import MessageFactory as _

RequiredReadingSchema = Schema((
                                        
    BooleanField('requiredReading',
        required=False,
        languageIndependent=True,
        schemata='categorization',
        widget=BooleanWidget(
            description=_(u'help_required_reading', default=u'Se selecionado, esse item terá sua leitura obrigatória'),
            label=_(u'label_required_reading', default=u'Leitura obrigatória'),
            visible={'view': 'hidden',
                     'edit': 'visible'},
            ),
        ),

    DateTimeField('startDateReqRead',
        required=False,
        languageIndependent=True,
        schemata='categorization',
        widget=CalendarWidget(
            label=_(u'label_start_date_req_read', u'Data inicial'),
            description=_(u'help_start_date_req_read',
                          default=u"Data inicial que o item terá sua leitura obrigatória.<br/>Se não "
                                   "for selecionada nenhuma data o item sempre terá sua leitura obrigatória."),
            visible={'view': 'hidden',
                     'edit': 'visible'},
            ),
        ),

    DateTimeField('expirationDateReqRead',
        required=False,
        languageIndependent=True,
        schemata='categorization',
        widget=CalendarWidget(
            label=_(u'label_expiration_date_req_read', u'Data de expiração'),
            description=_(u'help_expiration_date_req_read',
                          default=u"Data final que o item terá sua leitura obrigatória.<br/>Se não "
                                   "for selecionada nenhuma data o item sempre terá sua leitura obrigatória."),
            visible={'view': 'hidden',
                     'edit': 'visible'},
            ),
        ),
                               
    LinesField("usersGroupsReqRead",
        required=False,
        multiValued=1,
        schemata='categorization',
        widget = widget.UserAndGroupSelectionWidget(
            label=_(u'label_users_groups_req_read', u"Usuários e grupos para leitura obrigatória"),
            description=_(u'help_users_groups_req_read', u"Usuários e grupos de usuários para qual esse item terá sua leitura obrigatória. <br/>Se não "
                                                          "for selecionado nenhum usuário o item terá leitura obrigatória para todos os usuários."),
            visible={'view': 'hidden',
                     'edit': 'visible'},
            ),
        ),

    ))