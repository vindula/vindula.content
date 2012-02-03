# -*- coding: utf-8 -*-
try: # New CMF
    from Products.CMFCore.permissions import setDefaultRoles 
except ImportError: # Old CMF
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles


PROJECTNAME = 'vindula.content'

try:
    from Products.CMFPlone.migrations import v2_1
except ImportError:
    HAS_PLONE21 = False
else:
    HAS_PLONE21 = True


# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
#ADD_CONTENT_PERMISSIONS = {
#    'VindulaNews': 'vindula.content: Add VindulaNews',
#    'OrganizationalStructure': 'vindula.content: Add OrganizationalStructure',
#    'Unit': 'vindula.content: Add Unit',}


product_globals = globals()

