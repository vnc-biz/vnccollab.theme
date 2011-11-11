from zope.viewlet.interfaces import IViewletManager
from plone.theme.interfaces import IDefaultPloneLayer


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IVNCCollabHtmlHead(IViewletManager):
    """A viewlet manager that sits right after portal tabs viewlet"""
