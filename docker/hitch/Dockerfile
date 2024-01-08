ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum install -y hitch && yum clean all

EXPOSE 443

ENV ENABLE_ARGUMENTS=1

RUN mkdir -p /etc/certs
COPY generate-certificate /usr/local/bin/
COPY 01-auto-generate-certificate /etc/cont-init.d/

COPY service /etc/services.d/hitch
COPY arguments /etc/arguments/hitch
