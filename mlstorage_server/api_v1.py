import asyncio
import functools
import json
import math
import os
import pymongo
import sys
from json import JSONDecodeError
from logging import getLogger

from aiohttp import web

from mlstorage_server.query import (build_filter_dict_from_query_string,
                                    BadQueryError)
from mlstorage_server.schema import validate_experiment_id
from mlstorage_server.mldb import MLDB
from mlstorage_server.utils import query_string_get, path_info_get, JsonEncoder

__all__ = ['ApiV1']


def add_storage_dir(store_mgr, doc):
    doc['storage_dir'] = store_mgr.get_path(doc['id'], doc)
    return doc


def query_string_get_switch(request, name, default_value=False):
    value = query_string_get(request, name, None)
    if value is not None:
        return value.lower() in ('1', 'on', 'yes', 'true')
    else:
        return default_value


async def get_doc_or_error(mldb, store_mgr, experiment_id, error_class=None):
    doc = await mldb.get(experiment_id)
    if doc is None:
        if error_class is None:
            raise RuntimeError('Experiment {!r} does not exist.'.
                               format(experiment_id))
        else:
            raise error_class()
    return add_storage_dir(store_mgr, doc)


async def get_file_store(request, mldb, store_mgr):
    id = path_info_get(request, 'id', validator=validate_experiment_id)
    doc = await get_doc_or_error(
        mldb, store_mgr, id, web.HTTPNotFound)
    store = await store_mgr.open(id, doc)
    return store


def file_entry_to_dict(entry):
    ret = {
        'name': entry.name,
        'path': entry.path,
        'mtime': entry.stat.st_mtime,
        'isdir': entry.isdir,
    }
    if not ret['isdir']:
        ret['size'] = entry.stat.st_size
    return ret


