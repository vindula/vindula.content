# -*- coding: utf-8 -*-
from thread import allocate_lock

import transaction
from AccessControl import Unauthorized
from Products.statusmessages.interfaces import IStatusMessage
from ZODB.POSException import ConflictError
from collective.quickupload import logger, siteMessageFactory as _
from collective.quickupload.browser.uploadcapable import MissingExtension, get_id_from_filename
from collective.quickupload.interfaces import IQuickUploadFileSetter
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


upload_lock = allocate_lock()


def normalize_id_to_file_name(filename, context):
    charset = context.getCharset()
    id = filename.decode(charset).rsplit('.', 1)
    if len(id) != 2:
        raise MissingExtension('It seems like the file extension is missing.')
    normalizer = component.getUtility(IIDNormalizer)
    newid = '.'.join((normalizer.normalize(id[0]), id[1]))
    newid = newid.replace('_','-').replace(' ','-').lower()
    return newid

def create_or_set_folder_path(path, context):
    """
    Cria pastas recusivamente seguindo o caminho passado.

    Args:
        path (list): Do caminho onde a pasta será criada
        context (plone context): Contexto de onde irá criar a pasta

    Returns:
        Retorna o contexto da ultima pasta criada 
    """

    if path:
        #Remove espacos em branco da lista
        path = [i for i in path if i]
        if path:
            p = path[0]
            if context.get(p, False):
                folder = context[p]
                if len(path) <= 1:
                    return folder
            else:
                normalizer = component.getUtility(IIDNormalizer)
                id = normalizer.normalize(p)
                folder = context.invokeFactory(type_name="VindulaFolder", id=id, title=p, description='')
                folder = context[folder]
                folder.processForm()
                folder.reindexObject()

            return create_or_set_folder_path(path[1:], folder)
    else:
        return context

def vindula_file_factory(context, filename, title, description, content_type, data, portal_type):
        error = ''
        result = {}
        result['success'] = None
        newid = get_id_from_filename(filename, context)
        # consolidation because it's different upon Plone versions
        if not title :
            # try to split filenames because we don't want
            # big titles without spaces
            title = filename.rsplit('.', 1)[0].replace('_',' ').replace('-',' ')

        if newid in context:
            # only here for flashupload method since a check_id is done
            # in standard uploader - see also XXX in quick_upload.py
            raise NameError, 'Object id %s already exists' %newid
        else :
            upload_lock.acquire()
            try:
                try:
                    context.invokeFactory(type_name=portal_type, id=newid,
                                          title=title, description=description)
                except Unauthorized :
                    error = u'serverErrorNoPermission'
                except ConflictError :
                    # rare with xhr upload / happens sometimes with flashupload
                    error = u'serverErrorZODBConflict'
                except ValueError:
                    error = u'serverErrorDisallowedType'
                except Exception, e:
                    error = u'serverError'
                    logger.exception(e)

                if error:
                    if error == u'serverError':
                        logger.info("An error happens with setId from filename, "
                                    "the file has been created with a bad id, "
                                    "can't find %s", newid)
                else:
                    obj = getattr(context, newid)
                    if obj:
                        error = IQuickUploadFileSetter(obj).set(data, filename, content_type)
                        obj.processForm()

                #@TODO : rollback if there has been an error
                transaction.commit()
            finally:
                upload_lock.release()

        result['error'] = error
        if not error :
            result['success'] = obj

        return result


def vindula_file_updater(obj, filename, title, description, content_type, data):
        error = ''
        result = {}
        result['success'] = None

        # consolidation because it's different upon Plone versions
        if title:
            obj.setTitle(title)

        if description:
            obj.setDescription(description)

        error = IQuickUploadFileSetter(obj).set(data, filename, content_type)
        notify(ObjectModifiedEvent(obj))
        obj.reindexObject()

        result['error'] = error
        if not error :
            result['success'] = obj
            IStatusMessage(obj.REQUEST).addStatusMessage(_('msg_file_replaced',
                        default=u"${filename} file has been replaced",
                        mapping={'filename': filename}), type)

        return result
