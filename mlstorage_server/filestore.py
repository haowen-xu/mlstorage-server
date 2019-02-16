import os
import shutil
import stat
from asyncio import AbstractEventLoop
from concurrent.futures import Executor, ThreadPoolExecutor

from aiofile import AIOFile

from mlstorage_server.schema import validate_experiment_id, validate_relpath

__all__ = [
    'FileStoreManager', 'FileEntry', 'FileStore'
]


class FileStoreManager(object):
    """Manage the directories for storing experiment generated files."""

    def __init__(self, storage_root, loop, executor=None,
                 default_thread_workers=16):
        """
        Construct a new :class:`FileStoreManager`.

        Args:
            storage_root (str): The root directory for the experiment storage.
            loop (AbstractEventLoop): The asyncio event loop.
            executor (Executor): The executor for performing file-system
                related operations (e.g., "os.listdir").  If not specified,
                will create a separated :class:`ThreadPoolExecutor` with
                `default_thread_workers` number of workers.
            default_thread_workers (int): Default number of threads for
                creating the default `executor`. (default 16)
        """
        if executor is None:
            executor = ThreadPoolExecutor(max_workers=default_thread_workers)
        self._storage_root = os.path.abspath(storage_root)
        self._loop = loop
        self._executor = executor

    @property
    def storage_root(self):
        """Get the root directory for the experiment storages."""
        return self._storage_root

    @property
    def loop(self):
        """Get the asyncio event loop."""
        return self._loop

    @property
    def executor(self):
        """Get the executor for performing file-system related operations."""
        return self._executor

    def get_path(self, experiment_id, experiment_doc=None):
        """
        Get the path of the storage directory of the specified experiment.

        Args:
            experiment_id (str or ObjectId): The ID of the experiment.
            experiment_doc (None or dict): The experiment document from
                MongoDB.  If specified, will use its "storage_dir" as
                the directory to open, instead of the default location.
                (default :obj:`None`)

        Returns:
            str: The path of the experiment storage directory.
        """
        experiment_id = str(validate_experiment_id(experiment_id))
        storage_dir = (experiment_doc or None) and \
            experiment_doc.get('storage_dir', None)
        if storage_dir is None:
            r_id = ''.join(reversed(experiment_id))
            storage_dir = '{}/{}/{}'.format(r_id[:2], r_id[2: 4], r_id[4:])
            storage_dir = os.path.abspath(
                os.path.join(self.storage_root, storage_dir))
        return storage_dir

    async def open(self, experiment_id, experiment_doc=None):
        """
        Open a :class:`FileStore` for the specified experiment.

        Args:
            experiment_id (str or ObjectId): The ID of the experiment.
            experiment_doc (None or dict): The experiment document from
                MongoDB.  If specified, will use its "storage_dir" as
                the directory to open, instead of the default location.
                (default :obj:`None`)

        Returns:
            FileStore: The opened :class:`FileStore` instance.
        """
        storage_dir = self.get_path(experiment_id, experiment_doc)
        return FileStore(self, storage_dir)

    async def delete(self, experiment_id, experiment_doc=None):
        """
        Delete the storage directory of the specified experiment.

        Args:
            experiment_id (str or ObjectId): The ID of the experiment.
            experiment_doc (None or dict): The experiment document from
                MongoDB.  If specified, will use its "storage_dir" as
                the directory to open, instead of the default location.
                (default :obj:`None`)
        """
        def _sync_delete():
            storage_dir = self.get_path(experiment_id, experiment_doc)
            if os.path.exists(storage_dir):
                shutil.rmtree(storage_dir)
        await self.loop.run_in_executor(self.executor, _sync_delete)


class FileEntry(object):
    """
    Class to wrap the name and stat result of a file-system entry.
    """

    __slots__ = ('name', 'path', 'stat')

    def __init__(self, name, path, stat):
        """
        Construct a new :class:`FileEntry`.

        Args:
            name (str): Name of the file-system entry.
            path (str): Relative path of the file-system entry under
                its parent :class:`FileStore`.
            stat (os.stat_result): Stat result of the file-system entry.
        """
        self.name = name
        self.path = path
        self.stat = stat

    def __repr__(self):
        return 'FileEntry({!r})'.format(self.path)

    @property
    def mode(self):
        return stat.S_IMODE(self.stat.st_mode)

    @property
    def isdir(self):
        return stat.S_ISDIR(self.stat.st_mode)


