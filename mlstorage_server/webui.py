import os

from aiohttp import web

__all__ = ['WebUI']


class WebUI(object):
    """
    The aiohttp server handler for web UI.
    """

    def __init__(self, mldb, store_mgr):
        """
        Construct a new :class:`ApiV1`.

        Args:
            mldb (MLDB): The database instance.
            store_mgr (FileStoreManager): The file storage manager.
        """
        self._assets_dir = os.path.join(
            os.path.split(os.path.abspath(__file__))[0],
            'assets'
        )
        self._mldb = mldb
        self._store_mgr = store_mgr

    @property
    def assets_dir(self):
        """Get the assets directory."""
        return self._assets_dir

    @property
    def mldb(self):
        return self._mldb

    @property
    def store_mgr(self):
        return self._store_mgr

    def bind(self, app):
        """
        Bind this handler to the given `app`.

        Args:
            app (web.Application): The web application object.
        """
        def url(fmt):
            return '' + fmt.format(
                id='{id:[A-Za-z0-9]{24}}',
                path='{path:.*}'
            )
        app.add_routes([
            web.get(url('/'), self.handle_index),
            web.get(url('/{id}'), self.handle_add_slash),
            web.get(url('/{id}/'), self.handle_index),
            web.get(url('/{id}/console'), self.handle_index),
            web.get(url('/{id}/browse'), self.handle_add_slash),
            web.get(url('/{id}/browse/'), self.handle_index),
            web.get(url('/{id}/browse/{path}'), self.handle_index),
        ])
        app.router.add_static(
            '/static', os.path.join(self.assets_dir, 'static'))

    async def handle_add_slash(self, request):
        raise web.HTTPMovedPermanently(
            str(request.rel_url.with_path(request.rel_url.path + '/')))

    async def handle_index(self, request):
        return web.FileResponse(os.path.join(self.assets_dir, 'index.html'))
