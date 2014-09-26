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


    BooleanField(
        name='activ_personalit',
        default=False,
        widget=BooleanWidget(
            label="Ativar Personalização",
            description='Se selecionado, Ativa a opção de personalização dos itens inferiores a Unidade Organizacional.',
        ),
        schemata = 'Layout'
    ),

    TextField(
        name='text_subrodape',
        default_content_type = 'text/html',
        default_output_type = 'text/x-html-safe',

        searchable = True,
        widget=RichWidget(
            label=_(u"Sub Rodape"),
            description=_(u"Texto para o subrodapé."),
            rows=10,
        ),
        required=False,
        schemata='Layout'
    ),




    # StringField(
    #     name='corGeralPortal',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor',
    #         description="Cor para esta área, todo o layout desta área usará esta cor.",
    #     ),
    #     schemata = 'Layout'
    # ),

    ReferenceField('logoPortal',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Logo"),
        relationship='logoPortal',
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Logo "),
            description='Será exibido no topo do portal desta área. A imagem será redimensionada para um tamanho adequado.'),
        schemata = 'Layout'
    ),

    # ReferenceField('logoRodape',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     label=_(u"Logo Rodapé "),
    #     relationship='logoRodape',
    #     widget=VindulaReferenceSelectionWidget(
    #         #default_search_index='SearchableText',
    #         label=_(u"Logo Rodapé"),
    #         description='Será exibido no rodapé desta área o imagem selecionada. A imagem será redimensionada para um tamanho adequado.'),
    #     schemata = 'Layout'
    # ),


    # #-----------BackGroup do portal------------------
    # ReferenceField('imageBackground',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     label=_(u"WallPapper do portal "),
    #     relationship='imageBackground',
    #     widget=VindulaReferenceSelectionWidget(
    #         label=_(u"Imagem de fundo do portal"),
    #         description='A imagem será aplicada no background do portal. A imagem será mostrada em seu tamanho original, sem repetição.'),
    #     schemata = 'Layout'
    # ),

    # StringField(
    #     name = 'posicaoImageBackground',
    #     widget=SelectionWidget(
    #         label='Posição da imagem de fundo',
    #         description="Selecione o coportamento da imagem de fundo.",
    #         format = 'select',
    #     ),
    #     vocabulary = [('no-repeat', 'Centralizar'), ('repeat', 'Repetir na pagina toda'), ('repeat-x', 'Repetir horizontalmente'), ('repeat-y', 'Repetir verticamente'),],
    #     default='no-repeat',
    #     schemata = 'Layout'
    # ),

    # StringField(
    #     name='corBackground',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor de background',
    #         description="Cor para o background do portal, caso a imagem não carregue ou não esteja selecionada.",
    #     ),
    #     schemata = 'Layout'
    # ),

    # ReferenceField('imageFooter',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     label=_(u"Imagem para o rodapé do portal."),
    #     relationship='imageFooter',
    #     widget=VindulaReferenceSelectionWidget(
    #         label=_(u"Imagem para o rodapé do portal"),
    #         description='A imagem selecionada será exibida no rodapé do portal. Selecione uma imagem com dimenções 980x121'),
    #     schemata = 'Layout'
    # ),

    # #-----------Menu do portal------------------#

    # StringField(
    #     name='corMenuFundo',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor de fundo do menu',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFundo.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuFonte',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor da fonte do menu',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonte.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuHoverDropdown',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor do background do menu dropdown',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuHoverDropdown.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # ReferenceField('imageSubmenuBkg',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     label=_(u"Imagem para o background do menu dropdown"),
    #     relationship='imageBkgSubmenu',
    #     widget=VindulaReferenceSelectionWidget(
    #         label=_(u"Imagem para background do menu Dropdown"),
    #         description='A imagem selecionada será exibida como plano de fundo do menu dropdown.\
    #                      A imagem será mostrada com a sua largura original, com repetição.'),
    #     schemata = 'Menu'
    # ),

    # ReferenceField('imageMenuBkg',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     label=_(u"Imagem para o background do menu dropdown"),
    #     relationship='imageBkgMenu',
    #     widget=VindulaReferenceSelectionWidget(
    #         label=_(u"Imagem para background do primeiro nível do menu"),
    #         description='A imagem selecionada será exibida como plano de fundo do menu.\
    #                      A imagem será mostrada em seu tamanho original, com repetição.'),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuFonteDropdown',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor da fonte do menu dropdown',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteDropdown.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuFonteHoverDropdown',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor da fonte do menu quando ativo no menu dropdown',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteHoverDropdown.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuDropdownHover',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor do background do link ativo dentro do menu dropdown',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuDropdownHover.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuSelected',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor do background do link selecionado no primeiro nível do menu',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuSelected.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuFonteSelected',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor da fonte do link selecionado no primeiro nível do portal',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteSelected.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuSelectedDropdown',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor do background do link selecionado no menu dropdown',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuSelectedDropdown.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # StringField(
    #     name='corMenuFonteSelectedDropdown',
    #     searchable=0,
    #     required=0,
    #     widget=SmartColorWidget(
    #         label='Cor da fonte do link selecionado no menu ',
    #         description="Clique <a class='visualizacao' href='/++resource++vindula.controlpanel/menu/corMenuFonteSelectedDropdown.png'>aqui para exemplo</a>",
    #     ),
    #     schemata = 'Menu'
    # ),

    # # CONFIGURACAO DO TEMA DO PORTLET

    # ReferenceField('imageTopPortlet',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     relationship='imageTopPortlet',
    #     widget=VindulaReferenceSelectionWidget(
    #         label=_(u"Imagem para aparecer no topo do portlet"),
    #         description='A imagem selecionada será exibida como plano de fundo do menu.\
    #                      A imagem será mostrada com a sua altura original, com repetição.'),
    #     schemata = 'Portlet'

    # ),

    # IntegerField(
    #     name='heightTopPortlet',
    #     widget=IntegerWidget(
    #         label='Altura do topo do portlet',
    #         description='Altura, em pixels, do topo do portlet. Quando não definida, manterá o padrão de 15px',
    #     ),
    #     schemata = 'Portlet'
    # ),

    # ReferenceField('imageMiddlePortlet',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     relationship='imageMiddlePortlet',
    #     widget=VindulaReferenceSelectionWidget(
    #         label=_(u"Imagem para aparecer no meio do portlet"),
    #         description='A imagem selecionada será exibida como plano de fundo do menu.\
    #                      A imagem será mostrada com a sua altura original, com repetição.'),
    #     schemata = 'Portlet'
    # ),

    # ReferenceField('imageBottomPortlet',
    #     multiValued=0,
    #     allowed_types=('Image'),
    #     relationship='imageBottomPortlet',
    #     widget=VindulaReferenceSelectionWidget(
    #         label=_(u"Imagem para aparecer em baixo do portlet"),
    #         description='A imagem selecionada será exibida como plano de fundo do menu.\
    #                      A imagem será mostrada com a sua altura original, com repetição.'),
    #     schemata = 'Portlet'
    # ),

    # IntegerField(
    #     name='heightBottomPortlet',
    #     widget=IntegerWidget(
    #         label='Altura do rodapé do portlet',
    #         description='Altura, em pixels, do topo do portlet. Quando não definida manterá o padrão de 23px',
    #     ),
    #     schemata = 'Portlet'
    # ),

))