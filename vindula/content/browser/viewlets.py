# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from vindula.content.content.interfaces import IVindulaNews
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from Products.CMFCore.utils import getToolByName
from zope.app.component.hooks import getSite

from Products.CMFPlone import utils
from Products.CMFPlone.browser.navigation import get_view_url
from plone.app.layout.navigation.root import getNavigationRoot

# grok.context(Interface)

class PrintPageViewlet(grok.Viewlet):
    grok.name('vindula.content.printpage')
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContentTitle)
    grok.context(IVindulaNews)