FROM debian:buster

RUN apt-get update
RUN apt-get install cron -y
RUN touch /var/log/cron.log
# cleancache: for each layer, "find" folders and "rm" <layer>
COPY cleancache.sh /home
# cleancache2: group layers by rettime and "rm" <list folders>
COPY cleancache2.sh /home
COPY layers.properties /home

COPY start-cron /usr/sbin

CMD ["start-cron"]
