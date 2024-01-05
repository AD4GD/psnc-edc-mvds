ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum install -y gcc openssl-devel bzip2-devel libffi-devel zlib-devel make

RUN curl https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz --output Python-3.7.9.tgz \
    && tar xzf Python-3.7.9.tgz

RUN cd Python-3.7.9 \
    && ./configure --enable-optimizations --enable-shared \
    && make altinstall
