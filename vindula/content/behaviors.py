# coding=utf-8
"""Behaviours to assign tags (to ideas).

Includes a form field and a behaviour adapter that stores the data in the
standard Subject field.
"""

from rwproperty import getproperty, setproperty

from zope.interface import implements, alsoProvides
from zope.component import adapts

from plone.directives import form
from zope import schema
from Products.CMFCore.interfaces import IDublinCore

from vindula.content import MessageFactory as _

class ICommentEnable(form.Schema):
    """Add ICommentEnable to content
    """
    
    form.fieldset('settings', label=u"Settings",
                  fields=['activ_comment'])

    activ_comment = schema.Bool(
                title=_(u'label_activ_comment', default=u'Ativar Comentario'),
                description=_(u'help_activ_comment', default=u'Se selecionado, Ativa a opção de comentarios deste conteudo'),
                default=True
                )

alsoProvides(ICommentEnable, form.IFormFieldProvider)

class CommentEnable(object):
    """Store tags in the Dublin Core metadata Subject field. This makes
    tags easy to search for.
    """
    implements(ICommentEnable)
    adapts(IDublinCore)

    def __init__(self, context):
        self.context = context
    
    @getproperty
    def activ_comment(self):
        return self.context.activ_comment

    @setproperty
    def activ_comment(self, value):
        if value is None:
            value = False
        self.context.activ_comment = value