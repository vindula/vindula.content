# -*- coding: utf-8 -*-
from vindula.content import MessageFactory as _

from plone.app.folder.folder import ATFolder
from vindula.content.content.interfaces import IOrganizationalStructure
from zope.component import adapter
from zope.event import notify
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.UserAndGroupSelectionWidget.at import widget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *
from AccessControl import ClassSecurityInfo
from plone.contentrules.engine.interfaces import IRuleAssignable

from zope.app.component.hooks import getSite

from vindula.myvindula.models.funcdetails import FuncDetails
from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget
from vindula.content.content.orgstructure.subscribe import OrgstructureModifiedEvent

from vindula.content.content.orgstructure.theme import OSTheme_schema
from vindula.content.content.orgstructure.information import OSInf_schema

OrganizationalStructure_schema =  ATFolder.schema.copy() + OSTheme_schema + OSInf_schema + Schema((

    TextField(
            name='siglaunidade',
            # default_content_type = 'text/restructured',
            # default_output_type = 'text/x-html-safe',
            widget=StringWidget(
                label=_(u"Sigla da Unidade"),
                description=_(u"Informe a sigla da Unidade."),
                # rows="10",
            ),
            required=True,
    ),

    ReferenceField('structures',
        multiValued=0,
        allowed_types=('OrganizationalStructure',),
        relationship='structures',
        widget=VindulaReferenceSelectionWidget(
            typeview='list',
            label=_(u"Escolha uma Unidade Organizacional Pai"),
            description=_(u"Selecione uma Unidade Organizacional para ser Pai. "
                          u"Esta escolha fará com que esta Unidade Organizacional apareça como filho da escolhida"),

            ),
        required=False
    ),

    ReferenceField('units',
        multiValued=0,
        allowed_types=('Unit',),
        relationship='units',
        widget=VindulaReferenceSelectionWidget(
            typeview='list',
            label=_(u"Escolha um Campus"),
            description=_(u"Selecione o Campus da Unidade Organizacional"),
            ),
        required=False
    ),

    BooleanField(
        name='unidadeEspecial',
        default=False,
        widget=BooleanWidget(
            label="Unidade Especial",
            description='Caso ativado, Unidade Organizacional será exibida entre '
                        'pontilhados no Organograma, indicando que ela não tem Unidades Irmãs.',
        ),
    ),

    StringField(
        name = 'tipounidade',
        widget=SelectionWidget(
            label= 'Tipo de Unidade',
            description= 'Selecione o tipo de Unidade Organizacional.',
            format = 'select',
        ),
        vocabulary = 'getTipoUnidades',
        searchable = True,
    ),

    BooleanField(
        name='enable_organograma',
        default=True,
        widget=BooleanWidget(
            label="Visível no Organograma",
            description='Caso ativado, Unidade Organizacional será exibida no bloco de organograma.',
        ),
    ),

    LinesField(
            name="employees",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Funcionários desta Unidade Organizacional"),
                description=_(u"Selecione os participantes da Unidade Organizacional."),
                usersOnly=True,
                ),
            required=True,
            validators = ('isUserManageEmployees'),
            ),

    StringField(
            name='manager',
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Gestor"),
                description=_(u"Indique quem é o gestor dessa Unidade Organizacional."),
                usersOnly=True
                ),
            required=True,
    ),

    StringField(
            name='vice_manager',
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Gestor substituto "),
                description=_(u"Indique quem é o gestor substituto  dessa Unidade Organizacional."),
                usersOnly=True
                ),
            required=False,
    ),

    TextField(
            name='text',
            default_content_type = 'text/restructured',
            default_output_type = 'text/x-html-safe',
            widget=RichWidget(
                label=_(u"Anotações"),
                description=_(u"Insira aqui as anotações da estrutura."),
                rows="10",
            ),
            required=False,
    ),

    ReferenceField('image',
        multiValued=0,
        allowed_types=('Image'),
        label=_(u"Imagem "),
        relationship='Imagem',
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Imagem "),
            description='Será exibido na visualização desta estrutura. A imagem será redimensionada para um tamanho adequado.')
    ),

    #---------------------abas de permissão no Objeto---------------------------------
     LinesField(
            name="Groups_view",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Grupo de usuários para visualização"),
                description=_(u"Selecione os grupos que terão permissão de visualizar esta unidade organizacional."),
                groupsOnly=True,
                ),
            required=0,
            schemata = 'Permissões',
            ),

     LinesField(
            name="Groups_edit",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Grupo de usuários de gerencia o conteúdo"),
                description=_(u"Selecione os grupos que terão permissão de gerenciar o conteúdo desta unidade organizacional."),
                groupsOnly=True,
                ),
            required=0,
            schemata = 'Permissões',
            ),

     LinesField(
            name="Groups_admin",
            multiValued=1,
            widget = widget.UserAndGroupSelectionWidget(
                label=_(u"Grupo de usuários de administração"),
                description=_(u"Selecione os grupos que terão permissão de gerenciar totalmente esta unidade organizacional."),
                groupsOnly=True,
                ),
            required=0,
            schemata = 'Permissões',
            validators = ('isUserUpdate',),
            ),

    #---------------------abas de permissões no Objeto---------------------------------


))

