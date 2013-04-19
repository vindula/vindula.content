# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface


from plone.app.layout.viewlets.content import ContentHistoryView
from vindula.content.models.content import ModelsContent

from vindula.myvindula.tools.utils import UtilMyvindula

from datetime import datetime


class MacroPropertiesView(grok.View, UtilMyvindula):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-propertis-content')


    def __init__(self,context,request):
        super(MacroPropertiesView,self).__init__(context,request)
        owner = context.getOwner()
        username = owner.getUserName()
        self.dadosUser = self.get_prefs_user(username)

        self.creator = self.dadosUser.get('name')
        self.creation_date = context.creation_date.strftime('%d/%m/%Y')
        self.responsible = self.dadosUser.get('email')


    def gethistory(self):
        context = self.context
        HistoryView = ContentHistoryView(context, context.REQUEST)

        content_history = HistoryView.fullHistory()
        L = []
        for history in content_history:
            tipo = history.get('type','')
            if tipo == 'workflow':
                date = history.get('time','').strftime('%d/%m/%Y')
            else:
                date = datetime.fromtimestamp(history.get('time','')).strftime('%d/%m/%Y')

            actor = self.get_prefs_user(history.get('actor',{}).get('username',''))

            L.append({'actor': actor.get('name',''),
                      # 'action':  history.get('transition_title',''),
                      # 'type': tipo,
                      'date':date,})

        return L

class MacroCommentsView(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-comments-content')


class MacroRelatedItems(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-relateditens-content')


class MacroKeywords(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-keywords-content')


class MacroBusiestViews(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-busiest-content')


    def list_files(self, portal_type):
        list_files = []

        query = {'portal_type': portal_type}

        result = ModelsContent().search_catalog_by_access(context=self.context,
                                                           **query)
        return result

class MacroComboStandard(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-comboStandard-content')


class MacroRating(grok.View):
    grok.context(Interface)
    grok.require('zope2.View')
    grok.name('macro-rating-content')