class FileStore(object):
    """
    Storing the generated files of an experiment.

    The layout of the storage directory for an experiment is assumed to be::

        .
        |-- console.log     (the captured stdout and stderr of the program)
        `-- ...             (the other files generated by the program)
    """

    def __init__(self, manager, storage_dir):
        """
        Construct a new :class:`FileStore`.

        Args:
            manager (FileStoreManager): Get the :class:`FileStoreManager`.
            storage_dir (str): The root directory of this class:`FileStore`.
        """
        self._manager = manager
        self._storage_dir = storage_dir

    def __repr__(self):
        return 'FileStore({!r})'.format(self.storage_dir)

    @property
    def manager(self):
        """Get the :class:`FileStoreManager`."""
        return self._manager

    @property
    def storage_dir(self):
        """Get the root directory of this :class:`FileStore`."""
        return self._storage_dir

    def resolve_path(self, path):
        """
        Resolve a relative path within this :class:`FileStore` to absolute path.

        Args:
            path (str): The relative path within this :class:`FileStore`.

        Returns:
            str: The resolved absolute path.

        Raises:
            ValueError: If `path` jumps out of :attr:`storage_dir`.
        """
        path = validate_relpath(path)
        return self.storage_dir + os.sep + path

    async def listdir(self, path):
        """
        List the entries under `path`.

        Args:
            path (str): The relative path within this :class:`FileStore`.

        Returns:
            list[str]: The names of the entries.
        """
        def _sync_list():
            ret = []
            for name in os.listdir(abspath):
                ret.append(name)
            return ret
        abspath = self.resolve_path(path)
        return await self.manager.loop.run_in_executor(
            self.manager.executor, _sync_list)

    async def listdir_and_stat(self, path):
        """
        List the entries under `path`, and get their stats.

        Args:
            path (str): The relative path within this :class:`FileStore`.

        Returns:
            list[FileEntry]: The entries under `path`.
        """
        def _sync_list_and_stat():
            ret = []
            for name in os.listdir(abspath):
                f_path = name if not path else path + '/' + name
                f_abspath = abspath + os.sep + name
                try:
                    f_stat = os.stat(f_abspath, follow_symlinks=True)
                except FileNotFoundError:
                    f_stat = os.stat(f_abspath, follow_symlinks=False)
                ret.append(FileEntry(name, f_path, f_stat))
            return ret
        path = validate_relpath(path)
        abspath = (self.storage_dir if not path
                   else self.storage_dir + os.sep + path)
        return await self.manager.loop.run_in_executor(
            self.manager.executor, _sync_list_and_stat)

    async def compute_fs_size(self, path):
        """
        Sum up the file system size of `path`.

        Args:
            path (str): The relative path within this :class:`FileStore`.

        Returns:
            int: The size of `path` in bytes.
        """
        def _sync_compute_fs_size(p):
            st = os.stat(p, follow_symlinks=False)
            if stat.S_ISDIR(st.st_mode):
                return st.st_size + sum(
                    _sync_compute_fs_size(os.path.join(p, name))
                    for name in os.listdir(p)
                )
            else:
                return st.st_size
        path = validate_relpath(path)
        abspath = (self.storage_dir if not path
                   else self.storage_dir + os.sep + path)
        return await self.manager.loop.run_in_executor(
            self.manager.executor, lambda: _sync_compute_fs_size(abspath))

    async def isfile(self, path):
        """
        Check whether or not `path` is a file.

        Args:
            path (str): The relative path within this :class:`FileStore`.

        Returns:
            bool: Whether or not `path` exists and is a file.
        """
        def _check_stat():
            abspath = self.resolve_path(path)
            try:
                s = os.stat(abspath, follow_symlinks=True)
                return stat.S_ISREG(s.st_mode)
            except FileNotFoundError:
                return False
        return await self.manager.loop.run_in_executor(
            self.manager.executor, _check_stat)

    async def isdir(self, path):
        """
        Check whether or not `path` is a directory.

        Args:
            path (str): The relative path within this :class:`FileStore`.

        Returns:
            bool: Whether or not `path` exists and is a directory.
        """
        def _check_stat():
            abspath = self.resolve_path(path)
            try:
                return stat.S_ISDIR(os.stat(abspath, follow_symlinks=True))
            except FileNotFoundError:
                return False
        return await self.manager.loop.run_in_executor(
            self.manager.executor, _check_stat)

    async def exists(self, path):
        """
        Check whether or not `path` exists.

        Args:
            path (str): The relative path within this :class:`FileStore`.

        Returns:
            bool: Whether or not `path` exists.
        """

        def _check_exists():
            abspath = self.resolve_path(path)
            return os.path.exists(abspath)
        return await self.manager.loop.run_in_executor(
            self.manager.executor, _check_exists)

    def open_file(self, path, mode):
        """
        Open the `path` file.

        Args:
            path (str): The relative path within this :class:`FileStore`.
            mode (str): Mode for opening the file.

        Returns:
            AIOFile: The asynchronous file object.
        """
        abspath = self.resolve_path(path)
        return AIOFile(abspath, mode, loop=self.manager.loop)

    async def ensure_parent_exists(self, path):
        """
        Ensure the parent directory for `path` exists.

        Args:
            path (str): The relative path within this :class:`FileStore`.
        """
        def _check_parent_exists():
            parent_dir = os.path.split(abspath)[0]
            os.makedirs(parent_dir, exist_ok=True)
        abspath = self.resolve_path(path)
        await self.manager.loop.run_in_executor(
            self.manager.executor, _check_parent_exists)
