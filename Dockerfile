FROM ubuntu:18.04

MAINTAINER Haowen Xu <haowen.xu@outlook.com>

ARG UBUNTU_MIRROR=archive.ubuntu.com
ARG PIP_OPTS=""
ARG TZ=UTC
ARG CACHEBUST=1

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV SHELL=/bin/bash
ENV PIP_DEFAULT_TIMEOUT=120

ENV MLSTORAGE_SERVER_HOST=0.0.0.0
ENV MLSTORAGE_SERVER_PORT=8080
ENV MLSTORAGE_SERVER_WORKERS=4
ENV MLSTORAGE_EXPERIMENT_ROOT=/experiments
ENV MLSTORAGE_MONGO_CONN=mongodb://localhost:27017
ENV MLSTORAGE_MONGO_DB=test
ENV MLSTORAGE_MONGO_COLL=experiments

# do configuration and update packages
RUN echo ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    chsh -s /bin/bash && \
    sed -i "s/archive.ubuntu.com/${UBUNTU_MIRROR}/g" /etc/apt/sources.list && \
    DEBIAN_FRONTEND=noninteractive apt-get -y update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        locales \
        language-pack-en \
        tzdata \
        python3 python3-dev python3-pip \
    && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Dependencies
RUN python --version && \
    python -m pip --version && \
    python -m pip install ${PIP_OPTS} --no-cache-dir --upgrade setuptools pip && \
    python -m pip install ${PIP_OPTS} --no-cache-dir gunicorn

# Advanced Dependencies
# RUN python -m pip install ${PIP_OPTS} --no-cache-dir tensorflow==1.8.0

# Deploy MLStorage
COPY docker/mlboard.sh /mlboard.sh
COPY . /tmp/mlstorage
RUN chmod +x /mlboard.sh && \
    cd /tmp/mlstorage && \
    python -m pip install ${PIP_OPTS} --no-cache-dir --upgrade . && \
    rm -rf /tmp/mlstorage && \
    rm -rf /root/.cache

EXPOSE 8080
CMD ["/mlboard.sh"]
