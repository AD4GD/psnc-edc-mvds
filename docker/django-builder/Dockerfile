# setup a separate image as builder, so that gcc and other compilation
# stuff is not included in the final image
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum install -y gcc \
    # for pycurl
    nss libcurl-devel \
    # for psycopg2
    postgresql-devel \
    && yum clean all

ENV PYCURL_SSL_LIBRARY=nss PIP_NO_CACHE_DIR=off PIP_DISABLE_PIP_VERSION_CHECK=on

RUN python3.7 -m venv /srv/venv \
    && /srv/venv/bin/pip install -U pip==21.0.1 setuptools==56.0.0 wheel==0.35.1

RUN /srv/venv/bin/pip install \
    uwsgi==2.0.15 \
    pycurl==7.44.1 \
    psycopg2==2.9.9
