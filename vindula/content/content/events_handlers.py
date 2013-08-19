# -*- coding: utf-8 -*-

from five import grok
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseObject

from zope.app.container.interfaces import IObjectRemovedEvent
from Products.CMFCore.interfaces import IActionSucceededEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent
from zope.app.component.hooks import getSite

from vindula.myvindula.models.plone_event import PloneEvent


def addEventPlone(context, tipo):
    try:
        portal_membership = getToolByName(context, "portal_membership")
    except AttributeError:
        portal_membership = getToolByName(getSite(), "portal_membership")

    uid = context.UID()
    portal_type = context.portal_type

    try:actor = portal_membership.getAuthenticatedMember().getUserName()
    except:actor = 'administrador'

    if not 'portal_factory' in context.getPhysicalPath():
        print '-'*30
        print uid
        print tipo
        print actor
        print '-'*30
        PloneEvent().set_event(uid,portal_type,actor)


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