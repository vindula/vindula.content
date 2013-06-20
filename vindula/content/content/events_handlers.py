# -*- coding: utf-8 -*-

from five import grok

from Products.Archetypes.interfaces import IBaseObject

from zope.app.container.interfaces import IObjectRemovedEvent
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent

from vindula.myvindula.models.plone_event import PloneEvent


def addEventPlone(context, tipo):
    uid = context.UID()
    portal_type = context.portal_type
    if not 'portal_factory' in context.getPhysicalPath():
        print '-'*30
        print uid
        print tipo
        print '-'*30
        PloneEvent().set_event(uid,portal_type)


#---------Criação de um objeto
@grok.subscribe(IBaseObject, IObjectCreatedEvent)
def EventAddObject(context, event):
    addEventPlone(context,'ADD')

#---------Edição de um objeto
@grok.subscribe(IBaseObject, IObjectModifiedEvent)
def EventEditObject(context, event):
    addEventPlone(context,'EDIT')

#---------mudanã WF de um objeto
@grok.subscribe(IBaseObject, IActionSucceededEvent)
def EventWfObject(context, event):
    addEventPlone(context,'WF')

#---------Exclução de um objeto
@grok.subscribe(IBaseObject, IObjectRemovedEvent)
def EventDeletedObject(context, event):
    addEventPlone(context,'DELETE')