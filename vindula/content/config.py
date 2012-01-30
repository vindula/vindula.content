# -*- coding: utf-8 -*-
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'vindula.content'

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'VindulaNews': 'vindula.content: Add VindulaNews',
    'OrganizationalStructure': 'vindula.content: Add OrganizationalStructure',
    'Unit': 'vindula.content: Add Unit',
    
}

setDefaultRoles('vindula.content: Add VindulaNews', ('Manager','Owner'))
setDefaultRoles('vindula.content: Add OrganizationalStructure', ('Manager','Owner'))
setDefaultRoles('vindula.content: Add Unit', ('Manager','Owner'))


product_globals = globals()