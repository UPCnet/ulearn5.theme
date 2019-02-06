# -*- coding: utf-8 -*-
from plone.app.contenttypes.browser.collection import CollectionView

from base5.core.utils import abrevia


class MyCollectionView(CollectionView):

    def abrevia(self, summary, sumlenght):
        return abrevia(summary, sumlenght)
