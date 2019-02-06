# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.folder import FolderView

from base5.core.utils import abrevia


class MyFolderView(FolderView):

    def abrevia(self, obj, sumlenght):
        return abrevia(obj, sumlenght)
