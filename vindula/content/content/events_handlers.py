# -*- coding: utf-8 -*-

from five import grok
#Conteudo
from zope.lifecycleevent.interfaces import IObjectCreatedEvent, IObjectModifiedEvent

from vindula.myvindula.models.plone_event import PloneEvent
from vindula.content.content.interfaces import IVindulaNews, IVindulaPhotoAlbum, IVindulaPortlet


def addEventPlone(context):
    uid = context.UID()
    PloneEvent().set_event(uid)

#----------Vindula News
@grok.subscribe(IVindulaNews, IObjectCreatedEvent)
def EventAddVindulaNews(context, event):
    addEventPlone(context)

@grok.subscribe(IVindulaNews, IObjectModifiedEvent)
def EventEditVindulaNews(context, event):
    addEventPlone(context)

#-----------VindulaPhotoAlbum
@grok.subscribe(IVindulaPhotoAlbum, IObjectCreatedEvent)
def EventAddVindulaPhotoAlbum(context, event):
    addEventPlone(context)

@grok.subscribe(IVindulaPhotoAlbum, IObjectModifiedEvent)
def EventEditVindulaPhotoAlbum(context, event):
    addEventPlone(context)
    
#___________VindulaPortlet    
@grok.subscribe(IVindulaPortlet, IObjectCreatedEvent)
def EventAddVindulaPortlet(context, event):
    addEventPlone(context)

@grok.subscribe(IVindulaPortlet, IObjectModifiedEvent)
def EventEditVindulaPortlet(context, event):
    addEventPlone(context)
    
