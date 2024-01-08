ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY varnish60lts.repo /etc/yum.repos.d/
RUN yum install -y varnish && yum clean all

ENV ENABLE_ARGUMENTS=1

EXPOSE 80

COPY varnishreargument /usr/sbin/

COPY services /etc/services.d/
COPY arguments /etc/arguments/varnish
COPY init/* /etc/cont-init.d/

# needed to run a container as regular user
RUN chmod g=u /var/lib/varnish

# switch to regular user
USER 1000
