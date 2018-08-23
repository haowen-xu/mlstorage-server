import json
from datetime import datetime

from aiohttp import web
from bson import ObjectId
from pytz import UTC

__all__ = [
    'query_string_get', 'path_info_get', 'JsonEncoder',
]

_NOT_SET = object()


def _XXX_get(req_dict, name, default_value, validator):
    value = req_dict.get(name, None)
    if value is not None:
        if validator is not None:
            try:
                value = validator(value)
            except (ValueError, TypeError):
                raise web.HTTPBadRequest()
        return value
    elif default_value is _NOT_SET:
        raise web.HTTPBadRequest()
    else:
        return default_value


def query_string_get(request, name, default_value=_NOT_SET, validator=None):
    """
    Get the value of GET parameter `name` from `request`.

    Args:
        request (web.Request): The request object.
        name (str): Name of the parameter.
        default_value (any): The default value to take, if the parameter
            does not present.  If not specified, will instead raise a
            :class:`web.HTTPBadRequest`.
        validator ((str) -> any): The validator for the value.
            If a :class:`ValueError` or a :class:`TypeError` is raised
            by `validator`, then a :class:`web.HTTPBadRequest` will be
            raised as the response.

    Returns:
        The value of the parameter.

    Raises:
        web.HTTPBadRequest: If the value cannot pass validation.
    """
    return _XXX_get(request.rel_url.query, name, default_value, validator)


def path_info_get(request, name, default_value=_NOT_SET, validator=None):
    """
    Get the value of matched path information `name` from `request`.

    Args:
        request (web.Request): The request object.
        name (str): Name of the path information.
        default_value (any): The default value to take, if the path
            information does not present.  If not specified, will instead
            raise a :class:`KeyError`.
        validator ((str) -> any): The validator for the value.
            If a :class:`ValueError` or a :class:`TypeError` is raised
            by `validator`, then a :class:`web.HTTPBadRequest` will be
            raised as the response.

    Returns:
        The value of the path information.

    Raises:
        web.HTTPBadRequest: If the value cannot pass validation.
    """
    return _XXX_get(request.match_info, name, default_value, validator)


class JsonEncoder(json.JSONEncoder):
    """
    Extended JSON encoder for serializing experiment documents.
    """

    def __init__(self, use_timestamp=False, **kwargs):
        super(JsonEncoder, self).__init__(**kwargs)
        self.use_timestamp = use_timestamp

    def _default_object_handler(self, o):
        if isinstance(o, datetime):
            if self.use_timestamp:
                # we only use UTC datetime through out this project
                yield o.replace(tzinfo=UTC).timestamp()
            else:
                yield o.isoformat()
        elif isinstance(o, ObjectId):
            yield str(o)
        elif isinstance(o, bytes):
            try:
                yield o.decode('utf-8')
            except UnicodeDecodeError:
                yield repr(o)

    #: List of object serialization handlers
    OBJECT_HANDLERS = [_default_object_handler]

    def default(self, o):
        for handler in self.OBJECT_HANDLERS:
            for obj in handler(self, o):
                return obj
        return super(JsonEncoder, self).default(o)

    def encode(self, o):
        return super(JsonEncoder, self).encode(o)
