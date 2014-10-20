# -*- coding: utf-8 -*-
from five import grok
from plone.app.layout.viewlets.interfaces import IBelowContentTitle

from vindula.content.content.interfaces import IVindulaNews


# grok.context(Interface)

class PrintPageViewlet(grok.Viewlet):
    grok.name('vindula.content.printpage')
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContentTitle)
    grok.context(IVindulaNews)