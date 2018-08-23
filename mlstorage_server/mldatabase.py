import asyncio
import json
import os

import click
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient

from mlstorage_server.mldb import MLDB
from mlstorage_server.utils import JsonEncoder


@click.group()
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
@click.pass_context
def mldatabase(ctx, mongo, db, collection):
    """Manipulate the MongoDB experiment collection."""
    if mongo is None or db is None or collection is None:
        raise ValueError('One or more of the environmental variables'
                         ' are not specified: '
                         '"MLSTORAGE_EXPERIMENT_ROOT", "MLSTORAGE_MONGO_CONN",'
                         '"MLSTORAGE_MONGO_DB" and "MLSTORAGE_MONGO_COLL".')
    client = AsyncIOMotorClient(mongo)
    mldb = MLDB(client[db][collection])
    ctx.obj = {'mldb': mldb}


@mldatabase.command('export')
@click.option('--pretty', required=False, default=False, is_flag=True,
              help='Whether or not to generate prettified JSON?')
@click.option('--use-timestamp', required=False, default=False, is_flag=True,
              help='Whether or not to use timestamp instead of ISO format '
                   'datetime text?')
@click.option('--include-deleted', required=False, default=False, is_flag=True,
              help='Whether or not to include deleted experiments?')
@click.argument('export_file', type=click.Path())
@click.pass_context
def mldatabase_export(ctx, pretty, use_timestamp, include_deleted, export_file):
    """Export database as a JSON file."""
    loop = asyncio.get_event_loop()
    docs = loop.run_until_complete(
        ctx.obj['mldb'].fetch_docs(
            sort_by=[('id', pymongo.ASCENDING)],
            include_deleted=include_deleted
        )
    )
    docs_json = json.dumps(
        docs,
        cls=JsonEncoder,
        indent=2 if pretty else None,
        separators=(', ', ': ') if pretty else (',', ':'),
        use_timestamp=use_timestamp
    )
    with click.open_file(export_file, 'w', encoding='utf-8') as f:
        f.write(docs_json)


if __name__ == '__main__':
    mldatabase()
