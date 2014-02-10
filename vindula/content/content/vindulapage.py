# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from plone.app.discussion.interfaces import IConversation
from vindula.content.content.interfaces import IVindulaPage

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *

from vindula.content.content.vindulanews import VindulaNews, VindulaNews_schema
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from vindula.content.config import *
from plone.contentrules.engine.interfaces import IRuleAssignable

from Products.UserAndGroupSelectionWidget.at import widget
from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget

VindulaPage_schema = VindulaNews_schema.copy() + Schema((
   
    LinesField(
        'themesNews',
        multiValued=1,
        accessor="ThemeNews",
        searchable=True,
        schemata='categorization',
        widget=KeywordWidget(
            label=_(u'Temas'),
            description=_(u'Selecione os temas da noticia.'),
            ),
    ),

    TextField(
        name='previewPage',
        multiValued=1,
        accessor="PreviewPage",
        default_content_type = 'text/html',
            default_output_type = 'text/x-html-safe',
            widget=RichWidget(
                label=_(u"Preview page usuários"),
                description=_(u"Preview da página todos os usuários."),
                rows="10",
            ),
            required=False,
    ),


    LinesField(
            name="usuarios",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Usuários permitidos para visualizar o conteúdo completo."),
                description=_(u"Selecione todos os usuários com privilégios para visualizar o conteúdo completo."),
                usersOnly=True,
                ),
            required=True,
            ),

    BooleanField(
        name='activ_discussion',
        default=True,
        widget=BooleanWidget(
            label="Ativar Comentários",
            description='Caso selecionado, ativa a opção de comentários.',
        ),
        required=False,
    ),

))

invisivel = {'view':'invisible','edit':'invisible',}
#VindulaNews_schema['description'].widget.label = 'Sumário'
#VindulaNews_schema['description'].widget.description = 'Utilizado nas listagens de itens e resultado de buscas'

VindulaNews_schema['text'].widget.label = _(u"Visualização completa")
VindulaNews_schema['text'].widget.description = _(u"Visualização completa para os usuários/grupos selecionados.")
#VindulaNews_schema['image'].widget.visible = invisivel


VindulaPage_schema['allowDiscussion'].widget.visible = invisivel

finalizeATCTSchema(VindulaPage_schema, folderish=False)
#VindulaNews_schema.changeSchemataForField('activ_share', 'settings')
#VindulaNews_schema.changeSchemataForField('activ_share_footer', 'settings')
VindulaPage_schema.changeSchemataForField('activ_discussion', 'settings')
#VindulaNews_schema.changeSchemataForField('themesNews', 'categorization')


class VindulaPage(VindulaNews):
    """ Reserve Content for VindulaPage"""
    security = ClassSecurityInfo()

    implements(IVindulaPage, IRuleAssignable)
    portal_type = 'VindulaPage'
    _at_rename_after_creation = True
    schema = VindulaPage_schema


registerType(VindulaPage, PROJECTNAME)


# View
class VindulaPageView(grok.View):
    grok.context(IVindulaPage)
    grok.require('zope2.View')
    grok.name('view')


    enable_fulltext = False

    def update(self):
        context = self.context

        portal_membership = getToolByName(context, "portal_membership")
        groups_tool = getToolByName(context, 'portal_groups')

        user_login = portal_membership.getAuthenticatedMember()
        username = user_login.getUserName()

        groups = groups_tool.getGroupsByUserId(username)

        if username in context.getUsuarios():
            self.enable_fulltext = True

        for group in groups:
            if group.id in context.getUsuarios():
                self.enable_fulltext = True
                break
