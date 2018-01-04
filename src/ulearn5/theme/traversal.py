from plone.resource.traversal import ResourceTraverser


class UlearnTraverser(ResourceTraverser):
    """The ulearn static resource traverser.

    Allows traversal to /++ulearn++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """

    name = 'ulearn'


class LegacyTraverser(ResourceTraverser):
    """The web legacy resource traverser.

    Allows traversal to /++legacy++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """

    name = 'legacy'


class AppTraverser(ResourceTraverser):
    """The web app resource traverser.

    Allows traversal to /++app++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """

    name = 'app'


class ComponentsTraverser(ResourceTraverser):
    """The web components resource traverser.

    Allows traversal to /++components++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """

    name = 'components'


class DistTraverser(ResourceTraverser):
    """The web dist resource traverser.

    Allows traversal to /++dist++<name> using ``plone.resource`` to fetch
    things stored either on the filesystem or in the ZODB.
    """

    name = 'dist'
