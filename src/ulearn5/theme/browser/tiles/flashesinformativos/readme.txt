# 1-  Crear tipo de contenido Flash_informativo

# 2- Crear carpeta en el initialize

gestion = portal['gestion']
if not getattr(gestion, 'flashes_informativos', False):
    flashes_informativos = self.newPrivateFolder(gestion, 'flashes_informativos', u'Flashes informativos')
    flashes_informativos.exclude_from_nav = False
    flashes_informativos.reindexObject()

    behavior = ISelectableConstrainTypes(flashes_informativos)
    behavior.setConstrainTypesMode(1)
    behavior.setLocallyAllowedTypes(('Collection', 'Flash_informativo',))
    behavior.setImmediatelyAddableTypes(('Collection', 'Flash_informativo',))

    flashes_informativos_collection = self.newCollection(flashes_informativos,
                                                         'flashes_informativos',
                                                         u'Flashes informativos',
                                                         query=[{u'i': u'portal_type',
                                                                 u'o': u'plone.app.querystring.operation.selection.is',
                                                                 u'v': [u'Flash_informativo']}, ])
    flashes_informativos_collection.setSort_on('modified')
    flashes_informativos_collection.setSort_reversed(True)
    flashes_informativos_collection.setLayout('summary_view')
    flashes_informativos_collection.reindexObject()
    flashes_informativos.setDefaultPage('flashes_informativos')
