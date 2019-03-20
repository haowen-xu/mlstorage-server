import sys
import re
from collections import OrderedDict
from datetime import datetime

import bson
from bson import ObjectId

if sys.version_info[:2] < (3, 7):
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()

__all__ = [
    'EXPERIMENT_STATUSES',
    'validate_experiment_id',
    'validate_experiment_doc',
    'validate_relpath',
]

EXPERIMENT_STATUSES = ['RUNNING', 'COMPLETED', 'FAILED']


def validate_experiment_id(id):
    """
    Enforce `run_id` to be a valid experiment ID.

    Args:
        id (str or ObjectId): ID of the experiment.

    Returns:
        ObjectId: The validated experiment ID.

    Raises:
        ValueError: If the specified `run_id` is not a valid id.
    """
    try:
        if not isinstance(id, ObjectId):
            id = ObjectId(str(id))
        return id
    except bson.errors.InvalidId:
        raise ValueError('Invalid experiment ID: {!r}'.format(id))


def validate_experiment_doc(doc):
    """
    Validate the experiment `doc`.

    Args:
        doc: Object to be validated.

    Returns:
        dict: The validated experiment doc.

    Raises:
        ValueError: If the experiment doc cannot pass validation.
    """
    def str_list(value):
        return [str(t) for t in value]

    def validate_datetime(value):
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        elif isinstance(value, (int, float)):
            value = datetime.utcfromtimestamp(value)
        if not isinstance(value, datetime):
            raise ValueError('not a datetime: {!r}'.format(value))
        return value

    def choices(type_, choices):
        def inner(value):
            value = type_(value)
            if value not in choices:
                raise ValueError('only {!r} are allowed: got {!r}'.
                                 format(choices, value))
            return value
        return inner

    def validate_key(doc, key, validator, drop_None=True):
        if drop_None and doc.get(key, None) is None:
            doc.pop(key, None)
        if key in doc:
            try:
                doc[key] = validator(doc[key])
            except (ValueError, TypeError) as ex:
                raise ValueError('Attribute {!r} error: {}'.format(key, ex))

    def require_dict(o):
        if not isinstance(o, (dict, OrderedDict)):
            raise ValueError('must be a dict')
        return o

    def validate_error(error_dict):
        require_dict(error_dict)
        validate_key(error_dict, 'message', str)
        validate_key(error_dict, 'traceback', str)
        return error_dict

    def validate_env_dict(env_dict):
        require_dict(env_dict)
        env_dict = {str(k): str(v) for k, v in env_dict.items()}
        return env_dict

    def validate_exc_info(exc_info):
        require_dict(exc_info)
        validate_key(exc_info, 'hostname', str)
        validate_key(exc_info, 'pid', int)
        validate_key(exc_info, 'work_dir', str)
        validate_key(exc_info, 'env', validate_env_dict)
        return exc_info

    def validate_control_port(control_port):
        require_dict(control_port)
        validate_key(control_port, 'kill', str)
        return control_port

    if not isinstance(doc, dict):
        raise ValueError('Experiment doc must be a dict: got {!r}'.
                         format(doc))
    validate_key(doc, 'id', validate_experiment_id)
    validate_key(doc, 'parent_id', validate_experiment_id)
    validate_key(doc, 'name', str)
    validate_key(doc, 'description', str)
    validate_key(doc, 'tags', str_list)
    validate_key(doc, 'start_time', validate_datetime)
    validate_key(doc, 'stop_time', validate_datetime)
    validate_key(doc, 'heartbeat', validate_datetime)
    validate_key(doc, 'status', choices(str, EXPERIMENT_STATUSES))
    validate_key(doc, 'error', validate_error)
    validate_key(doc, 'exit_code', int)
    validate_key(doc, 'storage_dir', str)
    validate_key(doc, 'exc_info', validate_exc_info)
    validate_key(doc, 'webui', require_dict)
    validate_key(doc, 'fingerprint', str)
    validate_key(doc, 'args', str_list)
    validate_key(doc, 'config', require_dict)
    validate_key(doc, 'default_config', require_dict)
    validate_key(doc, 'result', require_dict)
    validate_key(doc, 'control_port', validate_control_port)

    return doc


_PATH_SEP_SPLITTER = re.compile(r'[/\\]')
_INVALID_PATH_CHARS = re.compile(r'[<>:"|?*]')


def validate_relpath(path):
    """
    Validate the `path`, enforcing `path` to be relative, translating "\\"
    into "/", reducing contiguous "/", eliminating "." and "..", and checking
    whether the `path` contains invalid characters.

    Args:
        path (str): The relative path to be normalized.

    Returns:
        str: The normalized relative path.

    Raises:
        ValueError: If any ".." would jump out of root, or the path contains
            invalid characters.
    """
    if _INVALID_PATH_CHARS.search(path):
        raise ValueError('Path contains invalid character(s): {!r}'.
                         format(path))
    segments = _PATH_SEP_SPLITTER.split(path)
    ret = []
    for segment in segments:
        if segment == '..':
            try:
                ret.pop()
            except IndexError:
                raise ValueError('Path jump out of root: {!r}'.format(path))
        elif segment not in ('', '.'):
            ret.append(segment)
    return '/'.join(ret)
