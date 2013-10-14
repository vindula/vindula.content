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
    

class IVindulaEdital(Interface):
    """ Interface for VindulaEdital content type """


class IVindulaContato(Interface):
    """ Interface for VindulaContato content type """


class IVindulaFile(Interface):
    """ Interface for VindulaFile content type """


class IVindulaVideo(Interface):
    """ Interface for VindulaFile content type """
    
class IVindulaTeam(Interface):
    """ Interface for VindulaTeam content type """


class IVindulaRevista(Interface):
    """ Interface for VindulaRevista content type """


class IVindulaEmployee(Interface):
    """ Interface for VindulaTeam content type """
