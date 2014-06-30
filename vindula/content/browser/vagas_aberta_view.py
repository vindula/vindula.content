# coding=utf-8
from five import grok
from zope.interface import Interface

grok.templatedir('macros_templates')


class VagasAbertasView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('view_vagas_abertas')


    def get_content(self):
    	aq_parent = self.context.aq_parent
    	if 'vagas-em-aberto' in aq_parent.keys():
    		return aq_parent['vagas-em-aberto']
    	return None

    def list_itens(self):
    	context = self.get_content()
    	if context:
    		return context.getDadosContent()
    	return []


    def getFields(self):
    	from vindula.contentcore.models.fields import ModelsFormFields
    	context = self.get_content()
        id_form = int(context.forms_id)

        return ModelsFormFields().get_Fields_ByIdForm(id_form)