finalizeATCTSchema(OrganizationalStructure_schema, folderish=True)
invisivel = {'view':'invisible','edit':'invisible',}
# Dates
L = ['effectiveDate','expirationDate','creation_date','modification_date']
# Categorization
L += ['subject','relatedItems','language']
# Ownership
L += ['creators','contributors','rights']
# Settings
L += ['allowDiscussion','excludeFromNav', 'nextPreviousEnabled']

for i in L:
    OrganizationalStructure_schema[i].widget.visible = invisivel

OrganizationalStructure_schema.changeSchemataForField('location', 'Informações')

class OrganizationalStructure(ATFolder):
    """ OrganizationalStructure """

    security = ClassSecurityInfo()
    implements(IOrganizationalStructure)
    portal_type = 'OrganizationalStructure'
    _at_rename_after_creation = True
    schema = OrganizationalStructure_schema

    def at_post_create_script(self):
        """Notify that the employee has been saved.
        """
        notify(OrgstructureModifiedEvent(self))

    def at_post_edit_script(self):
        """Notify that the employee has been saved.
        """
        notify(OrgstructureModifiedEvent(self))

    def voc_listGroups(self):
        terms = []
        if 'acl_users' in getSite().keys():
            groups = getSite().get('acl_users').getGroups()

            for group in groups:
                member_id = group.id
                member_name = group.getProperties().get('title','')
                terms.append((member_id, unicode(member_name)))

        return terms

    def voc_itens_menu(self):
        types = self.portal_types.listContentTypes()
        return types

    def getTipoUnidades(self):
        result = [('', 'Selecione um tipo de Unidade')]
        obj_control = getSite().get('control-panel-objects')
        tipounidade = obj_control.get('vindula_categories').getTipoUnidade()
        if tipounidade:
            tipounidade = tipounidade.replace('\r', '')
            tipounidade = tipounidade.split('\n')
            for modalidade in tipounidade:
               modalidade = modalidade.strip()
               result.append((modalidade, modalidade))
        return result

    def getImageIcone(self):
        image = self.getImage()

        if image:
            return image.absolute_url() +'/image_tile'
        else:
            return getSite().portal_url()+'/++resource++vindula.content/images/icon-org-default.png'
    
    def getImageSize(self, size='mini'):
        image = self.getImage()

        if image:
            return image.absolute_url() +'/image_' + size
        else:
            return ''

    def getSiglaOrTitle(self):
        return self.getSiglaunidade() or self.Title()

    def getSigla_and_Title(self):
        text = '%s - %s' %(self.getSiglaOrTitle(),
                                self.Title())
        return text


    def getContatoInfo(self):
        text = '%s <br/> %s <br/> %s' %(self.getEmail(),
                                        self.getPhone_number(),
                                        self.getPhone_alternative())
        return text

    def getGestorInfo(self):
        user_obj =  FuncDetails(username=unicode(self.getManager(),'utf-8'))
        text = "%s <br/> %s " %(user_obj.get('name',self.getManager()),
                                user_obj.get('position',''))

        return text

registerType(OrganizationalStructure, PROJECTNAME)
