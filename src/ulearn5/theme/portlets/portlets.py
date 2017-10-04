from zope.security import checkPermission
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.portlets.portlets.navigation import Renderer as NavigationRenderer
from ulearn5.core.content.community import ICommunity
from base5.core.browser.interfaces import IHomePage


# Not used
# class ulearnCommunitiesNavigation(NavigationRenderer):
#     """ The standard navigation portlet override 'old style'
#         as it doesn't allow to do it jbot way...
#     """
#     _template = ViewPageTemplateFile('templates/navigation.pt')
#     recurse = ViewPageTemplateFile('templates/navigation_recurse.pt')

#     def showCreateCommunity(self):
#         if IHomePage.providedBy(self.context):
#             return True

#     def showEditCommunity(self):
#         if not IPloneSiteRoot.providedBy(self.context) and \
#            ICommunity.providedBy(self.context) and \
#            checkPermission('cmf.RequestReview', self.context):
#             return True
