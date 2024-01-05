ARG BUILDER_IMAGE
ARG BASE_IMAGE

FROM ${BUILDER_IMAGE} AS base-builder
FROM ${BASE_IMAGE}

RUN yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel make

RUN curl https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz --output Python-3.7.9.tgz \
    && tar xzf Python-3.7.9.tgz

RUN cd Python-3.7.9 \
    && ./configure --enable-optimizations --enable-shared \
    && make altinstall

# install epel repo
RUN yum install -y epel-release && yum clean all

# install s6 init system
COPY docker/base/s6-overlay-amd64.tar.gz /tmp/
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C / --exclude="./bin" && \
    tar xzf /tmp/s6-overlay-amd64.tar.gz -C /usr ./bin && \
    rm /tmp/s6-overlay-amd64.tar.gz

# tweaks needed to run a container as regular user
RUN chmod -R g=u /etc/s6 /run \
    && > /etc/s6/init/init-stage2-fixattrs.txt

# regular user without superuser rights
RUN useradd --uid 1000 --gid 0 regular \
    && chmod g=u /srv

# copy python libraries
COPY --from=base-builder --chown=regular:0 /usr/local/bin/ /usr/local/bin
COPY --from=base-builder --chown=regular:0 /usr/local/lib/ /usr/local/lib
COPY --from=base-builder --chown=regular:0 /usr/local/include/ /usr/local/include

ENV LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}" ENABLE_ARGUMENTS=0 S6_BEHAVIOUR_IF_STAGE2_FAILS=2 S6_READ_ONLY_ROOT=1

# setup venv and install service arguments using separated venv
COPY modules/service-arguments /tmp/service-arguments
RUN python3.7 -m venv /root/venv && /root/venv/bin/pip install -U pip==21.0.1 setuptools==56.0.0 wheel==0.35.1
RUN /root/venv/bin/pip install --no-cache-dir /tmp/service-arguments && \
    rm -rf /tmp/service-arguments && \
    mkdir -p /etc/arguments

# copy files
COPY docker/base/01-activate-services-initial docker/base/02-arguments-initial /etc/cont-init.d/
COPY docker/base/shutdown-container docker/base/wait-for-port /usr/local/bin/



ENTRYPOINT [ "/init" ]
