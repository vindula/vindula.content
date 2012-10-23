# coding=utf-8
from five import grok
from vindula.content import MessageFactory as _

from zope.app.component.hooks import getSite 
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from plone.app.discussion.interfaces import IConversation
from vindula.content.content.interfaces import IVindulaEdital

from AccessControl import ClassSecurityInfo
from zope.interface import implements
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.newsitem import ATNewsItemSchema
from Products.ATContentTypes.content.newsitem import ATNewsItem
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from vindula.content.config import *

from vindula.controlpanel.browser.at.widget import VindulaReferenceSelectionWidget

from DateTime.DateTime import DateTime

VindulaEdital_schema = ATNewsItemSchema.copy() + Schema((
                                                         
    StringField(
        name='numeroEdital',
        searchable = True,
        widget = StringWidget(
            label = 'Número',
            description='Escolha um número para este edital.',
        ),
    ),
    
    StringField(
        name = 'orgao',
        widget=SelectionWidget(
            label='Órgão',
            description="Selecione o órgão relacionado a este edital.",
            format = 'select',
        ),
        vocabulary = 'getOrgaos',
        searchable = True,
    ),
    
    StringField(
        name = 'modalidade',
        widget=SelectionWidget(
            label= 'Modalidade',
            description= 'Selecione a modalidade relacionada a este edital.',
            format = 'select',
        ),
        vocabulary = 'getModalidades',
        searchable = True,
    ),

    DateTimeField(
        name='dataPublicacao',
        searchable = True,
        required = True,
        default_method = 'getDefaultTime',
        widget = CalendarWidget(
            label = 'Data de publicação',
            description='Selecione a data de publicação do edital.',
            format = '%d/%m/%Y',
            show_hm = 0,
        ),
    ),
    
    ReferenceField(
        name='archiveRelated',
        multiValued=True,
        allowed_types=('File'),
        relationship='archiveRelated',
        widget=VindulaReferenceSelectionWidget(
            label=_(u"Arquivo relacionado"),
            description=_(u'Selecione um arquivo relacionado a esse edital.'),
        ),
    ),

    BooleanField(
        name='activeShare',
        default=True,
        widget=BooleanWidget(
            label="Ativar Compartilhamento",
            description='Se selecionado, ativa a opção de compartilhamento entre redes sociais.',
        ),
    ),                                             

))
invisivel = {'view':'invisible','edit':'invisible',}
VindulaEdital_schema['description'].widget.label = 'Descrição'
VindulaEdital_schema['image'].widget.visible = invisivel
VindulaEdital_schema['imageCaption'].widget.visible = invisivel

finalizeATCTSchema(VindulaEdital_schema, folderish=False)
VindulaEdital_schema.moveField('numeroEdital', before='text')

class VindulaEdital(ATNewsItem):
    """ Reserve Content for VindulaEdital"""
    security = ClassSecurityInfo()    
    
    implements(IVindulaEdital)    
    portal_type = 'VindulaEdital'
    _at_rename_after_creation = True
    schema = VindulaEdital_schema
    
    # function to return the current date and time
    def getDefaultTime(self):  
        return DateTime()
    
    def getOrgaos(self):
        result = [('', 'Selecione um orgão')]
        obj_control = getSite().get('control-panel-objects')
        orgaos = obj_control.get('vindula_categories').orgaoEdital
        if orgaos:
            orgaos = orgaos.split('\n')
            for orgao in orgaos:
               result.append((orgao, orgao)) 
        return result
    
    def getModalidades(self):
        result = [('', 'Selecione uma modalidade')]
        obj_control = getSite().get('control-panel-objects')
        modalidades = obj_control.get('vindula_categories').modalidadeEdital
        if modalidades:
            modalidades = modalidades.split('\n')
            for modalidade in modalidades:
               result.append((modalidade, modalidade)) 
        return result

registerType(VindulaEdital, PROJECTNAME) 


# View
class VindulaEditalView(grok.View):
    grok.context(IVindulaEdital)
    grok.require('zope2.View')
    grok.name('view')
    
    def check_share(self):
        panel = self.context.restrictedTraverse('@@myvindula-conf-userpanel')
        if panel.check_share():
            return  self.context.getActiveShare()
        else:
            return False 
        
    def getRelated(self):
        form = self.request.form
        query ={}
        query['meta_type'] = 'VindulaEdital'
        query['review_state'] = 'published'
        
        if form.get('submitted'):
            orgao = form.get('orgao', None)
            modalidade = form.get('modalidade', None)
            n_edital = form.get('nedital', None)
        else:
            orgao = self.context.getOrgao()
            modalidade = self.context.getModalidade()
            n_edital = self.context.getNumeroEdital()
        
        itens = self.context.aq_parent.getFolderContents(query)
        result = []
        for item in itens:
            item = item.getObject()
            if item.id == self.context.id:
                continue
            if orgao and modalidade and n_edital:
                if item.getModalidade() == modalidade and item.getOrgao() == orgao and item.getNumeroEdital() == n_edital:
                    result.append(item)
            elif orgao and modalidade: 
                if item.getModalidade() == modalidade and item.getOrgao() == orgao:
                        result.append(item)
            elif orgao and n_edital: 
                if item.getOrgao() == orgao and item.getNumeroEdital() == n_edital:
                        result.append(item)
            elif modalidade and n_edital:
                if item.getModalidade() == modalidade and item.getNumeroEdital() == n_edital:
                        result.append(item)
            else:
                if item.getModalidade() == modalidade or item.getOrgao() == orgao or item.getNumeroEdital() == n_edital:
                    result.append(item)
        return result
        
        
        
        
        
        


#class ShareView(grok.View):
#    grok.context(Interface)
#    grok.require('zope2.View') 
#    grok.name('vindula-content-share')