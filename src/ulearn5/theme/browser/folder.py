from plone.app.contenttypes.browser.folder import FolderView


class MyFolderView(FolderView):

    def abrevia(self, obj, sumlenght):
        """ Retalla contingut de cadenes """
        text = getattr(obj, 'text', None)
        if text is not None:
            summary = text.output
            bb = ''

            if sumlenght < len(summary):
                bb = summary[:sumlenght]

                lastspace = bb.rfind(' ')
                cutter = lastspace
                precut = bb[0:cutter]

                if precut.count('<b>') > precut.count('</b>'):
                    cutter = summary.find('</b>', lastspace) + 4
                elif precut.count('<strong>') > precut.count('</strong>'):
                    cutter = summary.find('</strong>', lastspace) + 9
                bb = summary[0:cutter]

                if bb.count('<p') > precut.count('</p'):
                    bb += '...</p>'
                else:
                    bb = bb + '...'
            else:
                bb = summary

            return bb
        else:
            return ""
