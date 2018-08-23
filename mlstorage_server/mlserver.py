import asyncio
import logging
import os

import click
from aiohttp import web
from motor.motor_asyncio import AsyncIOMotorClient

from mlstorage_server.api_v1 import ApiV1
from mlstorage_server.filestore import FileStoreManager
from mlstorage_server.mldb import MLDB
from mlstorage_server.webui import WebUI

__all__ = ['make_app', 'mlserver']


try:
    from gunicorn.app.base import BaseApplication
except ImportError:
    BaseApplication = None


if BaseApplication:
    class GUnicornWrapper(BaseApplication):
        def __init__(self, app_factory, options=None):
            self.options = options or {}
            self.app_factory = app_factory
            super(GUnicornWrapper, self).__init__()

        def load_config(self):
            cfg = dict([
                (key, value)
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            ])
            for key, value in cfg.items():
                self.cfg.set(key.lower(), value)
            self.cfg.set('worker_class', 'aiohttp.worker.GunicornWebWorker')

        def load(self):
            return self.app_factory()
else:
    GUnicornWrapper = None


def make_app(storage_root=None, mongo=None, db=None, collection=None,
             debug=False):
    if storage_root is None:
        storage_root = os.environ.get('MLSTORAGE_EXPERIMENT_ROOT')
    if mongo is None:
        mongo = os.environ.get('MLSTORAGE_MONGO_CONN')
    if db is None:
        db = os.environ.get('MLSTORAGE_MONGO_DB')
    if collection is None:
        collection = os.environ.get('MLSTORAGE_MONGO_COLL')
    if storage_root is None or mongo is None or db is None or \
            collection is None:
        raise ValueError('One or more of the environmental variables'
                         ' are not specified: '
                         '"MLSTORAGE_EXPERIMENT_ROOT", "MLSTORAGE_MONGO_CONN",'
                         '"MLSTORAGE_MONGO_DB" and "MLSTORAGE_MONGO_COLL".')

    logging.basicConfig(
        level='DEBUG' if debug else 'INFO',
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )
    logging.info('MongoDB connection: %s', mongo)
    logging.info('MongoDB database: %s', db)
    logging.info('MongoDB collection: %s', collection)
    logging.info('Experiment root: %s', storage_root)

    loop = asyncio.get_event_loop()
    client = AsyncIOMotorClient(mongo)
    mldb = MLDB(client[db][collection])
    store_mgr = FileStoreManager(storage_root, loop)

    app = web.Application()
    for handler_class in [ApiV1, WebUI]:
        handler_class(mldb, store_mgr).bind(app)

    return app


@click.command()
@click.option('-h', '--host', help='Specify the interface to bind.',
              required=False, default='0.0.0.0')
@click.option('-p', '--port', type=click.INT, help='Specify port to bind.',
              required=False, default=8080)
@click.option('-w', '--workers', default=None, type=click.INT,
              help='Number of worker processes.')
@click.option('-R', '--storage-root', required=True,
              help='Experiment storage root.  If not specified, will use '
                   '``os.environ["MLSTORAGE_EXPERIMENT_ROOT"]``.',
              default=os.environ.get('MLSTORAGE_EXPERIMENT_ROOT') or None)
@click.option('-M', '--mongo', required=True,
              help='MongoDB connection str.  If not specified, will use '
                   '``os.environ["MLSTORAGE_MONGO_CONN"]``.',
              default=os.environ.get('MLSTORAGE_MONGO_CONN') or None)
@click.option('-D', '--db', required=True,
              help='MongoDB database name.  If not specified, will use '
                   '``os.environ["MLSTORAGE_MONGO_DB"]``.',
              default=os.environ.get('MLSTORAGE_MONGO_DB') or None)
@click.option('-C', '--collection', required=True,
              help='MongoDB collection name.  If not specified, will use '
                   '``os.environ["MLSTORAGE_MONGO_COLL"]``.',
              default=os.environ.get('MLSTORAGE_MONGO_COLL') or None)
@click.option('--debug', default=False, is_flag=True,
              help='Whether or not to enable debugging features?')
def mlserver(host, port, workers, storage_root, mongo, db, collection,
             debug):
    """
    MLStorage API and web UI server.
    """
    app_factory = lambda: make_app(storage_root, mongo, db, collection, debug)
    if workers and workers > 1 and GUnicornWrapper is None:
        click.echo('GUnicorn is not installed!  Downgrade to single worker.',
                   err=True)
    if workers and workers > 1 and GUnicornWrapper is not None and not debug:
        options = {
            'bind': '%s:%s' % (host, port),
            'workers': workers,
        }
        GUnicornWrapper(app_factory, options).run()
    else:
        web.run_app(app_factory(), host=host, port=port)


if __name__ == '__main__':
    mlserver()
