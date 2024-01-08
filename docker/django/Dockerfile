ARG BUILDER_IMAGE
ARG BASE_IMAGE

FROM ${BUILDER_IMAGE} AS builder
FROM ${BASE_IMAGE}

# postgresql package (psql program) is required if you want to use 'manage dbshell'
RUN yum install -y \
	libcurl \
	postgresql \
    diffutils \
    gcc-c++ \
    libffi-devel \
    nano \
    sshpass \
    openssh-server \
    openssh-clients \
    && yum clean all

# copy configuration files and scripts
COPY docker/django/arguments /etc/arguments/
COPY docker/django/services /etc/available.d/
COPY docker/django/init/* /etc/cont-init.d/
COPY docker/django/mime.types /etc/mime.types
COPY docker/django/scripts/* /usr/local/bin/

# copy virtual env created in builder image
COPY --from=builder --chown=regular:0 /srv/venv /srv/venv

# setup auto pip
COPY --chown=regular:0 reqs /srv/reqs
RUN auto-pip srv-venv /srv reqs/external.txt

COPY --chown=regular:0 audits /srv/audits

# switch to regular user
USER 1000

# activate virtual env for interactive shell
RUN echo "source /srv/venv/bin/activate" >> ~/.bashrc

RUN mkdir -p /srv/logs /srv/src /srv/pkgs

ENV PATH="/srv/venv/bin:${PATH}" LANG="en_US.utf-8" ENABLE_ARGUMENTS=1 \
    PYCURL_SSL_LIBRARY="nss" PIP_NO_CACHE_DIR="off" PIP_DISABLE_PIP_VERSION_CHECK="on"

WORKDIR /srv/src

# install external requirements
RUN auto-pip-srv-venv

# copy and install local requirements
COPY --chown=regular:0 modules/service-arguments /srv/pkgs/service-arguments
COPY --chown=regular:0 modules/pytest-http /srv/pkgs/pytest-http

RUN /srv/venv/bin/pip install -r /srv/reqs/internal.txt

# copy and compile source files
COPY --chown=regular:0 src /srv/src
COPY --chown=regular:0 setup.cfg /srv/setup.cfg


RUN /srv/venv/bin/python -m compileall /srv/src

#RUN manage collectstatic --traceback --noinput
