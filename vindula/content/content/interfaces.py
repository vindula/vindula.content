# -*- coding: utf-8 -*-
from zope.interface import Interface, Attribute

class IVindulaNews(Interface):
    """ Interface for VindulaNews content type """

class IVindulaFolder(Interface):
    """ Interface for VindulaFolder content type """

class IOrganizationalStructure(Interface):
    """ Interface for OrganizationalStructure content type """
    
class IInternalLink(Interface):
    """ Interface for IInternalLink content type """  
    
class IUnit(Interface):
   """ Interface for Unit content type """   

class IVindulaPortlet(Interface):
   """ Interface for VindulaPortlet content type """  
   
class IOrgstructureModifiedEvent(Interface):
    """An event fired when an Orgstructure object is saved.
    """
    context = Attribute("The content object that was saved.")   
    
class IVindulaPhotoAlbum(Interface):
    """An event fired when an Vindula Photo Album object is saved.
    """
    
    