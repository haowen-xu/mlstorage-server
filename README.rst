MLStorage Server
================

The server side for MLStorage.
MLStorage is an application for running machine learning experiments
and storing results as well as generated files, all accessible with a dashboard.

The client side: `MLStorage Client <http://github.com/haowen-xu/mlstorage-client>`_.

Pre-requisites
--------------

*   Python: >= 3.5.3, or Docker (for server)
*   MongoDB: for storing experiment documents.
*   A shared network file system: currently the programs must run on a host
    where the server's storage directory is accessible in the same location,
    so as to store its generated files.

Install via Pip
---------------

.. code-block:: bash

    pip install git+https://github.com/haowen-xu/mlstorage-server.git

    mlserver -h <ip> -p 8080 -w 4 -R /path/to/storage-dir \
        -M mongodb://user:password@localhost/admin -D user -C experiments


The above command starts an MLStorage server at ``http://<ip>:8080``, with
``4`` workers to serve requests.  The MongoDB connection string is set to
``mongodb://user:password@localhost/admin``, with ``user`` and ``password`` as
the login credential.  The ``user`` database and the ``experiments`` collection
is chosen to store the experiment documents.  The root directory of experiment
storage directory (i.e., working directory) is set to ``/path/to/storage-dir``.

Install from Docker
-------------------

.. code-block:: bash

    git clone git+https://github.com/haowen-xu/mlstorage-server.git

    docker build \
        --build-arg UBUNTU_MIRROR=archive.ubuntu.com \
        --build-arg TZ=UTC \
        -t mlstorage_server \
        .

    docker run \
        --name mlserver -d \
        -p 8080 \
        -e MLSTORAGE_SERVER_HOST=0.0.0.0 \
        -e MLSTORAGE_SERVER_PORT=8080 \
        -e MLSTORAGE_SERVER_WORKERS=4 \
        -e MLSTORAGE_EXPERIMENT_ROOT=/path/to/experiments \
        -v /path/to/experiments:/path/to/experiments \
        -e MLSTORAGE_MONGO_CONN=mongodb://localhost:27017 \
        -e MLSTORAGE_MONGO_DB=test \
        -e MLSTORAGE_MONGO_COLL=experiments \
        mlstorage_server
