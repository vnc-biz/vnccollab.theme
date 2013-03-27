from zope.interface import implements
from zope.component import adapts
from zope.component import queryAdapter

from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

from plone.portlets.interfaces import IPortletContext
from plone.portlets.interfaces import IPlacelessPortletManager
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.constants import GROUP_CATEGORY

from collective.braveportletsmanager.util import logException
from collective.braveportletsmanager.retriever import PlacelessPortletRetriever


class CloudPortalDashboardPortletRetriever(PlacelessPortletRetriever):
    """A placeless portlet retriever.

    Here we display only group portlets.
    """

    implements(IPortletRetriever)
    adapts(IPloneSiteRoot, IPlacelessPortletManager)

    def __init__(self, context, storage):
        self.context = context
        self.storage = storage

    def getPortlets(self):
        if IPortletContext.providedBy(self.context):
            pcontext = self.context
        else:
            pcontext = queryAdapter(self.context, IPortletContext)

        if pcontext is None:
            return []

        assignments = []
        for category, key in pcontext.globalPortletCategories(True):
            # skip all portlets that are not within Group category
            if category != GROUP_CATEGORY:
                continue

            mapping = self.storage.get(category, None)
            if mapping is not None:
                for assignment in mapping.get(key, {}).values():
                    try:
                        settings = IPortletAssignmentSettings(assignment)
                    except Exception:
                        logException(u'Error during retrieving assignment '
                            'settings. Context: "%s", Category: "%s", Key: '
                            '"%s", Assignment Class: "%s", Assignment ID: "%s"'
                            % ('/'.join(self.context.getPhysicalPath()),
                            category, key, str(assignment.__class__),
                            assignment.__name__), context=self.context)
                        continue

                    if not settings.get('visible', True):
                        continue
                    assignments.append({'category': category,
                                        'key': key,
                                        'name': assignment.__name__,
                                        'assignment': assignment
                                        })

        return assignments
