## Script (Python) "at_download"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Download a file keeping the original uploaded filename
##

if getattr(context, 'activ_download', False):
    can_download = getattr(context, 'activ_download')
else:
    can_download = True

if can_download:
    if traverse_subpath:
        field = context.getWrappedField(traverse_subpath[0])
    else:
        field = context.getPrimaryField()


    if not hasattr(field, 'download'):
        from zExceptions import NotFound
        raise NotFound
    return field.download(context)

else:
    context.plone_utils.addPortalMessage(('Este arquivo não está autorizado para download.'), 'error')
    context.REQUEST.RESPONSE.redirect(context.aq_parent.absolute_url())
