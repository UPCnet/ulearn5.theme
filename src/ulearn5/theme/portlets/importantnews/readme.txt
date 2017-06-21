
1-  Requiere que esté la class viewlet gwImportantNews, y su viewlets_template important.pt

  class gwImportantNews(viewletBase):
      grok.name('genweb.important')
      grok.context(INewsItem)
      grok.template('important')
      grok.viewletmanager(IAboveContentTitle)
      grok.require('cmf.ModifyPortalContent')
      grok.layer(IUlearnUdemoLayer)

      def permisos_important(self):
          # TODO: Comprovar que l'usuari tingui permisos per a marcar com a important
          return not IImportant(self.context).is_important and checkPermission("plone.app.controlpanel.Overview", self.portal())

      def permisos_notimportant(self):
          # TODO: Comprovar que l'usuari tingui permisos per a marcar com a notimportant
          return IImportant(self.context).is_important and checkPermission("plone.app.controlpanel.Overview", self.portal())

      def isNewImportant(self):
          context = aq_inner(self.context)
          is_important = IImportant(context).is_important
          return is_important

2 - Si se quiere la vista para visualizar el listado total de notícias maquetado
    para notícias, habrá que añadir la vista summary_view_news
