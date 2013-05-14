# -*- coding: utf-8 -*-

from five import grok

from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces import IObjectEditedEvent

from Products.CMFCore.interfaces import IActionSucceededEvent

#Conteudo
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent

from vindula.myvindula.models.plone_event import PloneEvent
# from vindula.content.content.interfaces import IVindulaNews, IVindulaPhotoAlbum, IVindulaPortlet, IOrganizationalStructure


def addEventPlone(context):
    uid = context.UID()
    portal_type = context.portal_type
    PloneEvent().set_event(uid,portal_type)


#---------Criação de um objeto
@grok.subscribe(IBaseObject, IObjectCreatedEvent)
def EventAddObject(context, event):
     addEventPlone(context)

#---------Criação de um objeto
@grok.subscribe(IBaseObject, IObjectModifiedEvent)
def EventEditObject(context, event):
    addEventPlone(context)

@grok.subscribe(IBaseObject, IActionSucceededEvent)
def EventWfObject(context,event):
    addEventPlone(context)


# #----------Vindula News
# @grok.subscribe(IVindulaNews, IObjectCreatedEvent)
# def EventAddVindulaNews(context, event):
#     addEventPlone(context)

# @grok.subscribe(IVindulaNews, IObjectModifiedEvent)
# def EventEditVindulaNews(context, event):
#     addEventPlone(context)

# #-----------VindulaPhotoAlbum
# @grok.subscribe(IVindulaPhotoAlbum, IObjectCreatedEvent)
# def EventAddVindulaPhotoAlbum(context, event):
#     addEventPlone(context)

# @grok.subscribe(IVindulaPhotoAlbum, IObjectModifiedEvent)
# def EventEditVindulaPhotoAlbum(context, event):
#     addEventPlone(context)

# #___________VindulaPortlet
# @grok.subscribe(IVindulaPortlet, IObjectCreatedEvent)
# def EventAddVindulaPortlet(context, event):
#     addEventPlone(context)

# @grok.subscribe(IVindulaPortlet, IObjectModifiedEvent)
# def EventEditVindulaPortlet(context, event):
#     addEventPlone(context)

# #___________OrganizationalStructure
# @grok.subscribe(IOrganizationalStructure, IObjectCreatedEvent)
# def EventAddOrganizationalStructure(context, event):
#     addEventPlone(context)

# @grok.subscribe(IOrganizationalStructure, IObjectModifiedEvent)
# def EventEditOrganizationalStructure(context, event):
#     addEventPlone(context)

