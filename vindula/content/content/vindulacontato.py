# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from zope.interface import Interface
from vindula.content.content.interfaces import IVindulaContato
from plone.contentrules.engine.interfaces import IRuleAssignable
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *

from Products.ATContentTypes.content.base import ATCTContent, ATContentTypeSchema
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column


from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

from Products.CMFCore.utils import getToolByName
from vindula.myvindula.tools.utils import UtilMyvindula

VindulaContato_schema = ATContentTypeSchema.copy() + Schema((
                                                         
    # StringField(
    #     name='nome',
    #     searchable = True,
    #     widget = StringWidget(
    #         label = 'Nome',
    #         description='Digite o nome do contato.',
    #     ),
    # ),
    
    StringField(
        name = 'razao_social',
        widget=StringWidget(
            label='Razão Social',
            description="Digite a razão social do contato.",
        ),
        searchable = True,
    ),
    
    StringField(
        name = 'cpf_cnpf',
        widget=StringWidget(
            label= 'CPF/CNPJ',
            description= 'Digite o CPF ou CNPF do contato.',
        ),
        searchable = True,
    ),

    StringField(
        name = 'email',
        widget=StringWidget(
            label= 'E-mail',
            description= 'Digite o e-mail do contato.',
        ),
        searchable = True,
    ),

    DataGridField('telefones',
                searchable=True,
                columns=('title','number'),
                allow_delete = True,
                allow_insert = True,
                allow_reorder = True,
                widget = DataGridWidget(label="Listagem de Telefones",
                                        label_msgid='vindula_tile_label_telefones',
                                        description="Adcione os telefones do contato.",
                                        description_msgid='vindula_controlpanel_help_telefones',
                                        columns= {
                                            "title" : Column(_(u"Titulo")),
                                            "number" : Column(_(u"Números Telefonicos")),
                                        }),
                ),


    StringField(
        name = 'endereco',
        widget=StringWidget(
            label= 'Endereço',
            description= 'Digite o endereço do contato.',
        ),
        searchable = True,
    ),

    StringField(
        name = 'cidade',
        widget=StringWidget(
            label= 'Cidade',
            description= 'Digite a cidade do contato.',
        ),
        searchable = True,
    ),

    StringField(
        name = 'estado',
        widget=StringWidget(
            label= 'Estado',
            description= 'Digite o estado do contato.',
        ),
        searchable = True,
    ),
  

))

VindulaContato_schema['title'].widget.label = 'Nome'
VindulaContato_schema['title'].widget.description = 'Digite o nome do contato'
finalizeATCTSchema(VindulaContato_schema, folderish=False)


class VindulaContato(ATCTContent):
    """ Reserve Content for VindulaContato"""
    security = ClassSecurityInfo()    
    
    implements(IVindulaContato, IRuleAssignable)    
    portal_type = 'VindulaContato'
    _at_rename_after_creation = True
    schema = VindulaContato_schema
    
    def get(self,atributo):
        try:
            #Retorna o valor do metodo passado
            return getattr(self, atributo)()
        except AttributeError:
            return ''
        except TypeError:
            #Retorna o valor do atributo passado
            return getattr(self, atributo)

    def get_lista_telefones(self):
        telefones = self.getTelefones()
        texto = ''
        for telefone in telefones:
            texto += '%s: %s \n' %(telefone.get('title',''),
                                   telefone.get('number',''))
        return texto


    def name(self):
        return self.Title()


registerType(VindulaContato, PROJECTNAME) 


# View
class VindulaContatoListView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('myvindulalistcontatos')
    
    def load_list(self):
        context = self.context
        
        path = context.portal_url.getPortalObject()
        catalog = getToolByName(context, 'portal_catalog')

        form = self.request.form
        result = None

        if 'SearchSubmit' in form.keys():
            title = form.get('title','').strip()
            campos = eval(form.get('campos',"[{'name':title}]"))

            check_form = [i for i in campos if i.values() != [u'']]
            query = {'portal_type': ('VindulaContato',),
                     'path': {'query':'/'.join(path.getPhysicalPath()),'depth':99},
                     'sort_on':'sortable_title', 'sort_order':'ascending'}

            SearchableText = []
            for item in check_form:

                if item.has_key('name'):
                    query['Title'] = item['name']+'*'

                else:
                    SearchableText.append(item.values()[0]+'*')

            if len(SearchableText):
                query['SearchableText'] = SearchableText

            busca = catalog(**query)
            result = [i.getObject() for i in busca]

        return result


    def update(self):
        open_for_anonymousUser =  self.context.restrictedTraverse('myvindula-conf-userpanel').check_myvindulaprivate_isanonymous();
        if open_for_anonymousUser:
            self.request.response.redirect(self.context.absolute_url() + '/login')