def strict_dumps(obj, dumps):
    def sub_filter(o):
        if isinstance(o, dict):
            return {k: sub_filter(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [sub_filter(v) for v in o]
        elif isinstance(o, float) and not math.isfinite(o):
            return str(o)
        else:
            return o

    return dumps(sub_filter(json.loads(dumps(obj))))


def json_api(method):
    """
    Wrap `method` as a JSON API endpoint.

    If `pretty` presents in the request GET parameters, then if it takes
    any value of ``{'1', 'on', 'true', 'yes'}``, the response JSON text
    will be human readable.

    The `method` must be an instance method, with the following signature::

        async def xxx(self, request):
            ...

    Raises:
        web.HTTPNotFound: If `method` raises :class:`KeyError`.
        web.HTTPBadRequest: If `method` raises :class:`ValueError` or
            :class:`TypeError`.
    """
    @functools.wraps(method)
    async def wrapper(self, request):
        pretty = query_string_get_switch(request, 'pretty', False)
        use_timestamp = query_string_get_switch(request, 'timestamp', False)
        strict = query_string_get_switch(request, 'strict', False)
        dumps = functools.partial(
            json.dumps,
            cls=JsonEncoder,
            indent=2 if pretty else None,
            sort_keys=pretty,
            separators=(', ', ': ') if pretty else (',', ':'),
            use_timestamp=use_timestamp
        )
        if strict:
            dumps = functools.partial(strict_dumps, dumps=dumps)
        try:
            ret = await method(self, request)
        except (KeyError, FileNotFoundError):
            raise web.HTTPNotFound()
        except (ValueError, TypeError, JSONDecodeError):
            raise web.HTTPBadRequest()
        else:
            if not isinstance(ret, (web.Response, web.StreamResponse)):
                ret = web.json_response(ret, dumps=dumps)
        return ret
    return wrapper


class ApiV1(object):
    """
    The aiohttp server handler for API v1.
    """

    def __init__(self, mldb, store_mgr):
        """
        Construct a new :class:`ApiV1`.

        Args:
            mldb (MLDB): The database instance.
            store_mgr (FileStoreManager): The file storage manager.
        """
        self._mldb = mldb
        self._store_mgr = store_mgr

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
            return '/v1' + fmt.format(
                id='{id:[A-Za-z0-9]{24}}',
                path='{path:.*}'
            )
        app.add_routes([
            # GET handlers for experiments
            web.get(url('/_query'), self.handle_query),
            web.get(url('/_get/{id}'), self.handle_get),
            web.get(url('/_tarball/{id}'), self.handle_tarball),

            # POST handlers for experiments
            web.post(url('/_heartbeat/{id}'), self.handle_heartbeat),
            web.post(url('/_delete/{id}'), self.handle_delete),
            web.post(url('/_query'), self.handle_query),
            web.post(url('/_create'), self.handle_create),
            web.post(url('/_update/{id}'), self.handle_update),
            web.post(url('/_set_finished/{id}'), self.handle_set_finished),

            # GET handlers for files
            web.get(url('/_listdir/{id}'), self.handle_listdir),
            web.get(url('/_listdir/{id}/{path}'), self.handle_listdir),
            web.get(url('/_getfile/{id}/{path}'), self.handle_getfile),
        ])

    NOT_CORE_FIELDS = ['exc_info']

    @json_api
    async def handle_query(self, request):
        """
        API endpoint for querying experiments.

        Usage:
            GET /v1/_query[?skip=0&limit=10&sort=[+/-]field&pretty=0]
            POST /v1/_query[?skip=0&limit=10&sort=[+/-]field&pretty=0] {...}

        Returns:
            List of experiment documents.
        """
        skip = query_string_get(request, 'skip', 0, int)
        limit = query_string_get(request, 'limit', 10, int)
        sort_by = query_string_get(request, 'sort', None, str)
        core_fields_only = query_string_get_switch(request, 'core', False)

        if core_fields_only:
            def filter_fields(doc):
                return {k: v for k, v in doc.items()
                        if k not in self.NOT_CORE_FIELDS}
        else:
            def filter_fields(doc):
                return doc

        if sort_by:
            order = pymongo.ASCENDING
            if sort_by.startswith('-'):
                order = pymongo.DESCENDING
                sort_by = sort_by[1:]
            elif sort_by.startswith('+'):
                sort_by = sort_by[1:]

            if not sort_by:
                raise web.HTTPBadRequest()
            sort_by = [(sort_by, order)]
        else:
            sort_by = None

        if request.method == 'GET':
            filter_ = {}
        elif request.headers.get('Content-Type', '').startswith('text/plain'):
            filter_ = await request.text()
        else:
            filter_ = await request.json()

        # build filter dict from query string
        if isinstance(filter_, str):
            try:
                filter_ = build_filter_dict_from_query_string(filter_)
                getLogger(__name__).info('Filter: %s', filter_)
            except BadQueryError:
                getLogger(__name__).info('Bad query, return empty response.')
                return []

        data = []
        try:
            async for doc in self.mldb.iter_docs(
                    filter_, skip, limit, sort_by=sort_by):
                data.append(filter_fields(add_storage_dir(self.store_mgr, doc)))
            return data
        except Exception:
            getLogger(__name__).warning(
                'Failed to load experiment.', exc_info=True)
            raise web.HTTPInternalServerError()

    @json_api
    async def handle_get(self, request):
        """
        API endpoint for getting experiment document.

        Usage:
            GET /v1/_get/[id]

        Returns:
            The experiment document.
        """
        id = path_info_get(request, 'id', validator=validate_experiment_id)
        return await get_doc_or_error(
            self.mldb, self.store_mgr, id, web.HTTPNotFound)

    async def handle_tarball(self, request):
        """
        API endpoint for downloading all files of an experiment as a tarball.

        Usage:
            GET /v1/_tarball/[id]
        """
        id = path_info_get(request, 'id', validator=validate_experiment_id)
        doc = await get_doc_or_error(self.mldb, self.store_mgr, id,
                                     error_class=web.HTTPNotFound)
        root_path = doc['storage_dir']
        if not os.path.isdir(root_path):
            raise web.HTTPNotFound()
        tar_script = os.path.join(
            os.path.split(os.path.abspath(__file__))[0], 'tar.py')
        proc = await asyncio.create_subprocess_exec(
            sys.executable, tar_script, root_path, str(id),
            stdout=asyncio.subprocess.PIPE
        )
        try:
            resp = web.StreamResponse(headers={
                'Content-Type': 'application/x-tar',
                'Content-Disposition': 'attachment; filename={}.tar'.format(id)
            })
            await resp.prepare(request)
            while True:
                buf = await proc.stdout.read(8192)
                if not buf:
                    break
                await resp.write(buf)
            await resp.write_eof()
        finally:
            if proc.returncode is None:
                proc.terminate()
                _ = proc.wait()

    @json_api
    async def handle_heartbeat(self, request):
        """
        API endpoint for experiment heartbeat.

        Usage:
            POST /v1/_heartbeat/[id]

        Returns:
            dict: An empty dict ``{}``.
        """
        id = path_info_get(request, 'id', validator=validate_experiment_id)
        await self.mldb.set_heartbeat(id)
        return {}

    @json_api
    async def handle_create(self, request):
        """
        API endpoint for creating experiment.

        Usage:
            POST /v1/_create {"name": ..., ...}

        Returns:
            The created experiment document.
        """
        doc_fields = await request.json()
        if 'name' not in doc_fields:
            raise web.HTTPBadRequest()
        id = await self.mldb.create(doc_fields['name'], doc_fields)
        return await get_doc_or_error(self.mldb, self.store_mgr, id)

    @json_api
    async def handle_update(self, request):
        """
        API endpoint for updating experiment document.

        Usage:
            POST /v1/_update/[id] {...}

        Returns:
            The updated experiment document.
        """
        id = path_info_get(request, 'id', validator=validate_experiment_id)
        doc_fields = await request.json()
        await self.mldb.update(id, doc_fields)
        return await get_doc_or_error(self.mldb, self.store_mgr, id)

    @json_api
    async def handle_set_finished(self, request):
        """
        API endpoint for setting the status of an experiment to be finished.

        Usage:
            POST /v1/_set_finished/[id] {"status": ..., ...}

        Returns:
            The updated experiment document.
        """
        id = path_info_get(request, 'id', validator=validate_experiment_id)
        doc_fields = await request.json()
        if 'status' not in doc_fields:
            raise web.HTTPBadRequest()
        await self.mldb.set_finished(id, doc_fields['status'], doc_fields)
        return await get_doc_or_error(self.mldb, self.store_mgr, id)

    @json_api
    async def handle_delete(self, request):
        """
        API endpoint for deleting an experiment.

        Usage:
            POST /v1/_delete/[id]

        Returns:
            The IDs of the deleted experiments.
        """
        async def delete_one(the_id):
            doc = await self.mldb.get(the_id)
            try:
                await self.store_mgr.delete(the_id, doc)
            except Exception:
                getLogger(__name__).debug(
                    'Failed to delete the storage for experiment %s', the_id,
                    exc_info=True
                )

        id = path_info_get(request, 'id', validator=validate_experiment_id)
        delete_ids = sorted(set(await self.mldb.mark_delete(id)))
        if not delete_ids:
            raise web.HTTPNotFound()
        await asyncio.gather(*[
            delete_one(delete_id)
            for delete_id in delete_ids
        ])
        await self.mldb.complete_deletion(delete_ids)
        return delete_ids

    @json_api
    async def handle_listdir(self, request):
        """
        API endpoint for listing a directory.

        Usage:
            GET /v1/_listdir/[id]/[path]

        Returns:
            The list of entries.
        """
        path = path_info_get(request, 'path', '')
        store = await get_file_store(request, self.mldb, self.store_mgr)
        ret = []
        for e in (await store.listdir_and_stat(path)):
            ret.append(file_entry_to_dict(e))
        return ret

    @json_api
    async def handle_getfile(self, request):
        """
        API endpoint for getting a file.

        Usage:
            GET /v1/_getfile/[id]/[path]

        Returns:
            The file content.
        """
        path = path_info_get(request, 'path', '')
        store = await get_file_store(request, self.mldb, self.store_mgr)
        if not (await store.isfile(path)):
            raise web.HTTPNotFound()
        headers = {}
        # Special treatment for console.log: force it to be recognized
        # as plain, UTF-8 text.
        if path.endswith('console.log'):
            headers['Content-Type'] = 'text/plain; charset=utf-8'
        return web.FileResponse(store.resolve_path(path), headers=headers)
