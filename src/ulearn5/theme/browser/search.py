# -*- coding: utf-8 -*-
from Products.CMFPlone.browser.search import Search as OriginalSearch


class Search(OriginalSearch):

    def get_subject_filters(self):
        if 'Subject' in self.request.form:
            return self.request.form['Subject']
        return False

    def get_all_subjects(self):
        subjects = self.context.portal_catalog.uniqueValuesFor('Subject')
        return sorted(subjects, key=lambda x: x.lower())
