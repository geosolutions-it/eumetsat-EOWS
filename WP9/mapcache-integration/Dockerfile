FROM camptocamp/mapcache:1.8

ENV MAPCACHE_VERSION=branch-1-8

RUN apt-get update
RUN LC_ALL=C DEBIAN_FRONTEND=noninteractive apt-get install -qqy libfcgi-dev libpq-dev postgresql-server-dev-all && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/partial/* /tmp/* /var/tmp/*

RUN mkdir /build

RUN cd /build && git clone https://github.com/mapserver/mapcache.git && \
    cd /build/mapcache && git checkout ${MAPCACHE_VERSION} && \
    mkdir /build/mapcache/build && cd /build/mapcache/build && \
    cmake \
      -DCMAKE_BUILD_TYPE=Release -DWITH_POSTGRESQL=1 -DWITH_MEMCACHE=1 \
      .. && \
    make && make install && ldconfig && \
    rm -Rf /build/mapcache