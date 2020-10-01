Guide for testing MapCache integration

Docker-compose file defines 4 services:

1. Mapcache, in front of Geoserver container and as part of an Apache2 (defined as module)
2. Memcached, used by MapCache as a memory cache level
3. Apache, which serves a couple of htmls/php files that allows to check/validate behavior on Mapcache+Memcached request. Including an OpenLayer client pointing to Mapcache.
4. Geoserver, a simple geoserver container with some information.

Steps

1. Run ./startup.sh script at mapcache/ folder level
2. Open browser and you can try:
    1. http://localhost:8082/ol/  - to get access to a OL sample that points to Mapcache with layers selector Tiger-NY and Tasmania
    2. http://localhost:8082/memcached-status.php   - you can check Memcached status (if Mapcache saved information there then you will notice it)
    3. http://localhost:8080/geoserver/web  -  you can access geoserver (admin/geoserver) with usual data_dir (but exposed in local folder so it's easy to change/look at it)
    4. http://localhost:8081/mapcache  - you will be challenging mapcache (but depending on parameters you will get or not info/tiles)
3. Run ./shutdown.sh whenever you want to finish created containers

Notes:
1. Since mapcache requires to know the container name/ip of geoserver container (internal network) you can use docker hostnames or assigned IPs (hostnames are used in docker-compose file)
2. In order to get your Docker HOSTIP, execute in console the next command   "ip a" and look for the docker0 network adapter definition. Your IP will be displayed there. Reference: https://nickjanetakis.com/blog/docker-tip-65-get-your-docker-hosts-ip-address-from-in-a-container
3. Mapcache docker image used is the one created by Camp2Camp (it can be customized creating our own Dockerfile)
4. Geoserver docker image comes from oscarfonts/geoserver dockerhub repositiory, since I could not find one available in GeosolutionsIt repo.
5. File called eumetsat.html used in combination with commented lines in eumetsat-ng-config.xml (lines 40 and 122) file (pointing to view.eumesat.int geoservers) were defined as part of testing, but unfortunatelly it's not possible to use those public servers since Mapcache is showing an error while trying to get tiles from server using CURL, showing a message related to SSL (and makes sense since EUMETSAT servers are using HTTPS)
6 File eumetsat-config.xml is the original file provided by customer.
